"""
backend/regime/hmm_detector.py

Macroeconomic regime detection via Hidden Markov Models (HMM).
Loads pre-trained HMM model and regime map at server startup.
Computes daily returns and rolling 20-day volatility from SPY market data cache,
predicts the current hidden state, maps it deterministically (Bear/Neutral/Bull),
and returns the regime along with state confidence.
"""

import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config

# Module-level variables loaded at startup
HMM_MODEL: Any = None
REGIME_MAP: Dict[int, str] = {0: "Bull", 1: "Neutral", 2: "Bear"}


def _load_startup():
    global HMM_MODEL, REGIME_MAP

    if config.HMM_MODEL_PATH.exists():
        try:
            with open(config.HMM_MODEL_PATH, "rb") as f:
                HMM_MODEL = pickle.load(f)
        except Exception as e:
            print(f"[hmm_detector] Error loading HMM model: {e}")

    if config.REGIME_MAP_PATH.exists():
        try:
            with open(config.REGIME_MAP_PATH, "rb") as f:
                REGIME_MAP = pickle.load(f)
        except Exception as e:
            print(f"[hmm_detector] Error loading regime map: {e}")

    # Ensure deterministic mapping fallback based on state means if model exists
    if HMM_MODEL is not None and hasattr(HMM_MODEL, "means_"):
        try:
            state_means = HMM_MODEL.means_[:, 0]
            order = np.argsort(state_means)
            REGIME_MAP = {
                int(order[0]): "Bear",
                int(order[1]): "Neutral",
                int(order[2]): "Bull"
            }
        except Exception:
            pass


# Execute startup load
_load_startup()


def detect_regime(market_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Detects current market regime using HMM on SPY returns and rolling volatility.

    Returns:
        {
          "regime": "Bull" | "Neutral" | "Bear",
          "state_id": int,
          "confidence": float
        }
    """
    spy_df = pd.DataFrame()

    # 1. Pull SPY data from provided market_data or from market_data cache
    if market_data is not None and "SPY" in market_data:
        spy_df = market_data["SPY"]
    else:
        if config.MARKET_DATA_CACHE_PATH.exists():
            try:
                with open(config.MARKET_DATA_CACHE_PATH, "rb") as f:
                    cache = pickle.load(f)
                    if isinstance(cache, dict) and "SPY" in cache:
                        spy_df = cache["SPY"]
            except Exception:
                pass

    # If SPY is empty or not present, construct market proxy from available tickers
    if spy_df.empty:
        if market_data:
            prices_list = [df["Close"] for df in market_data.values() if not df.empty and "Close" in df.columns]
            if prices_list:
                proxy_close = pd.concat(prices_list, axis=1).mean(axis=1)
                spy_df = pd.DataFrame({"Close": proxy_close})

    if spy_df.empty or "Close" not in spy_df.columns or len(spy_df) < 25:
        # Fallback default if insufficient data
        return {"regime": "Neutral", "state_id": 1, "confidence": 0.65}

    # Take last 60 days (or more to ensure valid rolling vol)
    close_series = spy_df["Close"].squeeze().tail(85)

    # 2. Compute daily returns
    returns = close_series.pct_change()

    # 3. Compute 20-day rolling volatility
    volatility = returns.rolling(window=20).std()

    # Drop NA rows resulting from pct_change and rolling std
    valid_data = pd.DataFrame({
        "returns": returns,
        "volatility": volatility
    }).dropna()

    if valid_data.empty or len(valid_data) == 0:
        return {"regime": "Neutral", "state_id": 1, "confidence": 0.65}

    # Filter to last 60 days
    last_60 = valid_data.tail(60)

    # 4. Stack as 2-column feature matrix: [returns, volatility]
    feature_matrix = last_60[["returns", "volatility"]].values

    # 5. Run hmm_model.predict() on feature matrix
    if HMM_MODEL is not None and hasattr(HMM_MODEL, "predict"):
        try:
            states = HMM_MODEL.predict(feature_matrix)
            # 6. Take most recent predicted state
            state_id = int(states[-1])

            # Compute confidence if predict_proba is available
            confidence = 0.85
            if hasattr(HMM_MODEL, "predict_proba"):
                probs = HMM_MODEL.predict_proba(feature_matrix)
                confidence = round(float(np.max(probs[-1])), 4)

            # 7. Map state to regime using regime_map
            regime = REGIME_MAP.get(state_id, "Neutral")
            return {
                "regime": regime,
                "state_id": state_id,
                "confidence": confidence
            }
        except Exception as e:
            print(f"[hmm_detector] Prediction error: {e}")

    # Heuristic fallback if model unavailable or prediction fails
    recent_ret = float(last_60["returns"].mean())
    if recent_ret > 0.0005:
        return {"regime": "Bull", "state_id": 0, "confidence": 0.70}
    elif recent_ret < -0.0005:
        return {"regime": "Bear", "state_id": 1, "confidence": 0.70}
    return {"regime": "Neutral", "state_id": 2, "confidence": 0.70}


def detect_market_regime(market_data: Optional[Dict[str, pd.DataFrame]] = None) -> str:
    """Backward-compatible wrapper returning the regime string ('Bull', 'Neutral', 'Bear') for main.py."""
    res = detect_regime(market_data)
    return res.get("regime", "Neutral")


if __name__ == "__main__":
    print("=== Testing HMM Detector ===")
    res = detect_regime()
    print("detect_regime() result:", res)
    print("detect_market_regime() string:", detect_market_regime())
