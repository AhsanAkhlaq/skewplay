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
