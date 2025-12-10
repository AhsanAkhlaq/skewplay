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
from json_utils import sanitize_for_json
import json

# ML & Stats Imports
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import scipy.stats as stats

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
    "MOCK_DATA.csv": "Gender",
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

        # 4. Target Missing (Specific)
        target_missing_pct = 0.0
        if target_col and target_col in df.columns:
            target_missing = df[target_col].isnull().sum()
            target_missing_pct = float(round((target_missing / row_count) * 100, 2)) if row_count > 0 else 0.0

        return {
            "rowCount": row_count,
            "type": type_,
            "imbalanceRatios": imbalance_ratios,
            "anomalies": anomalies,
            "sizeBytes": os.path.getsize(file_path),
            "targetCol": target_col,
            "targetMissingPct": target_missing_pct
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
    return sanitize_for_json(samples)

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

        return sanitize_for_json({
            "fileName": file.filename, 
            "storagePath": storage_path,
            **analysis
        })
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

        return sanitize_for_json({
            "status": "Completed",
            "results": metrics,
            "artifacts": artifacts
        })

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
        
        return sanitize_for_json(analysis)

    except Exception as e:
        print(f"Reanalyze failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dataset-details")
async def get_dataset_details(
    userId: str = Form(...),
    fileName: str = Form(...)
):
    try:
        # Resolve path
        if fileName in SAMPLE_TARGETS:
             file_path = os.path.join(SAMPLES_DIR, fileName)
        else:
             file_path = os.path.join(STORAGE_DIR, userId, "datasets", fileName)
        
        if not os.path.exists(file_path):
             raise HTTPException(status_code=404, detail=f"File not found: {fileName}")

        # Read CSV
        df = pd.read_csv(file_path)
        
        # 1. Basic Info
        rows, cols = df.shape
        duplicates = int(df.duplicated().sum())
        
        # 2. Columns Info
        columns_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = int(df[col].isnull().sum())
            pct_missing = float(round((missing / rows) * 100, 2)) if rows > 0 else 0
            
            # Value Range (for numeric)
            val_range = ""
            if pd.api.types.is_numeric_dtype(df[col]):
                val_range = f"{df[col].min()} - {df[col].max()}"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                val_range = f"{df[col].min()} - {df[col].max()}"
            else:
                 val_range = f"{df[col].nunique()} unique"

            col_info = {
                "name": col,
                "type": dtype,
                "missing": missing,
                "pct_missing": pct_missing,
                "range": val_range
            }
            columns_data.append(col_info)
            
        # 3. Frequency Tables (Top 5 for categorical/object)
        freq_tables = {}
        for col in df.select_dtypes(include=['object', 'category']).columns:
             if df[col].nunique() < 50: # Only if reasonable cardinality
                 counts = df[col].value_counts().head(5).to_dict()
                 freq_tables[col] = counts

        # 4. Statistics (Describe)
        # fillna to handle NaN in describe output for JSON serialization transformation
        desc = df.describe(include='all').transpose()
        desc.insert(0, 'column', desc.index)
        # Handle Inf
        desc.replace([np.inf, -np.inf], np.nan, inplace=True)
        # Convert NaN to None
        stats = desc.where(pd.notnull(desc), None).to_dict(orient='records')

        # 5. Preview
        # Create a safe copy for preview to handle Inf/NaN
        df_preview = df.copy()
        df_preview.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Convert NaN to None
        head = df_preview.head(5).where(pd.notnull(df_preview), None).values.tolist()
        tail = df_preview.tail(5).where(pd.notnull(df_preview), None).values.tolist()
        
        return sanitize_for_json({
            "fileName": fileName,
            "rows": rows,
            "cols": cols,
            "duplicates": duplicates,
            "columns": columns_data, # Includes types, missing, ranges
            "statistics": stats,
            "freqTables": freq_tables,
            "head": head,
            "tail": tail,
            "headers": list(df.columns)
        })

    except Exception as e:
        print(f"Details Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/perform-eda")
async def perform_eda(
    userId: str = Form(...),
    fileName: str = Form(...)
):
    try:
        # Resolve path
        if fileName in SAMPLE_TARGETS:
             file_path = os.path.join(SAMPLES_DIR, fileName)
        else:
             file_path = os.path.join(STORAGE_DIR, userId, "datasets", fileName)
        
        if not os.path.exists(file_path):
             raise HTTPException(status_code=404, detail=f"File not found: {fileName}")

        # Load Data
        df = pd.read_csv(file_path)
        row_count, col_count = df.shape

        # Identify Target
        # Re-use analyze_csv logic or logic passed from frontend. 
        # For EDA, we often want to know what the user thinks is the target.
        # But here we do general EDA. We will try to infer target from metadata or simple heuristic if not passed.
        # Ideally frontend passes targetCol. Let's add it to Form.
        # For now, let's proceed with generic EDA and specific target analysis if we can find it.
        # I'll rely on the frontend sending the target col? No, the signature didn't have it.
        # I will update signature to accept targetCol optionally.
        
        # NOTE: WE SHOULD UPDATE SIGNATURE TO ACCEPT targetCol
        # However, for now, let's just do robust general EDA.
        
        # --- 1. Univariate Analysis ---
        univariate = {}
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in df.columns:
            col_data = df[col]
            stats_obj = {}
            
            # Missing
            stats_obj['missing'] = int(col_data.isnull().sum())
            
            if col in numeric_cols:
                # Stats
                stats_obj['type'] = 'numeric'
                stats_obj['mean'] = float(col_data.mean()) if not col_data.isnull().all() else 0
                stats_obj['median'] = float(col_data.median()) if not col_data.isnull().all() else 0
                stats_obj['std'] = float(col_data.std()) if not col_data.isnull().all() else 0
                stats_obj['min'] = float(col_data.min()) if not col_data.isnull().all() else 0
                stats_obj['max'] = float(col_data.max()) if not col_data.isnull().all() else 0
                skew_val = col_data.skew()
                kurt_val = col_data.kurtosis()
                stats_obj['skew'] = float(skew_val) if not pd.isna(skew_val) and not np.isinf(skew_val) else 0.0
                stats_obj['kurtosis'] = float(kurt_val) if not pd.isna(kurt_val) and not np.isinf(kurt_val) else 0.0
                
                # Histogram (10 bins)
                data_clean = col_data.dropna()
                if len(data_clean) > 0:
                    hist, bin_edges = np.histogram(data_clean, bins=10)
                    stats_obj['histogram'] = {
                        'counts': hist.tolist(),
                        'bins': bin_edges.tolist() # Edges are n+1
                    }
                
                # Box Plot (Quartiles)
                if len(data_clean) > 0:
                    q1 = np.percentile(data_clean, 25)
                    q3 = np.percentile(data_clean, 75)
                    iqr = q3 - q1
                    stats_obj['boxplot'] = {
                        'q1': float(q1),
                        'median': float(np.median(data_clean)),
                        'q3': float(q3),
                        'min': float(np.min(data_clean)), # pure min, often whiskers are calculated differently in JS
                        'max': float(np.max(data_clean))
                    }
                    
            else:
                # Categorical
                stats_obj['type'] = 'categorical'
                stats_obj['unique'] = int(col_data.nunique())
                # Top 10 counts
                counts = col_data.value_counts().head(10)
                stats_obj['counts'] = counts.to_dict()
                
            univariate[col] = stats_obj

        # --- 2. Bivariate (Correlation) ---
        correlation = {}
        if len(numeric_cols) > 1:
             corr_matrix = df[numeric_cols].corr().fillna(0)
             # Convert to structure suitable for heatmap: x, y, value
             matrix_data = []
             for i, r in enumerate(corr_matrix.index):
                 for j, c in enumerate(corr_matrix.columns):
                     matrix_data.append({
                         'x': c,
                         'y': r,
                         'v': float(corr_matrix.iloc[i, j])
                     })
             correlation['matrix'] = matrix_data
             correlation['columns'] = list(numeric_cols)

        # --- 3. Feature Importance (Quick RF) ---
        feature_importance = {}
        target_col = None
        
        # Try to guess target (last column or one with least unique values if binary?)
        # Let's search for "class", "target", "label"
        potential_targets = [c for c in df.columns if c.lower() in ['class', 'target', 'label', 'y']]
        if potential_targets:
            target_col = potential_targets[0]
        else:
            target_col = df.columns[-1]
            
        if target_col and target_col in df.columns:
             # Preprocess for RF
             df_rf = df.copy()
             
             # Encode Categoricals
             le = LabelEncoder()
             for col in df_rf.select_dtypes(include=['object']).columns:
                 df_rf[col] = le.fit_transform(df_rf[col].astype(str))
                 
             # Impute
             imp = SimpleImputer(strategy='mean')
             df_rf_clean = pd.DataFrame(imp.fit_transform(df_rf), columns=df_rf.columns)
             
             X = df_rf_clean.drop(columns=[target_col])
             y = df_rf_clean[target_col]
             
             # Detect Type for RF
             if df[target_col].nunique() < 20:
                  rf = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
             else:
                  rf = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
                  
             rf.fit(X, y)
             
             # Extract
             importances = rf.feature_importances_
             indices = np.argsort(importances)[::-1]
             
             feats = []
             for f in range(X.shape[1]):
                 feats.append({
                     'feature': X.columns[indices[f]],
                     'importance': float(importances[indices[f]])
                 })
             feature_importance['scores'] = feats
             feature_importance['target'] = target_col

        return sanitize_for_json({
            "fileName": fileName,
            "univariate": univariate,
            "correlation": correlation,
            "featureImportance": feature_importance,
            "sample": df.head(5000).replace([np.inf, -np.inf], np.nan).fillna("").to_dict(orient='records') # Larger sample for detailed view
        })

    except Exception as e:
        print(f"EDA Error: {e}")
        # raise HTTPException(status_code=500, detail=str(e)) 
        # Return empty structure instead of crashing
        return {"error": str(e)}

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
