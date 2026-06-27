"""
backend/ml/loader.py

Loads ML models, transformation parameters, label encoders, and training metrics
from pickle files at server startup. Exposes loaded models as module-level variables.
If any pickle file is missing or corrupted, triggers generate_mock_models fallback.
"""

import pickle
from typing import Dict, Any
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config
from backend.ml.generate_mock_models import generate_mock_models, MockClassifier

# Module-level variables exposed at server startup
PRIMARY_MODELS: Dict[str, Any] = {}
META_MODELS: Dict[str, Any] = {}
TRANSFORM_PARAMS: Dict[str, Any] = {}
LABEL_ENCODERS: Dict[str, Any] = {}
TRAINING_METRICS: Dict[str, Any] = {}


def _load_or_generate():
    global PRIMARY_MODELS, META_MODELS, TRANSFORM_PARAMS, LABEL_ENCODERS, TRAINING_METRICS
    
    paths = [
        config.PRIMARY_MODELS_PATH,
        config.META_MODELS_PATH,
        config.TRANSFORM_PARAMS_PATH,
        config.LABEL_ENCODERS_PATH,
        config.TRAINING_METRICS_PATH
    ]
    
    # Check if any path is missing
    missing = any(not p.exists() for p in paths)
    if missing:
        print("[loader] One or more ML pickle files missing. Running generate_mock_models fallback...")
        try:
            generate_mock_models()
        except Exception as e:
            print(f"[loader] Fallback generation failed: {e}")
            
    # Helper to load pickle safe
    def load_pkl(path: Path, default_val: Any) -> Any:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"[loader] Error loading {path.name}: {e}. Using fallback.")
        return default_val

    PRIMARY_MODELS = load_pkl(config.PRIMARY_MODELS_PATH, {})
    META_MODELS = load_pkl(config.META_MODELS_PATH, {})
    TRANSFORM_PARAMS = load_pkl(config.TRANSFORM_PARAMS_PATH, {})
    LABEL_ENCODERS = load_pkl(config.LABEL_ENCODERS_PATH, {})
    TRAINING_METRICS = load_pkl(config.TRAINING_METRICS_PATH, {})
    
    # Ensure all universe tickers have valid entries
    for ticker in config.TICKERS:
        if ticker not in PRIMARY_MODELS or PRIMARY_MODELS[ticker] is None:
            PRIMARY_MODELS[ticker] = MockClassifier(prob=0.58)
        if ticker not in META_MODELS or META_MODELS[ticker] is None:
            META_MODELS[ticker] = MockClassifier(prob=0.62)
        if ticker not in TRANSFORM_PARAMS or not TRANSFORM_PARAMS[ticker]:
            TRANSFORM_PARAMS[ticker] = {
                "differenced_cols": [],
                "rolling_params": {col: {"mean": 0.0, "std": 1.0} for col in config.FEATURE_COLS},
                "final_features": config.FEATURE_COLS
            }
        if ticker not in TRAINING_METRICS or not TRAINING_METRICS[ticker]:
            TRAINING_METRICS[ticker] = {"accuracy": 0.65, "f1": 0.62}


# Execute loading at startup
_load_or_generate()


def load_ml_models() -> Dict[str, Any]:
    """Returns a unified dictionary of all loaded ML components."""
    return {
        "primary": PRIMARY_MODELS,
        "meta": META_MODELS,
        "transform_params": TRANSFORM_PARAMS,
        "encoders": LABEL_ENCODERS,
        "training_metrics": TRAINING_METRICS
    }


if __name__ == "__main__":
    print("=== Loaded ML Models at Startup ===")
    print(f"Primary Models:   {list(PRIMARY_MODELS.keys())}")
    print(f"Meta Models:      {list(META_MODELS.keys())}")
    print(f"Transform Params: {list(TRANSFORM_PARAMS.keys())}")
    print(f"Label Encoders:   {list(LABEL_ENCODERS.keys())}")
    print(f"Training Metrics: {list(TRAINING_METRICS.keys())}")
