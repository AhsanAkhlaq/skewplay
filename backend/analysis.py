import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from collections import Counter
from typing import Dict, Any, Tuple

class ImbalanceAnalyzer:
    def __init__(self, random_state=42):
        self.random_state = random_state

    def calculate_metrics(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Calculates comprehensive imbalance metrics:
        1. Class Distribution & IR
        2. Data Complexity (Safe/Borderline/Rare/Outlier) via k-NN
        3. PCA Projection (2D) for visualization
        """
        # 1. Basic Distribution
        counts = y.value_counts().to_dict()
        
        if not counts:
             return {
                "distribution": {},
                "imbalance_ratio": 0,
                "complexity": {"safe":0, "borderline":0, "rare":0},
                "pca": {},
                "shape": [0, 0],
                "technique_status": {}
            }

        majority_class = max(counts, key=counts.get)
        minority_class = min(counts, key=counts.get)
        
        n_majority = counts[majority_class]
        n_minority = counts[minority_class]
        
        ir = n_majority / n_minority if n_minority > 0 else 0
        
        # 2. Complexity / Hardness Analysis (k=5)
        # We only analyze minority samples to see how "hard" they are.
        # Safe: 4-5 neighbors are same class
        # Borderline: 2-3 neighbors are same class
        # Rare/Outlier: 0-1 neighbor is same class
        
        complexity = {
            "safe": 0,
            "borderline": 0,
            "rare": 0
        }
        
        # Sampling for large datasets to keep it fast
        MAX_SAMPLES = 2000
        if len(X) > MAX_SAMPLES:
            # Stratified sample if possible, or just sample
            # For complexity analysis, we need the whole density, so downsampling 
            # might distort neighbors. However, for UI responsiveness we might need to.
            # Let's try to use full dataset but limited query if X is huge.
             pass 

        # Only run if we have enough samples for k=5
        if len(X) > 6:
            try:
                # Scale for k-NN
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X.select_dtypes(include=[np.number]))
                
                # Check if we have numeric features
                if X_scaled.shape[1] > 0:
                    neigh = NearestNeighbors(n_neighbors=6) # 1 self + 5 neighbors
                    neigh.fit(X_scaled)
                    
                    # Find neighbors for all points
                    distances, indices = neigh.kneighbors(X_scaled)
                    
                    # Analyze Minority Class instances
                    y_arr = y.to_numpy()
                    minority_indices = np.where(y_arr == minority_class)[0]
                    
                    for idx in minority_indices:
                        # Get neighbors (exclude self at index 0)
                        neighbor_indices = indices[idx, 1:] 
                        neighbor_classes = y_arr[neighbor_indices]
                        
                        # Count how many neighbors are SAME class (Minority)
                        same_class_count = np.sum(neighbor_classes == minority_class)
                        
                        if same_class_count >= 4:
                            complexity["safe"] += 1
                        elif same_class_count >= 2:
                            complexity["borderline"] += 1
                        else:
                            complexity["rare"] += 1
                            
                    # Normalize percentages
                    total_minority = len(minority_indices)
                    if total_minority > 0:
                        complexity = {k: round((v / total_minority) * 100, 1) for k, v in complexity.items()}
            except Exception as e:
                print(f"Complexity analysis failed: {e}")

        # 3. PCA Projection (3D)
        pca_coords = self.get_pca_coordinates(X, y)

        # 4. Determine Valid Techniques with Reasons
        technique_status = {}
        
        # Helper to set status
        def set_status(name, is_valid, reason=""):
            technique_status[name] = {"valid": is_valid, "reason": reason}

        # Oversampling
        if n_minority >= 1:
            set_status("RandomOverSampler", True)
        else:
            set_status("RandomOverSampler", False, "Requires at least 1 minority sample.")

        if n_minority >= 2:
            set_status("SMOTE", True)
            set_status("ADASYN", True)
        else:
             msg = f"Requires at least 2 minority samples (Got {n_minority})."
             set_status("SMOTE", False, msg)
             set_status("ADASYN", False, msg)

        # Undersampling
        if len(X) > 50:
            set_status("RandomUnderSampler", True)
        else:
            set_status("RandomUnderSampler", False, "Dataset too small (<50 rows). Undersampling would lose critical data.")

        # Cleaning / Hybrid
        if n_minority >= 2: # heuristic for KNN based
            set_status("TomekLinks", True)
            set_status("ENN", True)
            set_status("SMOTETomek", True)
            set_status("SMOTEENN", True)
        else:
             msg = f"Requires at least 2 minority samples for neighbor analysis."
             set_status("TomekLinks", False, msg)
             set_status("ENN", False, msg)
             set_status("SMOTETomek", False, msg)
             set_status("SMOTEENN", False, msg)

        return {
            "distribution": counts,
            "imbalance_ratio": round(ir, 2),
            "complexity": complexity, # Percentages
            "pca": pca_coords,
            "shape": list(X.shape),
            "technique_status": technique_status
        }

    def get_pca_coordinates(self, X: pd.DataFrame, y: pd.Series, max_points=1000) -> Dict[str, Any]:
        """
        Returns 3D PCA coordinates for plotting. 
        Downsamples if dataset is too large to keep chart responsive.
        """
        try:
            # Handle Categorical: Only using numeric for PCA for simplicity
            X_numeric = X.select_dtypes(include=[np.number])
            
            if X_numeric.shape[1] < 3:
                 # If < 3 features, can't really do 3D PCA in the standard way without filling 0s or erroring.
                 # Allow 2D if only 2 features exist? 
                 # Let's try to do 3 components, it will output 0 for 3rd dim if rank is lower, or error.
                 # PCA implementation in sklearn handles n_components > n_features by capping components.
                 pass

            # Downsample for visualization
            if len(X) > max_points:
                # Simple random sample
                idx = np.random.choice(len(X), max_points, replace=False)
                X_subset = X_numeric.iloc[idx]
                y_subset = y.iloc[idx]
            else:
                X_subset = X_numeric
                y_subset = y

            # Impute if needed (PCA generally fails with NaNs)
            X_subset = X_subset.fillna(X_subset.mean())

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_subset)
            
            # Determine suitable n_components
            n_cols = X_scaled.shape[1]
            n_comps = min(n_cols, 3)
            
            pca = PCA(n_components=n_comps, random_state=self.random_state)
            X_pca = pca.fit_transform(X_scaled)
            
            result = {
                "x": X_pca[:, 0].tolist(),
                "y": X_pca[:, 1].tolist() if n_comps >= 2 else [0]*len(X_pca),
                "z": X_pca[:, 2].tolist() if n_comps >= 3 else [0]*len(X_pca),
                "labels": y_subset.tolist(),
                "explained_variance": pca.explained_variance_ratio_.tolist()
            }
            return result
            
        except Exception as e:
            print(f"PCA generation failed: {e}")
            return {}
