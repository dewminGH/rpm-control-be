import os
import joblib
from django.conf import settings

_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        # Resolve model path relative to this file
        base_dir = os.path.dirname(os.path.dirname(__file__))  
        model_path = os.path.join(base_dir, "artifacts", "logistic_catboost_model_V4.pkl")
        _MODEL = joblib.load(model_path)
    return _MODEL
