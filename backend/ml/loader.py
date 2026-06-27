import pickle
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from ml.generate_mock_models import MockClassifier

def load_ml_models() -> Dict[str, Any]:
    """Loads primary models, meta models, transform parameters, and encoders from pickle storage."""
    models = {
        "primary": {},
        "meta": {},
        "transform_params": {},
        "encoders": {}
    }
    
    # Load Primary Models
    if config.PRIMARY_MODELS_PATH.exists():
        try:
            with open(config.PRIMARY_MODELS_PATH, "rb") as f:
                models["primary"] = pickle.load(f)
        except Exception as e:
            print(f"Error loading primary models: {e}")
            
    # Load Meta Models
    if config.META_MODELS_PATH.exists():
        try:
            with open(config.META_MODELS_PATH, "rb") as f:
                models["meta"] = pickle.load(f)
        except Exception as e:
            print(f"Error loading meta models: {e}")
            
    # Load Transform Params
    if config.TRANSFORM_PARAMS_PATH.exists():
        try:
            with open(config.TRANSFORM_PARAMS_PATH, "rb") as f:
                models["transform_params"] = pickle.load(f)
        except Exception as e:
            print(f"Error loading transform params: {e}")
            
    # Load Label Encoders
    if config.LABEL_ENCODERS_PATH.exists():
        try:
            with open(config.LABEL_ENCODERS_PATH, "rb") as f:
                models["encoders"] = pickle.load(f)
        except Exception as e:
            print(f"Error loading label encoders: {e}")
            
    # Ensure every ticker has fallback models if missing
    for ticker in config.TICKERS:
        if ticker not in models["primary"]:
            models["primary"][ticker] = MockClassifier(prob=0.58)
        if ticker not in models["meta"]:
            models["meta"][ticker] = MockClassifier(prob=0.62)
        if ticker not in models["transform_params"]:
            models["transform_params"][ticker] = {
                "differenced_cols": [],
                "rolling_params": {col: {"mean": 0.0, "std": 1.0} for col in config.FEATURE_COLS},
                "final_features": config.FEATURE_COLS
            }
            
    return models

if __name__ == "__main__":
    m = load_ml_models()
    print(f"Loaded models for tickers: {list(m['primary'].keys())}")
