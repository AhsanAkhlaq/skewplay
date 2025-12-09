import os
import shutil
import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from utils import get_user_storage_usage

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vue Frontend
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
SAMPLES_DIR = "storage/samples"
STORAGE_DIR = "storage/users" # User data root

os.makedirs(SAMPLES_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

# Mount static files to serve CSVs
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")
# Mount the entire storage directory.
# URL format: /storage/{userId}/datasets/{filename}
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# Configuration for Sample Datasets
# Format: "filename.csv": "TargetColumnName"
SAMPLE_TARGETS = {
    "dummy_sample.csv": "target",
    "credit_card.csv": "Class",
    # Add your sample files here
}

def analyze_csv(file_path: str, user_target_col: Optional[str] = None) -> Dict[str, Any]:
    try:
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        # 1. Target Column Detection
        target_col = None
        if user_target_col and user_target_col in df.columns:
            target_col = user_target_col
        else:
            # Fallback heuristic: last column
            target_col = df.columns[-1]
            
        # 2. Anomaly Detection (Null Values)
        anomalies = []
        if df.isnull().values.any():
            null_count = df.isnull().sum().sum()
            anomalies.append(f"Missing Values ({null_count})")
            
        # 3. Type & Imbalance Analysis
        # Ensure target col exists (heuristic fallback might fail if empty df)
        if target_col and target_col in df.columns:
            if df[target_col].nunique() < 20: # Assume classification if < 20 unique values
                value_counts = df[target_col].value_counts(normalize=True).to_dict()
                imbalance_ratios = {str(k): float(v) for k, v in value_counts.items()}
                
                type_ = "binary" if len(value_counts) == 2 else "multiclass"
            else:
                imbalance_ratios = {}
                type_ = "regression"
        else:
            imbalance_ratios = {}
            type_ = "unknown"

        return {
            "rowCount": row_count,
            "type": type_,
            "imbalanceRatios": imbalance_ratios,
            "anomalies": anomalies,
            "sizeBytes": os.path.getsize(file_path),
            "targetCol": target_col
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            "rowCount": 0,
            "type": "unknown",
            "imbalanceRatios": {},
            "anomalies": ["Analysis Failed"],
            "sizeBytes": 0
        }

@app.get("/samples")
async def get_samples():
    samples = []
    # Ensure directory exists just in case
    if not os.path.exists(SAMPLES_DIR):
        return []

    for filename in os.listdir(SAMPLES_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(SAMPLES_DIR, filename)
            
            # Use configured target if available, otherwise None (triggers heuristic)
            configured_target = SAMPLE_TARGETS.get(filename)
            analysis = analyze_csv(file_path, user_target_col=configured_target)
            
            samples.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, filename)), # Consistent ID based on filename
                "userId": "system",
                "fileName": filename,
                "storagePath": f"http://localhost:8000/samples/{filename}",
                "isPublic": True,
                "isSample": True,
                "createdAt": {"seconds": os.path.getctime(file_path), "nanoseconds": 0},
                **analysis
            })
    return samples

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    userId: str = Form(...),
    targetCol: Optional[str] = Form(None)
):
    try:
        # 1. Create User Directory Structure: storage/{userId}/datasets/
        user_datasets_dir = os.path.join(STORAGE_DIR, userId, "datasets")
        os.makedirs(user_datasets_dir, exist_ok=True)

        # 2. Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(user_datasets_dir, filename)
        
        # 3. Save File using shutil
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 4. Analyze with User's Target Column preference
        analysis = analyze_csv(file_path, user_target_col=targetCol)
        
        # 5. Return Metadata
        # URL construction: http://localhost:8000/storage/{userId}/datasets/{filename}
        storage_path = f"http://localhost:8000/storage/{userId}/datasets/{filename}"

        return {
            "fileName": file.filename, 
            "storagePath": storage_path,
            **analysis
        }
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")    

