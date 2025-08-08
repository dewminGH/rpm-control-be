import os
import joblib

_MODEL = None

def get_model():
    """
    load model v4 -cat boost
    """
    global _MODEL
    if _MODEL is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_dir, "artifacts", "logistic_catboost_model_V4.pkl")
        _MODEL = joblib.load(model_path)
    return _MODEL
