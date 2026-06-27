import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Core Asset Universe
TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA", "XOM", "JPM"]

# Model File Paths
PRIMARY_MODELS_PATH = MODELS_DIR / "primary_models.pkl"
META_MODELS_PATH = MODELS_DIR / "meta_models.pkl"
TRANSFORM_PARAMS_PATH = MODELS_DIR / "transform_params.pkl"
LABEL_ENCODERS_PATH = MODELS_DIR / "label_encoders.pkl"
TRAINING_METRICS_PATH = MODELS_DIR / "training_metrics.pkl"
HMM_MODEL_PATH = MODELS_DIR / "hmm_model.pkl"
REGIME_MAP_PATH = MODELS_DIR / "regime_map.pkl"

# Cache File Paths
MARKET_DATA_CACHE_PATH = CACHE_DIR / "market_data.pkl"

# API Keys & Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", 8000))

# Technical Indicator Feature Columns
FEATURE_COLS = [
    'RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower', 
    'ADX', 'MA5', 'MA20', 'MA50', 'Volume_change'
]
