import sys
import os
sys.path.append(os.getcwd() + '/backend')
import pandas as pd
import numpy as np
import json
from json_utils import sanitize_for_json
from analysis import ImbalanceAnalyzer

df = pd.DataFrame({'f1': [1.0, np.nan, 3.0], 'f2': [4.0, 5.0, 6.0]})
y = pd.Series([1, 1, 0])

analyzer = ImbalanceAnalyzer()
res = analyzer.calculate_metrics(df, y)
sanitized = sanitize_for_json(res)
print('Keys type:', type(list(sanitized['distribution'].keys())[0]))
print(sanitized)
try:
    print(json.dumps(sanitized))
except Exception as e:
    print('JSON ERROR:', e)