@app.post("/run")
async def run_experiment(
    userId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(...),
    config: str = Form(...)  # JSON string
):
    import json
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    try:
        # Parse Config
        # Config structure matches PipelineConfig interface
        cfg = json.loads(config)
        
        # 1. Load Data
        # Check if sample
        if fileName in SAMPLE_TARGETS:
             file_path = os.path.join(SAMPLES_DIR, fileName)
        else:
             file_path = os.path.join(STORAGE_DIR, userId, "datasets", fileName)
        
        if not os.path.exists(file_path):
             raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        df = pd.read_csv(file_path)
        
        # 2. Preprocessing
        X = df.drop(columns=[targetCol])
        y = df[targetCol]
        
        # Numerical/Categorical Split
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X.select_dtypes(include=['object']).columns

        # Transformers
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler() if cfg['preprocessing']['scaling'] == 'Standard' else 
                       MinMaxScaler() if cfg['preprocessing']['scaling'] == 'MinMax' else None)
        ])
        
        categorical_transformer = Pipeline(steps=[
             ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
             ('encoder', OneHotEncoder(handle_unknown='ignore') if cfg['preprocessing']['encoding'] == 'OneHot' else 
                         None) # Label encoding usually for target, or Ordinal for features. Simplified here.
        ])

        # Filter out None steps
        if cfg['preprocessing']['scaling'] == 'None':
             numeric_transformer.steps.pop(-1) # remove scaler
        if cfg['preprocessing']['encoding'] == 'None':
             categorical_transformer.steps.pop(-1)

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])

        # 3. Model Selection
        algo = cfg['model']['algorithm']
        params = cfg['model']['hyperparameters']
        
        if algo == 'RandomForest':
            model = RandomForestClassifier(
                n_estimators=int(params.get('n_estimators', 100)),
                max_depth=int(params.get('max_depth', 10)) if params.get('max_depth') else None
            )
        elif algo == 'XGBoost':
            model = GradientBoostingClassifier( # Using sklearn GBDT as placeholder for XGB interaction
                n_estimators=int(params.get('n_estimators', 100))
            )
        elif algo == 'LogisticRegression':
            model = LogisticRegression(C=float(params.get('C', 1.0)))
        elif algo == 'SVM':
            model = SVC(C=float(params.get('C', 1.0)), kernel=params.get('kernel', 'rbf'))
        else:
             model = RandomForestClassifier()

        # 4. Pipeline Execution
        clf = Pipeline(steps=[('preprocessor', preprocessor),
                              # ('sampling', ... ) # Imbalance handling would go here (requires imblearn pipeline)
                              ('classifier', model)])

        # Split
        test_size = float(cfg['preprocessing'].get('splitRatio', 0.2))
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        clf.fit(X_train, y_train)
        
        # 5. Evaluation
        y_pred = clf.predict(X_test)
        
        # Metrics
        # Simple heuristic: if regression, these will fail. Assume classification for now as per "imbalance" context.
        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "f1Score": round(f1_score(y_test, y_pred, average='weighted'), 4),
            "precision": round(precision_score(y_test, y_pred, average='weighted'), 4),
            "recall": round(recall_score(y_test, y_pred, average='weighted'), 4),
            "executionTimeSeconds": 0.5 # Mock time
        }
        
        # 6. Artifacts
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        artifacts_dir = os.path.join(STORAGE_DIR, userId, "artifacts", timestamp)
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Save Model
        model_filename = "model.joblib"
        joblib.dump(clf, os.path.join(artifacts_dir, model_filename))
        
        # Save Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        cm_filename = "confusion_matrix.png"
        plt.savefig(os.path.join(artifacts_dir, cm_filename))
        plt.close()

        # URLs
        artifacts = {
             "modelPath": f"http://localhost:8000/storage/{userId}/artifacts/{timestamp}/{model_filename}",
             "confusionMatrixUrl": f"http://localhost:8000/storage/{userId}/artifacts/{timestamp}/{cm_filename}",
        }

        return {
            "status": "Completed",
            "results": metrics,
            "artifacts": artifacts
        }

    except Exception as e:
        print(f"Run Error: {e}")
        # Return error structure or raise
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reanalyze")
async def reanalyze_dataset(
    userId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(...)
):
    try:
        # 1. Locate file
        # Note: fileName here is likely the TIMESTAMPED filename stored in Firestore (e.g. 2025..._data.csv)
        # However, frontend's "fileName" might be the DISPLAY name. 
        # We need the ACTUAL filename on disk. 
        # In current datasets.ts, we store: "fileName": analysisData.fileName (which is original name usually)
        # wait, analyze_csv returns "fileName": file.filename (original).
        # We need the STORAGE path or the generated filename. 
        # The frontend has `storagePath`: "http://.../storage/{uid}/datasets/{GENERATED_FILENAME}"
        # So we can extract the filename from the storagePath or pass storagePath and parse it.
        # Let's assume frontend extracts the filename from storagePath or we accept storagePath.
        
        # Simpler: Accept fileName as the ON-DISK filename.
        # But frontend might not have it easily if it only has display name. 
        # Actually, let's look at what we return in /upload: we return "fileName": file.filename (original).
        # But the file on disk is f"{timestamp}_{file.filename}".
        # AND we return "storagePath". 
        # The frontend should probably pass the filename derived from storagePath. 
        
        # Strategy: Pass `userId` and `actualFileName` (extracted from storagePath on FE).
        
        user_datasets_dir = os.path.join(STORAGE_DIR, userId, "datasets")
        file_path = os.path.join(user_datasets_dir, fileName)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # 2. Re-Analyze
        analysis = analyze_csv(file_path, user_target_col=targetCol)
        
        return analysis

    except Exception as e:
        print(f"Reanalyze failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usage/{user_id}")
async def get_usage(user_id: str):
    try:
        usage = get_user_storage_usage(user_id)
        return {"storageUsedBytes": usage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
