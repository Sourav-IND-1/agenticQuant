import os
import yfinance as yf
import pickle
import pandas as pd
import numpy as np
from collections import Counter
import pandas_ta as ta
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.feature_selection import mutual_info_classif
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# Ensure models directory exists for output
os.makedirs("../backend/models", exist_ok=True)
os.makedirs("../backend/cache", exist_ok=True)

TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA", "XOM", "JPM"]
FEATURE_COLS = ['RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower', 'ADX', 'MA5', 'MA20', 'MA50', 'Volume_change']

def fetch_data():
    data = {}
    for ticker in TICKERS:
        df = yf.download(ticker, start="2008-01-01", end="2024-12-31")
        data[ticker] = df
    return data

def add_indicators(df):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    bb = ta.bbands(df['Close'])
    df['BB_upper'] = bb['BBU_5_2.0']
    df['BB_lower'] = bb['BBL_5_2.0']
    df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
    df['MA5'] = ta.sma(df['Close'], length=5)
    df['MA20'] = ta.sma(df['Close'], length=20)
    df['MA50'] = ta.sma(df['Close'], length=50)
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
        label = 0  # default hold
        
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

def check_stationarity(X_train):
    differenced_cols = []
    for col in X_train.columns:
        if adfuller(X_train[col].dropna())[1] > 0.05:
            X_train[col] = X_train[col].diff()
            differenced_cols.append(col)
    return X_train.dropna(), differenced_cols

def rolling_zscore(X_train, window=60):
    rolling_params = {}
    for col in X_train.columns:
        mean = X_train[col].rolling(window).mean()
        std = X_train[col].rolling(window).std()
        rolling_params[col] = {"mean": float(mean.iloc[-1]), "std": float(std.iloc[-1])}
        X_train[col] = (X_train[col] - mean) / std
    return X_train.dropna(), rolling_params

def remove_correlated_features(X_train, threshold=0.95):
    corr = X_train.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [c for c in upper.columns if any(upper[c] > threshold)]
    return X_train.drop(columns=to_drop), to_drop

def remove_vif_features(X_train, threshold=10):
    dropped = []
    while True:
        vif_data = pd.DataFrame()
        vif_data["feature"] = X_train.columns
        vif_data["VIF"] = [variance_inflation_factor(X_train.values, i) for i in range(X_train.shape[1])]
        max_vif = vif_data["VIF"].max()
        if max_vif < threshold: break
        worst = vif_data.loc[vif_data["VIF"].idxmax(), "feature"]
        X_train = X_train.drop(columns=[worst])
        dropped.append(worst)
    return X_train, dropped

def mutual_information_filter(X_train, y_train, threshold=0.01):
    mi = mutual_info_classif(X_train.fillna(0), y_train, random_state=42)
    mi_df = pd.DataFrame({"feature": X_train.columns, "mi_score": mi}).sort_values("mi_score", ascending=False)
    top_features = mi_df[mi_df["mi_score"] > threshold]["feature"].tolist()
    dropped = [f for f in X_train.columns if f not in top_features]
    return X_train[top_features], dropped, mi_df

def snr_check(X_train):
    return {col: abs(X_train[col].mean()) / X_train[col].std() if X_train[col].std() != 0 else 0 for col in X_train.columns}

def purge_embargo_split(df, split_date='2024-01-01', purge_days=10, embargo_days=5):
    split = pd.Timestamp(split_date)
    train = df[df.index < split - pd.Timedelta(days=purge_days)]
    test = df[df.index >= split + pd.Timedelta(days=embargo_days)]
    return train, test

def run_pre_modeling_matrix(df, ticker, feature_cols, split_date='2024-01-01'):
    train, test = purge_embargo_split(df, split_date)
    
    X_train = train[feature_cols].copy()
    y_train = train['label'].values
    X_test = test[feature_cols].copy()
    y_test = test['label'].values
    
    X_train, differenced_cols = check_stationarity(X_train)
    for col in differenced_cols: X_test[col] = X_test[col].diff()
    X_test = X_test.dropna()
    
    X_train, rolling_params = rolling_zscore(X_train)
    for col in X_train.columns:
        if col in rolling_params:
            m, s = rolling_params[col]["mean"], rolling_params[col]["std"]
            X_test[col] = (X_test[col] - m) / s if s != 0 else 0
    X_test = X_test.dropna()
    
    X_train, dropped_corr = remove_correlated_features(X_train)
    X_test = X_test.drop(columns=[c for c in dropped_corr if c in X_test.columns])
    
    X_train, dropped_vif = remove_vif_features(X_train)
    X_test = X_test.drop(columns=[c for c in dropped_vif if c in X_test.columns])
    
    X_train, dropped_mi, mi_df = mutual_information_filter(X_train, y_train[:len(X_train)])
    X_test = X_test[X_train.columns]
    
    snr = snr_check(X_train)
    
    transform_params = {
        "differenced_cols": differenced_cols,
        "rolling_params": rolling_params,
        "dropped_corr": dropped_corr,
        "dropped_vif": dropped_vif,
        "dropped_mi": dropped_mi,
        "final_features": X_train.columns.tolist(),
        "snr": snr
    }
    return X_train, y_train[-len(X_train):], X_test, y_test[-len(X_test):], transform_params

def main():
    print("Fetching data...")
    data = fetch_data()
    
    primary_models, meta_models, transform_params_all, label_encoders, metrics_all = {}, {}, {}, {}, {}

    for ticker in TICKERS:
        print(f"Training XGBoost for {ticker}...")
        df = add_indicators(data[ticker].copy())
        df = triple_barrier_labels(df)
        
        le = LabelEncoder()
        df['label'] = le.fit_transform(df['label'])
        label_encoders[ticker] = le
        
        X_train, y_train, X_test, y_test, t_params = run_pre_modeling_matrix(df, ticker, FEATURE_COLS)
        transform_params_all[ticker] = t_params
        
        counts = Counter(y_train)
        scale = counts.get(1, 1) / max(counts.get(0, 1), 1)
        
        primary = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, scale_pos_weight=scale, random_state=42)
        primary.fit(X_train, y_train)
        
        meta = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
        meta.fit(primary.predict_proba(X_train), y_train)
        
        primary_models[ticker], meta_models[ticker] = primary, meta

    # Export Pickles directly into the backend directory
    print("Saving artifacts to backend/models...")
    with open("../backend/models/primary_models.pkl", "wb") as f: pickle.dump(primary_models, f)
    with open("../backend/models/meta_models.pkl", "wb") as f: pickle.dump(meta_models, f)
    with open("../backend/models/transform_params.pkl", "wb") as f: pickle.dump(transform_params_all, f)
    with open("../backend/models/label_encoders.pkl", "wb") as f: pickle.dump(label_encoders, f)
    print("Training pipeline complete.")

if __name__ == "__main__":
    main()
