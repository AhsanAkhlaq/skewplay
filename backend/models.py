from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Advanced Models & Imbalance
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
from imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier, RUSBoostClassifier
class ModelFactory:
    @staticmethod
    def get_model(algorithm: str, params: Dict[str, Any]):
        """
        Factory method to initialize a model based on algorithm name and parameters.
        """
        # --- Category A: Interpretable ---
        if algorithm == 'LogisticRegression':
            return LogisticRegression(C=float(params.get('C', 1.0)), penalty=params.get('penalty', 'l2'), solver='liblinear' if params.get('penalty') == 'l1' else 'lbfgs', class_weight=params.get('class_weight'), max_iter=1000)
        if algorithm == 'RandomForest':
            return RandomForestClassifier(n_estimators=int(params.get('n_estimators', 100)), max_depth=int(params.get('max_depth', 0)) or None, class_weight=params.get('class_weight'), random_state=42)
            
        # --- Category B: Gradient Boosting ---
        if algorithm == 'XGBoost':
            return xgb.XGBClassifier(n_estimators=int(params.get('n_estimators', 100)), learning_rate=float(params.get('learning_rate', 0.1)), max_depth=int(params.get('max_depth', 6)), scale_pos_weight=float(params.get('scale_pos_weight', 1.0)), random_state=42)
        if algorithm == 'LightGBM':
            return lgb.LGBMClassifier(n_estimators=int(params.get('n_estimators', 100)), learning_rate=float(params.get('learning_rate', 0.1)), max_depth=int(params.get('max_depth', -1)), class_weight=params.get('class_weight'), random_state=42)
        if algorithm == 'CatBoost':
            aw = params.get('auto_class_weights')
            # CatBoost handles multiclass automatically, but verbose=0 is good.
            return CatBoostClassifier(iterations=int(params.get('n_estimators', 100)), learning_rate=float(params.get('learning_rate', 0.1)), depth=int(params.get('max_depth', 6)), auto_class_weights=aw if aw != 'None' else None, random_seed=42, verbose=0)
            
        # --- Category C: Imbalance-Specific Ensembles ---
        if algorithm == 'BalancedRandomForest':
            return BalancedRandomForestClassifier(n_estimators=int(params.get('n_estimators', 100)), max_depth=int(params.get('max_depth', 0)) or None, replacement=bool(params.get('replacement', False)), random_state=42)
        if algorithm == 'EasyEnsemble':
            return EasyEnsembleClassifier(n_estimators=int(params.get('n_estimators', 10)), random_state=42)
        if algorithm == 'RUSBoost':
            return RUSBoostClassifier(n_estimators=int(params.get('n_estimators', 50)), learning_rate=float(params.get('learning_rate', 1.0)), random_state=42)
            
        # --- Category D: Distance & Margin ---
        if algorithm == 'SVM':
            return SVC(C=float(params.get('C', 1.0)), kernel=params.get('kernel', 'rbf'), class_weight=params.get('class_weight'), probability=True)
        if algorithm == 'KNN':
            return KNeighborsClassifier(n_neighbors=int(params.get('n_neighbors', 5)), weights=params.get('weights', 'uniform'))
            
        # Default
        return RandomForestClassifier()
