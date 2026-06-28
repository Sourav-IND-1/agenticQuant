import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    # Explicitly load backend/.env with override to ensure .env values win over system env vars
    _env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent

# User-requested directory definitions
MODEL_DIR = "backend/models/"
CACHE_DIR = "backend/cache/"

# Compatible Path objects for filesystem operations
MODELS_DIR = BASE_DIR / "models"
CACHE_PATH_DIR = BASE_DIR / "cache"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_PATH_DIR.mkdir(parents=True, exist_ok=True)

# Core Asset Universe — Nifty 50 (NSE India)
TICKERS = [
    # IT / Technology
    "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
    # Banking & Finance
    "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS",
    "INDUSINDBK.NS", "HDFCLIFE.NS", "SBILIFE.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
    # Energy & Conglomerate
    "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "POWERGRID.NS", "NTPC.NS", "COALINDIA.NS",
    # Consumer & FMCG
    "HINDUNILVR.NS", "ITC.NS", "BRITANNIA.NS", "NESTLEIND.NS", "TATACONSUM.NS",
    # Pharma & Healthcare
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS",
    # Auto & Engineering
    "MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "M&M.NS",
    # Metals & Materials
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "GRASIM.NS", "ULTRACEMCO.NS",
    # Telecom
    "BHARTIARTL.NS",
    # Infrastructure & Defence
    "LT.NS", "ADANIENT.NS", "ADANIPORTS.NS", "BEL.NS",
    # Luxury & Retail
    "TITAN.NS", "TRENT.NS",
    # Paint
    "ASIANPAINT.NS",
]

# Financial Constants (India-adjusted)
RISK_FREE_RATE = 0.065   # RBI repo rate ~6.5%
MARKET_PREMIUM = 0.05    # India equity risk premium ~5%

# Model File Paths
PRIMARY_MODELS_PATH = MODELS_DIR / "primary_models.pkl"
META_MODELS_PATH = MODELS_DIR / "meta_models.pkl"
TRANSFORM_PARAMS_PATH = MODELS_DIR / "transform_params.pkl"
LABEL_ENCODERS_PATH = MODELS_DIR / "label_encoders.pkl"
TRAINING_METRICS_PATH = MODELS_DIR / "training_metrics.pkl"
HMM_MODEL_PATH = MODELS_DIR / "hmm_model.pkl"
REGIME_MAP_PATH = MODELS_DIR / "regime_map.pkl"

# Cache File Paths
MARKET_DATA_CACHE_PATH = CACHE_PATH_DIR / "market_data.pkl"

# API Keys & Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", 8000))

# Technical Indicator Feature Columns
FEATURE_COLS = [
    'RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower', 
    'ADX', 'MA5', 'MA20', 'MA50', 'Volume_change'
]
