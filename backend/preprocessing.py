import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, 
    OneHotEncoder, OrdinalEncoder, LabelEncoder, 
    FunctionTransformer, PowerTransformer
)
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif, f_regression
from sklearn.decomposition import PCA

# Try importing TargetEncoder (sklearn >= 1.3)
try:
    from sklearn.preprocessing import TargetEncoder
except ImportError:
    TargetEncoder = None

class PreprocessingPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.split_ratio = float(config.get('splitRatio', 0.2))
        self.random_state = 42
        self.dropped_features = set(config.get('droppedFeatures', []))
        self.feature_configs = config.get('featureConfigs', {})
        self.selection_config = config.get('selection', {})
        
        # Artifacts to be saved
        self.preprocessor = None
        self.selector = None
        self.label_encoder = None
        self.target_mapping = {}

    def run(self, df: pd.DataFrame, target_col: str, output_dir: str) -> Dict[str, Any]:
        """
        Main execution method for the preprocessing pipeline.
        
        Args:
            df: Input DataFrame.
            target_col: Name of the target column.
            output_dir: Directory to save artifacts.
            
        Returns:
            Dictionary containing execution summary and artifact paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Clean and Split Data
        X, y, dropped_rows = self._prepare_data(df, target_col)
        
        # 2. Train/Test Split
        # Stratify if classification (heuristic: < 50 unique values in target)
        is_classification = False
        if y is not None:
             if y.nunique() < 50 or y.dtype == 'object':
                 is_classification = True
        
        stratify = y if is_classification else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.split_ratio, random_state=self.random_state, stratify=stratify
        )
        
        # 3. Build and Fit Preprocessor
        self.preprocessor = self._build_column_transformer(X_train)
        
        # Fit on Train, Transform both
        # Pass y_train for TargetEncoder compatibility
        X_train_transformed = self.preprocessor.fit_transform(X_train, y_train)
        X_test_transformed = self.preprocessor.transform(X_test)
        
        # 4. Feature Selection (Optional)
        if self.selection_config.get('method') != 'None':
            self.selector = self._build_selector(self.selection_config, is_classification)
            if self.selector:
                 X_train_transformed = self.selector.fit_transform(X_train_transformed, y_train)
                 X_test_transformed = self.selector.transform(X_test_transformed)

        # 5. Save Artifacts
        artifact_paths = self._save_results(
            output_dir, 
            X_train_transformed, X_test_transformed, 
            y_train, y_test
        )
        
        # 6. Generate Preview
        # Convert sparse matrix to dense for preview if necessary
        preview_data = X_train_transformed[:10]
        if hasattr(preview_data, "toarray"):
            preview_data = preview_data.toarray()
            
        # Attempt to recover feature names
        feature_names = self._get_feature_names()
        
        # Fix: Check if list/array is empty or length mismatch safely for numpy arrays
        is_empty = feature_names is None or len(feature_names) == 0
        if is_empty or len(feature_names) != X_train_transformed.shape[1]:
             feature_names = [f"Feature_{i}" for i in range(X_train_transformed.shape[1])]
        # Convert to list if it is an array
        elif hasattr(feature_names, 'tolist'):
             feature_names = feature_names.tolist()
        
        # Create preview dictionaries
        preview_list = []
        if isinstance(preview_data, np.ndarray):
            for row in preview_data:
                # Zip with feature names if available, else generic indices
                if len(feature_names) == len(row):
                     preview_list.append(dict(zip(feature_names, row)))
                else:
                     preview_list.append(dict(zip([f"Feat_{i}" for i in range(len(row))], row)))

        # Calculate Distributions
        def get_dist(series):
             if series is None: return {}
             # If categorical/object/int with few values
             try:
                 vc = series.value_counts().to_dict()
                 # Map if encoded
                 if self.target_mapping:
                     # Key in vc is integer (encoded), map to original string
                     # Ensure keys are matched correctly (int vs int)
                     return {self.target_mapping.get(int(k), str(k)): int(v) for k, v in vc.items()}
                 return {str(k): int(v) for k, v in vc.items()}
             except:
                 return {}

        train_dist = get_dist(y_train)
        test_dist = get_dist(y_test)
        
        # Calculate Correlations (on Transformed Data)
        correlation_data = {}
        feature_importance = []
        try:
            # Densify if sparse (limit size to avoid OOM)
            # Limit to 500 features for correlation calculation
            max_features = 200
            features_to_corr = feature_names[:max_features]
            
            data_for_corr = X_train_transformed[:, :max_features]
            if hasattr(data_for_corr, "toarray"):
                data_for_corr = data_for_corr.toarray()
                
            df_corr = pd.DataFrame(data_for_corr, columns=features_to_corr)
            
            # Add target if numeric (or encoded)
            target_series = y_train
            # If target is Series with name
            t_name = 'target'
            if hasattr(y_train, 'name') and y_train.name:
                t_name = str(y_train.name)
            
            # Ensure target is accessible/numeric
            if is_classification and self.label_encoder:
                 df_corr[t_name] = y_train.values
            elif pd.api.types.is_numeric_dtype(y_train):
                 df_corr[t_name] = y_train.values

            # Compute Correlation Matrix
            corr_mat = df_corr.corr(method='pearson')
            
            # Format for frontend: columns list, and matrix array of {x, y, v}
            # Only send non-zero or significant correlations to save space? 
            # Frontend expects dense matrix style usually, or sparse tuples.
            # EdaDashboard expects: { columns: string[], matrix: {x,y,v}[] }
            
            corr_columns = corr_mat.columns.tolist()
            corr_values = []
            
            # Iterate to build matrix list
            # To optimize, we can rely on symmetry, but frontend might expect full.
            for c1 in corr_columns:
                for c2 in corr_columns:
                    val = corr_mat.loc[c1, c2]
                    if not pd.isna(val):
                        corr_values.append({"x": c1, "y": c2, "v": float(val)})
            
            correlation_data = {
                "columns": corr_columns,
                "matrix": corr_values
            }
            
            # Extract Feature Importance (Correlation with Target)
            if t_name in corr_mat.columns:
                 target_corrs = corr_mat[t_name].drop(index=[t_name])
                 # Sort by absolute value
                 sorted_corrs = target_corrs.abs().sort_values(ascending=False)
                 feature_importance = [
                     {"feature": idx, "importance": float(val)} 
                     for idx, val in sorted_corrs.items()
                 ]

        except Exception as e:
            print(f"Warning: Correlation calculation failed: {e}")
            
        return {
            "status": "Completed",
            "trainCount": int(X_train_transformed.shape[0]),
            "testCount": int(X_test_transformed.shape[0]),
            "featureCount": int(X_train_transformed.shape[1]),
            "features": feature_names,
            "targetMapping": self.target_mapping,
            "trainDistribution": train_dist,
            "testDistribution": test_dist,
            "droppedRows": dropped_rows,
            "processedData": preview_list,
            "processedShape": list(X_train_transformed.shape),
            "processedCorrelation": correlation_data,
            "featureImportance": feature_importance,
            "artifactsPath": output_dir, 
            "artifacts": artifact_paths
        }

    def _prepare_data(self, df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series, int]:
        """Separates target, drops ignored features, cleans target."""
        # Drop rows with missing target
        dropped_rows = 0
        if target_col in df.columns:
            initial_count = len(df)
            df = df.dropna(subset=[target_col])
            dropped_rows = initial_count - len(df)
        else:
            raise ValueError(f"Target column '{target_col}' not found in dataset.")
            
        # Split X, y
        y = df[target_col]
        X = df.drop(columns=[target_col])
        
        # Drop ignored features
        if self.dropped_features:
            X = X.drop(columns=[col for col in self.dropped_features if col in X.columns], errors='ignore')
            
        # Encode Target if categorical
        if y.dtype == 'object' or y.dtype.name == 'category' or y.nunique() < 50:
            # Check if it's already numeric though
            if not pd.api.types.is_numeric_dtype(y):
                self.label_encoder = LabelEncoder()
                y = pd.Series(self.label_encoder.fit_transform(y), index=y.index, name=target_col)
                self.target_mapping = {int(i): str(l) for i, l in enumerate(self.label_encoder.classes_)}
            
        return X, y, dropped_rows

    def _build_column_transformer(self, X: pd.DataFrame) -> ColumnTransformer:
        """Constructs the ColumnTransformer based on featureConfigs."""
        transformers = []
        
        # Default Strategies
        numeric_cols = X.select_dtypes(include=['number']).columns
        # categorical_cols = X.select_dtypes(include=['object', 'category']).columns

        # Helper to create pipeline for a single feature or group
        def create_feature_pipeline(config, dtype='numeric'):
            steps = []
            
            # 1. Imputation
            strategy = config.get('strategy', 'mean' if dtype == 'numeric' else 'most_frequent')
            if strategy == 'knn':
                k = int(config.get('params', {}).get('n_neighbors', 5))
                steps.append(('imputer', KNNImputer(n_neighbors=k)))
            elif strategy == 'constant':
                fill_value = config.get('params', {}).get('fill_value', 0 if dtype == 'numeric' else 'missing')
                # Ensure correct type for constant
                if dtype == 'numeric':
                     try: fill_value = float(fill_value)
                     except: fill_value = 0
                steps.append(('imputer', SimpleImputer(strategy='constant', fill_value=fill_value)))
            else:
                # mean, median, most_frequent
                steps.append(('imputer', SimpleImputer(strategy=strategy)))
                
            # 2. Transformation (Numeric only)
            if dtype == 'numeric':
                transform = config.get('transform', 'none')
                if transform == 'log':
                    steps.append(('transform', FunctionTransformer(np.log1p, validate=True)))
                elif transform == 'sqrt':
                    steps.append(('transform', FunctionTransformer(np.sqrt, validate=True)))
                elif transform == 'yeo-johnson':
                    steps.append(('transform', PowerTransformer(method='yeo-johnson')))
                elif transform == 'box-cox':
                    # Box-Cox requires strictly positive data
                    steps.append(('transform', PowerTransformer(method='box-cox')))
                    
                # 3. Scaling (Numeric only)
                scaler_type = config.get('scaling', 'Standard')
                if scaler_type == 'Standard':
                    steps.append(('scaler', StandardScaler()))
                elif scaler_type == 'MinMax':
                    steps.append(('scaler', MinMaxScaler()))
                elif scaler_type == 'Robust':
                    steps.append(('scaler', RobustScaler()))
                # None -> no step
                
            # 4. Encoding (Categorical only)
            if dtype == 'categorical':
                encoding = config.get('params', {}).get('encoding', 'OneHot')
                if encoding == 'OneHot':
                    steps.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
                elif encoding == 'Ordinal':
                    steps.append(('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)))
                elif encoding == 'Target':
                    if TargetEncoder:
                        steps.append(('encoder', TargetEncoder()))
                    else:
                        # Fallback if sklearn < 1.3
                         steps.append(('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)))

            return Pipeline(steps)

        # Build Transformers List
        for col in X.columns:
            # Get specific config or default
            if col in self.feature_configs:
                cfg = self.feature_configs[col]
                ftype = cfg.get('type', 'numeric')
            else:
                 # Infer fallback
                 if col in numeric_cols:
                     ftype = 'numeric' 
                     cfg = {'strategy': 'mean', 'scaling': 'Standard'}
                 else:
                     ftype = 'categorical'
                     cfg = {'strategy': 'most_frequent', 'params': {'encoding': 'OneHot'}}
            
            pipe = create_feature_pipeline(cfg, dtype=ftype)
            transformers.append((f"{col}_pipe", pipe, [col]))

        # Create ColumnTransformer
        # sparse_threshold=0 to force dense output if possible (easier for pandas/preview)
        # but for very large OneHot, sparse might be better. We'll use default (0.3).
        # n_jobs=None to avoid joblib resource tracker issues on Windows
        return ColumnTransformer(transformers=transformers, n_jobs=None, verbose_feature_names_out=False)

    def _build_selector(self, config: Dict, is_classification: bool):
        method = config.get('method')
        params = config.get('params', {})
        
        if method == 'VarianceThreshold':
            threshold = float(params.get('threshold', 0.0))
            return VarianceThreshold(threshold=threshold)
            
        elif method == 'SelectKBest':
            k = int(params.get('k', 10))
            # f_classif for Classifier, f_regression for Regressor
            score_func = f_classif if is_classification else f_regression
            return SelectKBest(score_func=score_func, k=k)
            
        elif method == 'PCA':
            n_components = float(params.get('n_components', 0.95))
            # If n_components > 1, it's integer count. If < 1, it's variance ratio.
            if n_components >= 1:
                n_components = int(n_components)
            return PCA(n_components=n_components)
            
        return None

    def _get_feature_names(self) -> List[str]:
        """Attempts to retrieve feature names from the fitted preprocessor."""
        try:
            # 1. Get feature names from the preprocessor (ColumnTransformer)
            feature_names = self.preprocessor.get_feature_names_out()
            
            # 2. If selector is applied, filter the feature names
            if self.selector:
                # We typically can't get feature names from a generic selector without input names
                # unless it supports it natively (rare for numpy input).
                # safely pass input_features
                if hasattr(self.selector, 'get_feature_names_out'):
                     return self.selector.get_feature_names_out(input_features=feature_names)
                else:
                     # Fallback for some selectors or if method missing
                     # e.g. PCA generates new components, doesn't select from input
                     if isinstance(self.selector, PCA):
                         return [f"PC{i+1}" for i in range(self.selector.n_components_)]
                     
            return feature_names
        except Exception as e:
            print(f"Warning: Could not retrieve feature names: {e}")
            return []

    def _save_results(self, output_dir: str, X_train, X_test, y_train, y_test) -> Dict[str, str]:
        """Saves transform data to parquet and pipelines to joblib."""
        
        # 1. Save Data (Parquet)
        # Convert to DataFrame for Parquet
        # Check if sparse
        if hasattr(X_train, "toarray"):
            X_train = X_train.toarray()
            X_test = X_test.toarray()
        
        feature_names = self._get_feature_names()
        is_empty = feature_names is None or len(feature_names) == 0
        if is_empty or len(feature_names) != X_train.shape[1]:
             feature_names = [f"feat_{i}" for i in range(X_train.shape[1])]
        elif hasattr(feature_names, 'tolist'):
             feature_names = feature_names.tolist()
             
        pd.DataFrame(X_train, columns=feature_names).to_parquet(os.path.join(output_dir, "X_train.parquet"))
        pd.DataFrame(X_test, columns=feature_names).to_parquet(os.path.join(output_dir, "X_test.parquet"))

       
        # Save Targets
        pd.DataFrame({'target': y_train}).to_parquet(os.path.join(output_dir, "y_train.parquet"))
        pd.DataFrame({'target': y_test}).to_parquet(os.path.join(output_dir, "y_test.parquet"))
        print(y_train.head())
        print('ttttttt')
        # Save Pipelines
        full_pipeline_steps = [('preprocessor', self.preprocessor)]
        if self.selector:
            full_pipeline_steps.append(('selector', self.selector))
            
        full_pipeline = Pipeline(full_pipeline_steps)
        
        pipeline_path = os.path.join(output_dir, "preprocessing_pipeline.joblib")
        joblib.dump(full_pipeline, pipeline_path)
        
        # Save Label Encoder
        encoder_path = ""
        if self.label_encoder:
            encoder_path = os.path.join(output_dir, "label_encoder.joblib")
            joblib.dump(self.label_encoder, encoder_path)
            
        return {
            "X_train": os.path.join(output_dir, "X_train.parquet"),
            "X_test": os.path.join(output_dir, "X_test.parquet"),
            "y_train": os.path.join(output_dir, "y_train.parquet"),
            "y_test": os.path.join(output_dir, "y_test.parquet"),
            "pipeline": pipeline_path,
            "label_encoder": encoder_path
        }
