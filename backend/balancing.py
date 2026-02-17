import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE, ADASYN, RandomOverSampler, SMOTENC
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, EditedNearestNeighbours
from imblearn.combine import SMOTETomek, SMOTEENN

class BalancingPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.technique = config.get('technique', 'None')
        self.params = config.get('params', {})
        self.resampler = None

    def apply_balancing(self, X_train: pd.DataFrame, y_train: pd.Series, categorical_features_indices: Optional[list] = None) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
        """
        Applies the configured balancing technique to the training data.
        
        Args:
            X_train: Training features (DataFrame or numpy array)
            y_train: Training labels
            categorical_features_indices: List of indices for categorical features (required for SMOTENC)
            
        Returns:
            Tuple containing:
            - X_train_resampled
            - y_train_resampled
            - metadata (before/after distribution)
        """
        
        # 1. Calculate Initial Distribution
        before_dist = y_train.value_counts().to_dict()
        # Ensure keys are strings for JSON serialization
        before_dist = {str(k): int(v) for k, v in before_dist.items()}
        
        # 2. Select Resampler
        if self.technique == 'None':
            return X_train, y_train, {
                "before": before_dist,
                "after": before_dist,
                "technique": "None"
            }
            
        # Get minority count for safety checks
        counts = y_train.value_counts()
        min_class_count = counts.min()
        
        self.resampler = self._get_resampler_with_checks(min_class_count, categorical_features_indices)
        
        if not self.resampler:
             return X_train, y_train, {
                "before": before_dist,
                "after": before_dist,
                "technique": "None (Failed to initialize)"
            }

        # 3. Fit and Resample
        # Note: We don't use Pipeline here for the *act* of resampling data directly 
        # because we want to return the resampled data for visualization/saving.
        # However, for the final model pipeline, we would wrap this in imblearn.pipeline.
        
        try:
            X_resampled, y_resampled = self.resampler.fit_resample(X_train, y_train)
        except Exception as e:
            print(f"Balancing failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to original
            return X_train, y_train, {
                "before": before_dist,
                "after": before_dist,
                "error": str(e)
            }
            
        # 4. Calculate Final Distribution
        after_dist = y_resampled.value_counts().to_dict()
        after_dist = {str(k): int(v) for k, v in after_dist.items()}
        
        return X_resampled, y_resampled, {
            "before": before_dist,
            "after": after_dist,
            "technique": self.technique
        }

    def _get_resampler(self, categorical_indices: Optional[list] = None):
        # Helper to parse neighbors safely
        # We need access to X or at least n_samples to adjust k.
        # But this method is called inside apply_balancing where X_train is available 
        # but NOT passed to _get_resampler yet.
        # Let's refactor apply_balancing to pass n_samples to _get_resampler
        return None

    def _get_resampler_with_checks(self, n_samples_minority: int, categorical_indices: Optional[list] = None):
        
        # Helper: Adjust k if dataset is tiny
        def get_safe_k(param_name='k_neighbors', default=5):
            k = int(self.params.get(param_name, default))
            # k_neighbors must be < n_samples_minority
            if k >= n_samples_minority:
                new_k = max(1, n_samples_minority - 1)
                print(f"Warning: {param_name}={k} >= n_samples_minority={n_samples_minority}. Adjusting to {new_k}")
                return new_k
            return k

        strategy = self.params.get('sampling_strategy', 'auto')
        
        # Category A: Oversampling
        if self.technique == 'SMOTE':
            return SMOTE(k_neighbors=get_safe_k('k_neighbors'), sampling_strategy=strategy, random_state=42)
            
        elif self.technique == 'ADASYN':
             return ADASYN(n_neighbors=get_safe_k('n_neighbors'), sampling_strategy=strategy, random_state=42)
             
        elif self.technique == 'RandomOverSampler':
            return RandomOverSampler(sampling_strategy=strategy, random_state=42)
            
        # Category B: Undersampling
        elif self.technique == 'RandomUnderSampler':
            replacement = bool(self.params.get('replacement', False))
            return RandomUnderSampler(sampling_strategy=strategy, replacement=replacement, random_state=42)
            
        elif self.technique == 'TomekLinks':
            return TomekLinks(sampling_strategy=strategy) 
            
        elif self.technique == 'ENN': # EditedNearestNeighbours
            # ENN uses n_neighbors to check surroundings. 
            # If n_samples is small, we might not find enough neighbors? 
            # ENN removes samples if their neighbors disagree.
            # We can use the whole dataset size here for safety check, but n_neighbors usually refers to local neighborhood.
            # Hard to check minority count vs n_neighbors for ENN as it looks at all classes.
            # We'll just use the param as is for now or cap it at reasonable number if needed.
            return EditedNearestNeighbours(sampling_strategy=strategy, n_neighbors=int(self.params.get('n_neighbors', 3)))

        # Category C: Hybrids
        elif self.technique == 'SMOTETomek':
             # SMOTE part needs safety check
             smote = SMOTE(k_neighbors=get_safe_k('k_neighbors'), sampling_strategy=strategy, random_state=42)
             return SMOTETomek(smote=smote, random_state=42)
             
        elif self.technique == 'SMOTEENN':
             smote = SMOTE(k_neighbors=get_safe_k('k_neighbors'), sampling_strategy=strategy, random_state=42)
             return SMOTEENN(smote=smote, random_state=42)

        return None
