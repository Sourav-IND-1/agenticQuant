import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

try:
    import yfinance as yf
except ImportError:
    yf = None

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute technical indicators using pure pandas/numpy to avoid dependency issues."""
    df = df.copy()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14, min_periods=1).mean()
    rs = gain / loss.replace(0, 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands (5, 2.0 matching training notebook)
    sma5 = df['Close'].rolling(window=5, min_periods=1).mean()
    std5 = df['Close'].rolling(window=5, min_periods=1).std().fillna(0)
    df['BB_upper'] = sma5 + 2 * std5
    df['BB_lower'] = sma5 - 2 * std5
    
    # ADX (14)
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    up_move = df['High'] - df['High'].shift()
    down_move = df['Low'].shift() - df['Low']
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    tr14 = pd.Series(tr, index=df.index).rolling(window=14, min_periods=1).sum().replace(0, 1e-10)
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(window=14, min_periods=1).sum() / tr14)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(window=14, min_periods=1).sum() / tr14)
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-10))
    df['ADX'] = dx.rolling(window=14, min_periods=1).mean().fillna(20.0)
    
    # Moving Averages
    df['MA5'] = df['Close'].rolling(window=5, min_periods=1).mean()
    df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['MA50'] = df['Close'].rolling(window=50, min_periods=1).mean()
    
    # Volume Change
    df['Volume_change'] = df['Volume'].pct_change().fillna(0.0)
    
    # Fill any lingering NaNs with bfill/ffill
    df = df.bfill().ffill().fillna(0)
    return df

def get_live_market_data() -> dict[str, pd.DataFrame]:
    """Loads cache, fetches live delta from yfinance if available, computes indicators, and returns clean dict."""
    cache = {}
    if config.MARKET_DATA_CACHE_PATH.exists():
        try:
            with open(config.MARKET_DATA_CACHE_PATH, "rb") as f:
                cache = pickle.load(f)
        except Exception as e:
            print(f"Failed to load cache: {e}")
            
    clean_data = {}
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    for ticker in config.TICKERS:
        df = cache.get(ticker, pd.DataFrame())
        
        # Fetch delta if yfinance is available
        if yf is not None and not df.empty:
            last_date = df.index[-1].strftime('%Y-%m-%d')
            if last_date < today_str:
                try:
                    delta_df = yf.download(ticker, start=last_date, end=today_str, progress=False)
                    if not delta_df.empty:
                        df = pd.concat([df, delta_df])
                        df = df[~df.index.duplicated(keep='last')]
                except Exception as e:
                    print(f"Offline or delta fetch failed for {ticker}: {e}")
                    
        if df.empty:
            # Generate synthetic fallback if completely empty
            dates = pd.date_range(end=datetime.today(), periods=200, freq='B')
            df = pd.DataFrame(index=dates)
            df['Close'] = np.linspace(150, 180, 200) + np.random.normal(0, 2, 200)
            df['Open'] = df['Close']
            df['High'] = df['Close'] + 1
            df['Low'] = df['Close'] - 1
            df['Volume'] = 20000000
            
        df = compute_indicators(df)
        clean_data[ticker] = df
        
    # Update cache
    try:
        with open(config.MARKET_DATA_CACHE_PATH, "wb") as f:
            pickle.dump(clean_data, f)
    except Exception as e:
        print(f"Warning: Could not save updated cache: {e}")
        
    return clean_data

if __name__ == "__main__":
    data = get_live_market_data()
    for t, d in data.items():
        print(f"{t}: shape={d.shape}, last close={d['Close'].iloc[-1]:.2f}, RSI={d['RSI'].iloc[-1]:.1f}")
