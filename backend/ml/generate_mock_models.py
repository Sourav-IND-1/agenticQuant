import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path so config can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    pass

class MockClassifier:
    """Fallback classifier if scikit-learn is unavailable or for lightweight mocking."""
    def __init__(self, prob=0.6):
        self.prob = prob
        self.classes_ = np.array([0, 1])

    def predict_proba(self, X):
        n = len(X)
        # return array of [1-prob, prob] with slight random variation
        noise = np.random.uniform(-0.05, 0.05, size=(n, 1))
        p = np.clip(self.prob + noise, 0.1, 0.9)
        return np.hstack([1 - p, p])

    def predict(self, X):
        probs = self.predict_proba(X)[:, 1]
        return (probs > 0.5).astype(int)

class MockHMM:
    """Mock Hidden Markov Model for regime detection."""
    def __init__(self, n_components=3):
        self.n_components = n_components

    def predict(self, X):
        # Return regime 0 (Bull), 1 (Neutral), or 2 (Bear) based on return drift
        regimes = []
        for row in X:
            ret = row[0] if len(row) > 0 else 0
            if ret > 0.002:
                regimes.append(0) # Bull
            elif ret < -0.002:
                regimes.append(2) # Bear
            else:
                regimes.append(1) # Neutral
        return np.array(regimes)

def generate_mock_data():
    print("Generating synthetic market data cache...")
    dates = pd.date_range(end=datetime.today(), periods=500, freq='B')
    market_data = {}
    
    base_prices = {
        "AAPL": 180.0, "MSFT": 420.0, "GOOGL": 170.0, 
        "NVDA": 120.0, "XOM": 115.0, "JPM": 200.0
    }
    
    for ticker in config.TICKERS:
        start_price = base_prices.get(ticker, 100.0)
        returns = np.random.normal(0.0008, 0.015, len(dates))
        price_series = start_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame(index=dates)
        df['Close'] = price_series
        df['Open'] = df['Close'] * np.random.uniform(0.99, 1.01, len(dates))
        df['High'] = np.maximum(df['Open'], df['Close']) * np.random.uniform(1.00, 1.015, len(dates))
        df['Low'] = np.minimum(df['Open'], df['Close']) * np.random.uniform(0.985, 1.00, len(dates))
        df['Volume'] = np.random.randint(10000000, 50000000, len(dates))
        
        market_data[ticker] = df
        
    with open(config.MARKET_DATA_CACHE_PATH, "wb") as f:
        pickle.dump(market_data, f)
    print(f"Saved market data cache to {config.MARKET_DATA_CACHE_PATH}")

def generate_mock_models():
    print("Generating synthetic ML models and parameters...")
    primary_models = {}
    meta_models = {}
    transform_params = {}
    label_encoders = {}
    training_metrics = {}
    
    X_dummy = np.random.randn(100, len(config.FEATURE_COLS))
    y_dummy = np.random.choice([0, 1], size=100)
    
    for ticker in config.TICKERS:
        try:
            clf_primary = GradientBoostingClassifier(n_estimators=20, random_state=42)
            clf_primary.fit(X_dummy, y_dummy)
            clf_meta = GradientBoostingClassifier(n_estimators=10, random_state=42)
            clf_meta.fit(clf_primary.predict_proba(X_dummy), y_dummy)
            le = LabelEncoder()
            le.fit([0, 1])
        except Exception:
            clf_primary = MockClassifier(prob=0.58)
            clf_meta = MockClassifier(prob=0.62)
            le = None
            
        primary_models[ticker] = clf_primary
        meta_models[ticker] = clf_meta
        label_encoders[ticker] = le
        
        transform_params[ticker] = {
            "differenced_cols": [],
            "rolling_params": {col: {"mean": 0.0, "std": 1.0} for col in config.FEATURE_COLS},
            "dropped_corr": [],
            "dropped_vif": [],
            "dropped_mi": [],
            "final_features": config.FEATURE_COLS,
            "snr": {col: 1.2 for col in config.FEATURE_COLS}
        }
        training_metrics[ticker] = {"accuracy": 0.65, "f1": 0.62}
        
    with open(config.PRIMARY_MODELS_PATH, "wb") as f:
        pickle.dump(primary_models, f)
    with open(config.META_MODELS_PATH, "wb") as f:
        pickle.dump(meta_models, f)
    with open(config.TRANSFORM_PARAMS_PATH, "wb") as f:
        pickle.dump(transform_params, f)
    with open(config.LABEL_ENCODERS_PATH, "wb") as f:
        pickle.dump(label_encoders, f)
    with open(config.TRAINING_METRICS_PATH, "wb") as f:
        pickle.dump(training_metrics, f)
        
    hmm_model = MockHMM(n_components=3)
    regime_map = {0: "Bull", 1: "Neutral", 2: "Bear"}
    
    with open(config.HMM_MODEL_PATH, "wb") as f:
        pickle.dump(hmm_model, f)
    with open(config.REGIME_MAP_PATH, "wb") as f:
        pickle.dump(regime_map, f)
        
    print("Saved all mock models and regime maps successfully!")

if __name__ == "__main__":
    generate_mock_data()
    generate_mock_models()
