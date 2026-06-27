import numpy as np
import pandas as pd
from typing import Dict, Any, List

def transform_live_features(df: pd.DataFrame, transform_params: Dict[str, Any]) -> pd.DataFrame:
    """Transforms a live feature DataFrame matching the pre-modeling pipeline.

    Applies stationarity differencing, rolling z-score normalization, and feature selection based on saved transform parameters.
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    # 1. Apply Stationarity Differencing
    differenced_cols = transform_params.get("differenced_cols", [])
    for col in differenced_cols:
        if col in df.columns:
            df[col] = df[col].diff().fillna(0)
            
    # 2. Apply Rolling Z-Score Normalization
    rolling_params = transform_params.get("rolling_params", {})
    for col, params in rolling_params.items():
        if col in df.columns:
            mean = params.get("mean", 0.0)
            std = params.get("std", 1.0)
            if std == 0:
                std = 1.0
            # If mean/std are default 0/1, compute rolling 60d mean/std on the fly if dataframe has enough history
            if mean == 0.0 and std == 1.0 and len(df) >= 10:
                col_mean = df[col].rolling(min(60, len(df)), min_periods=1).mean()
                col_std = df[col].rolling(min(60, len(df)), min_periods=1).std().replace(0, 1.0)
                df[col] = (df[col] - col_mean) / col_std
            else:
                df[col] = (df[col] - mean) / std
                
    # 3. Filter to Final Selected Features
    final_features = transform_params.get("final_features", df.columns.tolist())
    available_cols = [c for c in final_features if c in df.columns]
    
    X = df[available_cols].bfill().ffill().fillna(0)
    return X

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from data.market_data import get_live_market_data
    import config
    
    data = get_live_market_data()
    dummy_params = {
        "differenced_cols": ["RSI"],
        "rolling_params": {"MACD": {"mean": 0.0, "std": 1.0}},
        "final_features": config.FEATURE_COLS
    }
    aapl_X = transform_live_features(data["AAPL"], dummy_params)
    print(f"Transformed AAPL X shape: {aapl_X.shape}")
    print(aapl_X.tail(2))
