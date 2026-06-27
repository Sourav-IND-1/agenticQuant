import pickle
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score
import yfinance as yf
import numpy as np

TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA", "XOM", "JPM"]
FEATURE_COLS = ['RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower', 'ADX', 'MA5', 'MA20', 'MA50', 'Volume_change']

def add_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    sma5 = df['Close'].rolling(window=5).mean()
    std5 = df['Close'].rolling(window=5).std()
    df['BB_upper'] = sma5 + (2.0 * std5)
    df['BB_lower'] = sma5 - (2.0 * std5)

    high_diff = df['High'].diff()
    low_diff = df['Low'].diff()
    pos_dm = np.where((high_diff > 0) & (high_diff > -low_diff), high_diff, 0.0)
    neg_dm = np.where((low_diff < 0) & (-low_diff > high_diff), -low_diff, 0.0)
    
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    
    atr14 = tr.rolling(window=14).mean()
    pos_dm_series = pd.Series(pos_dm.flatten(), index=df.index).rolling(window=14).mean()
    neg_dm_series = pd.Series(neg_dm.flatten(), index=df.index).rolling(window=14).mean()
    
    plus_di14 = 100 * (pos_dm_series / atr14)
    minus_di14 = 100 * (neg_dm_series / atr14)
    dx = 100 * ((plus_di14 - minus_di14).abs() / (plus_di14 + minus_di14))
    df['ADX'] = dx.rolling(window=14).mean()

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Volume_change'] = df['Volume'].pct_change()
    
    return df.dropna()

def triple_barrier_labels(df, upper_mult=2, lower_mult=1, horizon=10):
    daily_vol = df['Close'].pct_change().rolling(60).std().bfill()
    labels = []
    for i in range(len(df) - horizon):
        entry = df['Close'].iloc[i]
        vol = daily_vol.iloc[i]
        upper = entry * (1 + upper_mult * vol)
        lower = entry * (1 - lower_mult * vol)
        label = 0  
        for j in range(1, horizon + 1):
            price = df['Close'].iloc[i + j]
            if price >= upper:
                label = 1
                break
            elif price <= lower:
                label = -1
                break
        labels.append(label)
    df = df.iloc[:-horizon].copy()
    df['label'] = labels
    return df

def main():
    print("Loading saved models and parameters...")
    with open("../backend/models/primary_models.pkl", "rb") as f: primary_models = pickle.load(f)
    with open("../backend/models/meta_models.pkl", "rb") as f: meta_models = pickle.load(f)
    with open("../backend/models/transform_params.pkl", "rb") as f: transform_params = pickle.load(f)
    with open("../backend/models/label_encoders.pkl", "rb") as f: label_encoders = pickle.load(f)

    print("\n--- Out-of-Sample Verification (2024 Data) ---")
    
    for ticker in TICKERS:
        if ticker not in primary_models: continue
        
        # Download specifically out of sample data (after our 2024 split date)
        df_raw = yf.download(ticker, start="2023-10-01", end="2024-12-31", progress=False)
        if isinstance(df_raw.columns, pd.MultiIndex):
            df_raw.columns = df_raw.columns.droplevel(1)
            
        df = add_indicators(df_raw.copy())
        df = triple_barrier_labels(df)
        
        # Keep only strict out of sample (2024+)
        df = df[df.index >= pd.Timestamp('2024-01-01')]
        
        if len(df) < 50:
            continue
            
        X_test = df[FEATURE_COLS].copy()
        
        # Apply strict Inference-time Transformations based on saved Pickles
        params = transform_params[ticker]
        
        for col in params["differenced_cols"]:
            X_test[col] = X_test[col].diff()
        X_test = X_test.dropna()
        
        for col, stats in params["rolling_params"].items():
            if col in X_test.columns:
                m, s = stats["mean"], stats["std"]
                X_test[col] = (X_test[col] - m) / s if s != 0 else 0
                
        # Drop features that were dropped in training
        X_test = X_test.drop(columns=[c for c in params["dropped_corr"] if c in X_test.columns])
        X_test = X_test.drop(columns=[c for c in params["dropped_vif"] if c in X_test.columns])
        X_test = X_test[params["final_features"]] # Enforce exact feature order
        
        # Align labels
        df_aligned = df.loc[X_test.index]
        y_true = label_encoders[ticker].transform(df_aligned['label'].values)
        
        # Predict using Primary Model
        primary = primary_models[ticker]
        y_pred = primary.predict(X_test)
        
        acc = accuracy_score(y_true, y_pred)
        print(f"\n{ticker} Primary Model Accuracy on 2024 unseen data: {acc*100:.2f}%")
        print(classification_report(y_true, y_pred, zero_division=0))

if __name__ == "__main__":
    main()
