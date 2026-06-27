import os
import yfinance as yf
import pickle
import pandas as pd
import numpy as np
from collections import Counter
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
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        data[ticker] = df
    return data

def add_indicators(df):
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands (5, 2.0)
    sma5 = df['Close'].rolling(window=5).mean()
    std5 = df['Close'].rolling(window=5).std()
    df['BB_upper'] = sma5 + (2.0 * std5)
    df['BB_lower'] = sma5 - (2.0 * std5)

    # ADX (14)
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

    # MAs and Volume
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

class PurgedKFold:
    def __init__(self, n_splits=5, purge_days=10, embargo_days=5):
        self.n_splits = n_splits
        self.purge_days = purge_days
        self.embargo_days = embargo_days

    def split(self, df):
        indices = np.arange(len(df))
        test_size = len(df) // self.n_splits
        for i in range(self.n_splits):
            test_start = i * test_size
            test_end = (i + 1) * test_size if i < self.n_splits - 1 else len(df)
            
            test_indices = indices[test_start:test_end]
            
            train_mask = np.ones(len(df), dtype=bool)
            train_mask[test_start:test_end] = False
            
            purge_start = max(0, test_start - self.purge_days)
            train_mask[purge_start:test_start] = False
            
            embargo_end = min(len(df), test_end + self.embargo_days)
            train_mask[test_end:embargo_end] = False
            
            yield indices[train_mask], test_indices

def run_pre_modeling_matrix(train, test, feature_cols):
    
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
        df_raw = data.get(ticker)
        if df_raw is None or df_raw.empty or len(df_raw) < 100:
            print(f"Skipping {ticker} due to insufficient data.")
            continue
            
        df = add_indicators(df_raw.copy())
        df = triple_barrier_labels(df)
        
        le = LabelEncoder()
        df['label'] = le.fit_transform(df['label'])
        label_encoders[ticker] = le
        
        cv = PurgedKFold(n_splits=5)
        fold_scores = []
        for train_idx, test_idx in cv.split(df):
            train_fold = df.iloc[train_idx]
            test_fold = df.iloc[test_idx]
            if len(train_fold) < 100 or len(test_fold) < 20: continue
            
            X_train, y_train, X_test, y_test, _ = run_pre_modeling_matrix(train_fold, test_fold, FEATURE_COLS)
            if len(X_train) == 0 or len(X_test) == 0: continue
            
            counts = Counter(y_train)
            scale = counts.get(1, 1) / max(counts.get(0, 1), 1)
            model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, scale_pos_weight=scale, random_state=42)
            model.fit(X_train, y_train)
            acc = (model.predict(X_test) == y_test).mean()
            fold_scores.append(acc)
            
        print(f"  CPCV Average Accuracy for {ticker}: {np.mean(fold_scores)*100:.2f}%")
        
        # Train FINAL model on ALL data minus last 5 days (embargo for safety)
        final_train = df.iloc[:-5]
        X_train, y_train, _, _, t_params = run_pre_modeling_matrix(final_train, final_train, FEATURE_COLS)
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
