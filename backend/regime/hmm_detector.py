import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def detect_market_regime(market_data: Dict[str, pd.DataFrame]) -> str:
    """Predicts current market regime (Bull, Neutral, Bear) using loaded HMM or heuristic fallback."""
    hmm_model = None
    regime_map = {0: "Bull", 1: "Neutral", 2: "Bear"}
    
    if config.HMM_MODEL_PATH.exists() and config.REGIME_MAP_PATH.exists():
        try:
            with open(config.HMM_MODEL_PATH, "rb") as f:
                hmm_model = pickle.load(f)
            with open(config.REGIME_MAP_PATH, "rb") as f:
                regime_map = pickle.load(f)
        except Exception as e:
            print(f"Warning loading HMM model: {e}")
            
    # Compute market proxy returns
    returns_list = []
    for df in market_data.values():
        if not df.empty and 'Close' in df.columns:
            returns_list.append(df['Close'].pct_change().dropna())
            
    if not returns_list:
        return "Neutral"
        
    market_ret = pd.DataFrame(returns_list).mean().dropna()
    if len(market_ret) < 10:
        return "Neutral"
        
    latest_ret = float(market_ret.iloc[-1])
    latest_vol = float(market_ret.tail(20).std())
    
    if hmm_model is not None and hasattr(hmm_model, "predict"):
        try:
            X_input = np.array([[latest_ret, latest_vol]])
            state = hmm_model.predict(X_input)[0]
            return regime_map.get(int(state), "Neutral")
        except Exception as e:
            pass
            
    # Heuristic fallback based on 20-day cumulative return
    cum_20 = float((1 + market_ret.tail(20)).prod() - 1)
    if cum_20 > 0.015:
        return "Bull"
    elif cum_20 < -0.015:
        return "Bear"
    return "Neutral"

if __name__ == "__main__":
    from data.market_data import get_live_market_data
    data = get_live_market_data()
    regime = detect_market_regime(data)
    print(f"Detected Market Regime: {regime}")
