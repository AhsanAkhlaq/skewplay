
import faulthandler
faulthandler.enable()

import os
import shutil
import json
import uuid
import joblib
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ML & Stats Imports
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from scipy.stats import entropy

from preprocessing import PreprocessingPipeline
from balancing import BalancingPipeline
from models import ModelFactory
from analysis import ImbalanceAnalyzer

from utils import get_user_storage_usage
from json_utils import sanitize_for_json

def validate_classification_target(df: pd.DataFrame, target_col: str) -> dict:
    if target_col not in df.columns:
        return {"valid": False, "error": "Target column not found."}
        
    target_series = df[target_col]
    
    # 1. Strict Data Type Check
    if pd.api.types.is_float_dtype(target_series):
        return {"valid": False, "error": "Target contains decimals (float). This is a regression problem. Please select a categorical target."}
        
    # 2. The Absolute Cap (For Integers/Strings)
    unique_count = target_series.nunique()
    MAX_CLASSES = 50 # Safe absolute cap
    
    if unique_count > MAX_CLASSES:
        return {"valid": False, "error": f"Target has {unique_count} unique classes (Max allowed is {MAX_CLASSES}). This looks like continuous data or an ID column."}
        
    if unique_count < 2:
        return {"valid": False, "error": "Target must have at least 2 unique classes."}
        
    # 3. The Minimum Minority Samples Rule (For SMOTE)
    MIN_SAMPLES_NEEDED = 6 # k=5 neighbors + 1
    class_counts = target_series.value_counts()
    rarest_class_count = class_counts.min()
    
    if rarest_class_count < MIN_SAMPLES_NEEDED:
        return {"valid": False, "error": f"The rarest class only has {rarest_class_count} rows. Imbalance algorithms require at least {MIN_SAMPLES_NEEDED} rows per class to work."}
        
    return {"valid": True, "message": "Valid classification target."}

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
    targetCol: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
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
        if targetCol:
            # We read the saved file just to validate the target column properly
            df_val = pd.read_csv(file_path)
            validation = validate_classification_target(df_val, targetCol)
            if not validation["valid"]:
                os.remove(file_path) # cleanup
                raise HTTPException(status_code=400, detail=validation["error"])

        analysis = analyze_csv(file_path, user_target_col=targetCol)
        
        # 5. Return Metadata
        # URL construction: http://localhost:8000/storage/{userId}/datasets/{filename}
        storage_path = f"http://localhost:8000/storage/{userId}/datasets/{filename}"

        return sanitize_for_json({
            "fileName": file.filename, 
            "storagePath": storage_path,
            "description": description,
            **analysis
        })
    except HTTPException as he:
        # Re-raise HTTPExceptions so frontend receives them correctly
        raise he
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")  


@app.post("/reanalyze")
async def reanalyze_dataset(
    userId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(...)
):
    try:
        # 1. Locate file
        # Note: fileName must be the actual on-disk filename (with timestamp prefix if present).
        
        user_datasets_dir = os.path.join(STORAGE_DIR, userId, "datasets")
        file_path = os.path.join(user_datasets_dir, fileName)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # 2. Validate Target Column
        df = pd.read_csv(file_path)
        validation = validate_classification_target(df, targetCol)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])

        # 3. Re-Analyze
        analysis = analyze_csv(file_path, user_target_col=targetCol)
        
        return sanitize_for_json(analysis)

    except HTTPException as he:
        raise he
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
        for col in df.select_dtypes(include=['object', 'category', 'str']).columns:
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

def calculate_pca(df, target_col):
    try:
        # Select all columns and encode categoricals for PCA visualization
        # We use a copy to avoid modifying original df if passed by reference (though here it's usually fresh)
        df_pca = df.copy().dropna()
        
        # Limit rows first to speed up processing
        if len(df_pca) > 2000:
             df_pca = df_pca.sample(2000, random_state=42)   
        # Encode Categoricals
        le = LabelEncoder()
        for col in df_pca.select_dtypes(include=['object', 'category', 'str']).columns:
             df_pca[col] = le.fit_transform(df_pca[col].astype(str))
             
        # Now we have all numeric (native or encoded)
        if df_pca.shape[1] < 2:
            return []
        # Standardize
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_pca)
        # PCA
        n_comps = min(3, scaled_data.shape[0], scaled_data.shape[1])
        pca = PCA(n_components=n_comps)
        components = pca.fit_transform(scaled_data)
        # Get targets for coloring
        targets = []
        if target_col and target_col in df.columns:
            targets = df.loc[df_pca.index, target_col].astype(str).tolist()
        else:
            targets = ["n/a"] * len(components)
        # Format
        plot_data = []
        for i in range(len(components)):
            plot_data.append({
                "x": float(components[i, 0]) if n_comps > 0 else 0.0,
                "y": float(components[i, 1]) if n_comps > 1 else 0.0,
                "z": float(components[i, 2]) if n_comps > 2 else 0.0,
                "target": targets[i]
            })
        return plot_data
    except Exception as e:
        print(f"PCA Error: {e}")
        return []

