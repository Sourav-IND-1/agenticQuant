import os
from hmmlearn import hmm
import numpy as np
import yfinance as yf
import pickle
import pandas as pd

import time

def main():
    print("Fetching SPY data for regime detection...")
    spy = None
    for attempt in range(5):
        spy = yf.download("SPY", start="2008-01-01", end="2024-12-31")
        if not spy.empty:
            break
        print("yfinance failed to download SPY. Retrying in 2 seconds...")
        time.sleep(2)
        
    if spy is None or spy.empty:
        print("Failed to download SPY data after 5 attempts.")
        return
        
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.droplevel(1)
        
    # Calculate features
    returns = spy['Close'].pct_change().dropna()
    volatility = returns.rolling(20).std().dropna()

    # Align data lengths
    returns = returns.loc[volatility.index]
    features = np.column_stack([returns, volatility])

    print("Training HMM with 3 components...")
    model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100, random_state=42)
    model.fit(features)

    # Map the hidden states to human readable regimes
    state_means = model.means_[:, 0]
    order = np.argsort(state_means)
    
    # Lower mean return = Bear, Middle = Neutral, Highest = Bull
    regime_map = {
        int(order[0]): "Bear",
        int(order[1]): "Neutral",
        int(order[2]): "Bull"
    }

    print(f"Detected Regime Mapping: {regime_map}")

    # Ensure models directory exists
    os.makedirs("../backend/models", exist_ok=True)
    
    print("Saving HMM artifacts to backend/models...")
    with open("../backend/models/hmm_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("../backend/models/regime_map.pkl", "wb") as f:
        pickle.dump(regime_map, f)
        
    print("HMM training complete.")

if __name__ == "__main__":
    main()
