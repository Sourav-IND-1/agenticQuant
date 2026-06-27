import os
from hmmlearn import hmm
import numpy as np
import yfinance as yf
import pickle
import pandas as pd

import time

def main():
    print("Fetching ^NSEI (Nifty 50) data for regime detection...")
    nsei = None
    for attempt in range(5):
        nsei = yf.download("^NSEI", start="2008-01-01", end="2024-12-31")
        if not nsei.empty:
            break
        print("yfinance failed to download ^NSEI. Retrying in 2 seconds...")
        time.sleep(2)
        
    if nsei is None or nsei.empty:
        print("Failed to download ^NSEI data after 5 attempts.")
        return
        
    if isinstance(nsei.columns, pd.MultiIndex):
        nsei.columns = nsei.columns.droplevel(1)
        
    # Calculate features
    returns = nsei['Close'].pct_change().dropna()
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
