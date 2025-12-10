import pandas as pd
import numpy as np

def sanitize_for_json(obj):
    """
    Recursively clean an object to ensure it is JSON serializable.
    Handles NaN, Infinity, and numpy types.
    """
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif hasattr(obj, 'item'): # Handle numpy scalars (np.float64, np.int64, etc.)
        val = obj.item()
        if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
            return None
        return val
    elif pd.isna(obj): # Handle pandas NaT/NaN
        return None
    return obj
