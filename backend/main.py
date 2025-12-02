import os
import shutil
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import uuid
from datetime import datetime

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
SAMPLES_DIR = "samples"
UPLOADS_DIR = "uploads"

os.makedirs(SAMPLES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount static files to serve CSVs
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

def analyze_csv(file_path: str) -> Dict[str, Any]:
    try:
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        # Simple heuristic for target column (last column)
        target_col = df.columns[-1]
        
        # Check if classification
        if df[target_col].nunique() < 20: # Assume classification if < 20 unique values
            value_counts = df[target_col].value_counts(normalize=True).to_dict()
            imbalance_ratios = {str(k): float(v) for k, v in value_counts.items()}
            type_ = "binary" if len(value_counts) == 2 else "multiclass"
        else:
            imbalance_ratios = {}
            type_ = "regression" # Fallback

        return {
            "rowCount": row_count,
            "type": type_,
            "imbalanceRatios": imbalance_ratios,
            "anomalies": [], # Placeholder for now
            "sizeBytes": os.path.getsize(file_path),
            "targetCol": target_col
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            "rowCount": 0,
            "type": "unknown",
            "imbalanceRatios": {},
            "anomalies": [],
            "sizeBytes": 0
        }

@app.get("/samples")
async def get_samples():
    samples = []
    for filename in os.listdir(SAMPLES_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(SAMPLES_DIR, filename)
            analysis = analyze_csv(file_path)
            
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
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        analysis = analyze_csv(file_path)
        
        return {
            "fileName": file.filename, # Return original name for display
            "storagePath": f"http://localhost:8000/uploads/{filename}",
            **analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