@app.post("/perform-eda")
async def perform_eda(
    userId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(None) # Optional target column
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
        
        # Filter dropped rows if targetCol is known
        if targetCol and targetCol != 'Unknown' and targetCol in df.columns:
             df = df.dropna(subset=[targetCol])
        
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
        categorical_cols = df.select_dtypes(include=['object', 'category', 'str']).columns
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

                # ADDED: For numeric columns with few unique values (e.g. binary extraction), treat as categorical for counts
                if col_data.nunique() < 50:
                    counts = col_data.value_counts().head(10)
                    stats_obj['counts'] = {str(k): int(v) for k, v in counts.items()} # Ensure keys are strings for JSON

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
        target_col = targetCol
        
        # Try to guess target ONLY if targetCol is not provided
        if not target_col or target_col == 'Unknown':
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
             for col in df_rf.select_dtypes(include=['object', 'str']).columns:
                 df_rf[col] = le.fit_transform(df_rf[col].astype(str))
                 
             # Impute
             imp = SimpleImputer(strategy='mean')
             df_rf_clean = pd.DataFrame(imp.fit_transform(df_rf), columns=df_rf.columns)
             
             X = df_rf_clean.drop(columns=[target_col])
             y = df_rf_clean[target_col]
             
             # Detect Type for RF
             is_categorical = False
             target_dtype = df[target_col].dtype
             
             if target_dtype == 'object' or target_dtype.name == 'category':
                 is_categorical = True
             elif pd.api.types.is_integer_dtype(target_dtype) and df[target_col].nunique() < 20:
                 is_categorical = True
             
             if is_categorical:
                  # Ensure classes are integers (SimpleImputer might have made them floats)
                  y = y.astype(int)
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
        # --- 4. PCA and Target Stats ---
        pca_data = calculate_pca(df, target_col)
        return sanitize_for_json({
            "fileName": fileName,
            "univariate": univariate,
            "correlation": correlation,
            "featureImportance": feature_importance,
            "sample": df.head(5000).replace([np.inf, -np.inf], np.nan).fillna("").to_dict(orient='records'), # Larger sample for detailed view
            "targetStats": {
                "entropy": float(entropy(df[target_col].value_counts(normalize=True))) if target_col and target_col in df.columns else 0,
                "imbalanceRatio": (df[target_col].value_counts().max() / df[target_col].value_counts().min()) if target_col and target_col in df.columns and len(df[target_col].value_counts()) > 0 else 1,
                "kurtosis": float(df[target_col].kurtosis()) if target_col and target_col in df.columns and pd.api.types.is_numeric_dtype(df[target_col]) else None,
                "skew": float(df[target_col].skew()) if target_col and target_col in df.columns and pd.api.types.is_numeric_dtype(df[target_col]) else None
            },
            "pca": pca_data
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

@app.post("/preprocess")
async def preprocess_data(
    userId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(...),
    workflowId: str = Form(...), # New: Workflow ID for unique storage
    config: str = Form(...)  # JSON string
):
    try:
        from preprocessing import PreprocessingPipeline
        
        # Parse Config
        cfg = json.loads(config)
        
        # 1. Load Data
        if fileName in SAMPLE_TARGETS:
             file_path = os.path.join(SAMPLES_DIR, fileName)
        else:
             file_path = os.path.join(STORAGE_DIR, userId, "datasets", fileName)
        
        if not os.path.exists(file_path):
             raise HTTPException(status_code=404, detail=f"File not found: {fileName}")

        df = pd.read_csv(file_path)
        
        # 2. Output Directory
        output_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "preprocessing")
        
        # 3. Run Pipeline
        pipeline = PreprocessingPipeline(cfg)
        result = pipeline.run(df, targetCol, output_dir)
        
        # 4. Construct Response
        result["timestamp"] = datetime.now().isoformat()
        
        return sanitize_for_json(result)

    except Exception as e:
        print(f"Preprocessing Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/imbalance-analysis")
async def analyze_imbalance(
    userId: str = Form(...),
    workflowId: str = Form(...)
):
    try:
        from analysis import ImbalanceAnalyzer
        
         # Locate Preprocessed Data
        artifacts_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "preprocessing")
        X_train_path = os.path.join(artifacts_dir, "X_train.parquet")
        y_train_path = os.path.join(artifacts_dir, "y_train.parquet")
        
        if not os.path.exists(X_train_path) or not os.path.exists(y_train_path):
             return sanitize_for_json({"status": "NoData"})
        
        X_train = pd.read_parquet(X_train_path)
        y_train = pd.read_parquet(y_train_path)
        print('eeee')
        print(y_train.head())
        y_train = y_train.iloc[:, 0]
        print('wwww')
        print(y_train.head())

        analyzer = ImbalanceAnalyzer()
        metrics = analyzer.calculate_metrics(X_train, y_train)
        
        return sanitize_for_json(metrics)

    except Exception as e:
        print(f"Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/balance")
async def balance_data(
    userId: str = Form(...),
    workflowId: str = Form(...),
    config: str = Form(...)  # JSON string
):
    try:
        
        # 1. Parse Config
        cfg = json.loads(config)
        
        # 2. Locate Artifacts
        # We need X_train and y_train from the preprocessing step
        artifacts_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "preprocessing")
        
        X_train_path = os.path.join(artifacts_dir, "X_train.parquet")
        y_train_path = os.path.join(artifacts_dir, "y_train.parquet")
        
        if not os.path.exists(X_train_path) or not os.path.exists(y_train_path):
             raise HTTPException(status_code=404, detail="Preprocessed training data not found. Run preprocessing first.")
             
        # 3. Load Data
        X_train = pd.read_parquet(X_train_path)
        y_train = pd.read_parquet(y_train_path).iloc[:, 0] # Series
   
        
        # 4. Initialize Balancing Pipeline
        balancing_cfg = cfg.get('imbalance', {})
        pipeline = BalancingPipeline(balancing_cfg)
        
        # 5. Apply Balancing
        X_resampled, y_resampled, metadata = pipeline.apply_balancing(X_train, y_train)
        
        # 6. Save Results
        balancing_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "balancing")
        os.makedirs(balancing_dir, exist_ok=True)
        
        X_resampled.to_parquet(os.path.join(balancing_dir, "X_train_resampled.parquet"))
        pd.DataFrame({'target': y_resampled}).to_parquet(os.path.join(balancing_dir, "y_train_resampled.parquet"))
        
        # 7. Post-Processing Analysis (PCA for visualization)
        analyzer = ImbalanceAnalyzer()
        # We only need PCA coordinates for the balanced dataset to plot it
        pca_coords = analyzer.get_pca_coordinates(X_resampled, y_resampled)

        # 8. Return Metadata
        return sanitize_for_json({
            "status": "Completed",
            "distribution": metadata,
            "shape": {
                "before": list(X_train.shape),
                "after": list(X_resampled.shape)
            },
            "pca": pca_coords, 
            "artifactsPath": balancing_dir
        })

    except Exception as e:
        print(f"Balancing Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_experiment(
    userId: str = Form(...),
    workflowId: str = Form(...),
    fileName: str = Form(...),
    targetCol: str = Form(...),
    config: str = Form(...)  # JSON string
):
    try:
        # Parse Config
        cfg = json.loads(config)
        
        # Preprocessing artifacts
        pp_artifacts_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "preprocessing")
        
        # Load test data from preprocessing
        X_test_path = os.path.join(pp_artifacts_dir, "X_test.parquet")
        y_test_path = os.path.join(pp_artifacts_dir, "y_test.parquet")
        
        if not os.path.exists(X_test_path) or not os.path.exists(y_test_path):
             raise HTTPException(status_code=404, detail="Preprocessed test data not found. Run preprocessing first.")
             
        X_test = pd.read_parquet(X_test_path)
        y_test = pd.read_parquet(y_test_path).iloc[:, 0]
        
        # Check if balancing was applied
        balancing_cfg = cfg.get('imbalance', {})
        if balancing_cfg.get('technique', 'None') != 'None':
             bal_artifacts_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "balancing")
             X_train_path = os.path.join(bal_artifacts_dir, "X_train_resampled.parquet")
             y_train_path = os.path.join(bal_artifacts_dir, "y_train_resampled.parquet")
             if not os.path.exists(X_train_path) or not os.path.exists(y_train_path):
                  raise HTTPException(status_code=404, detail="Balanced training data not found. Run balancing first.")
        else:
             X_train_path = os.path.join(pp_artifacts_dir, "X_train.parquet")
             y_train_path = os.path.join(pp_artifacts_dir, "y_train.parquet")
             if not os.path.exists(X_train_path) or not os.path.exists(y_train_path):
                  raise HTTPException(status_code=404, detail="Preprocessed training data not found. Run preprocessing first.")
             
        X_final_train = pd.read_parquet(X_train_path)
        y_final_train = pd.read_parquet(y_train_path).iloc[:, 0]

        # 4. Model Initialization & Training
        model_cfg = cfg.get('model', {})
        algo = model_cfg.get('algorithm', 'RandomForest')
        params = model_cfg.get('hyperparameters', {})
        
        model = ModelFactory.get_model(algo, params)

        # Fit
        model.fit(X_final_train, y_final_train)

        # 5. Evaluation
        is_multiclass = len(np.unique(y_test)) > 2
        y_pred = model.predict(X_test)
        
        y_prob = None
        if hasattr(model, "predict_proba"):
             y_prob = model.predict_proba(X_test)
             if not is_multiclass:
                  y_prob = y_prob[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        
        if is_multiclass:
            f1_metric = f1_score(y_test, y_pred, average='weighted')
            prec_metric = precision_score(y_test, y_pred, average='weighted')
            rec_metric = recall_score(y_test, y_pred, average='weighted')
            g_mean = 0.0 # G-Mean is complex for multiclass, defaulting to 0 or macro-avg
            pr_auc = 0.0 # PR-AUC natively isn't singular for multiclass without binarization
        else:
            # Assume minority class is 1 or second distinct value
            pos_label = np.unique(y_test)[-1] if 1 not in np.unique(y_test) else 1
            f1_metric = f1_score(y_test, y_pred, pos_label=pos_label, average='binary')
            prec_metric = precision_score(y_test, y_pred, pos_label=pos_label, average='binary')
            rec_metric = recall_score(y_test, y_pred, pos_label=pos_label, average='binary')
            
            tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            g_mean = (sensitivity * specificity) ** 0.5
            
            pr_auc = 0.0
            if y_prob is not None:
                from sklearn.metrics import average_precision_score
                pr_auc = average_precision_score(y_test, y_prob)

        metrics = {
            "accuracy": round(acc, 4),
            "f1Score": round(f1_metric, 4),
            "precision": round(prec_metric, 4),
            "recall": round(rec_metric, 4),
            "prAuc": round(pr_auc, 4),
            "gMean": round(g_mean, 4),
            "executionTimeSeconds": 0.5 
        }
        
        # 6. Save Artifacts strictly under workflow artifacts correctly
        artifacts_dir = os.path.join(STORAGE_DIR, userId, "workflows", workflowId, "artifacts", "model")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Save Model
        model_filename = "model.joblib"
        joblib.dump(model, os.path.join(artifacts_dir, model_filename))
        
        # Save Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix ({algo})')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        cm_filename = "confusion_matrix.png"
        plt.savefig(os.path.join(artifacts_dir, cm_filename))
        plt.close()

        # Save Precision-Recall Curve (only for binary with proba)
        pr_curve_filename = ""
        if y_prob is not None and not is_multiclass:
             from sklearn.metrics import PrecisionRecallDisplay
             plt.figure(figsize=(6, 5))
             PrecisionRecallDisplay.from_predictions(y_test, y_prob, name=algo)
             plt.title("Precision-Recall Curve")
             pr_curve_filename = "pr_curve.png"
             plt.savefig(os.path.join(artifacts_dir, pr_curve_filename))
             plt.close()


        # Save Feature Importance (if available)
        feat_imp_filename = ""
        feature_names = X_test.columns.tolist() if hasattr(X_test, 'columns') else [f"f{i}" for i in range(X_test.shape[1])]
        
        importances = None
        if hasattr(model, "feature_importances_"):
             importances = model.feature_importances_
        elif hasattr(model, "coef_"):
             importances = np.abs(model.coef_[0])
             
        if importances is not None:
             # Top 20
             indices = np.argsort(importances)[::-1][:20]
             top_feats = [feature_names[i] for i in indices]
             top_imps = importances[indices]
             
             plt.figure(figsize=(8, 6))
             sns.barplot(x=top_imps, y=top_feats, palette="viridis")
             plt.title("Feature Importance (Top 20)")
             plt.xlabel("Importance")
             feat_imp_filename = "feature_importance.png"
             plt.tight_layout()
             plt.savefig(os.path.join(artifacts_dir, feat_imp_filename))
             plt.close()

        # URLs
        artifacts = {
             "modelPath": f"http://localhost:8000/storage/{userId}/workflows/{workflowId}/artifacts/model/{model_filename}",
             "confusionMatrixUrl": f"http://localhost:8000/storage/{userId}/workflows/{workflowId}/artifacts/model/{cm_filename}",
             "prCurveUrl": f"http://localhost:8000/storage/{userId}/workflows/{workflowId}/artifacts/model/{pr_curve_filename}" if pr_curve_filename else None,
             "featureImportanceUrl": f"http://localhost:8000/storage/{userId}/workflows/{workflowId}/artifacts/model/{feat_imp_filename}" if feat_imp_filename else None,
        }

        return sanitize_for_json({
            "status": "Completed",
            "results": metrics,
            "artifacts": artifacts
        })

    except Exception as e:
        print(f"Run Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
