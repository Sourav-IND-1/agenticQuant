import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union

def compute_quant_context(arg1: Union[List[str], Dict[str, pd.DataFrame]], arg2: Union[Dict[str, pd.DataFrame], List[str]] = None) -> Dict[str, Any]:
    """Computes quantitative financial metrics, rolling 60d correlations, and z-score normalization.

    Supports dual calling conventions:
        compute_quant_context(ticker_list, cached_market_data)
        compute_quant_context(cached_market_data)
    """
    tickers = None
    market_data = {}

    if arg2 is None:
        if isinstance(arg1, dict):
            market_data = arg1
            tickers = [t for t in market_data.keys() if t != '^NSEI']
        elif isinstance(arg1, list):
            tickers = arg1
    else:
        if isinstance(arg1, list) and isinstance(arg2, dict):
            tickers = arg1
            market_data = arg2
        elif isinstance(arg1, dict) and isinstance(arg2, list):
            market_data = arg1
            tickers = arg2

    if not tickers:
        tickers = [t for t in market_data.keys() if t != '^NSEI']

    returns_dict = {}
    for ticker, df in market_data.items():
        if not df.empty and 'Close' in df.columns:
            returns_dict[ticker] = df['Close'].squeeze().pct_change().dropna()

    # Ensure there is valid data to prevent "scalar without index" pandas error
    valid_series = [s for s in returns_dict.values() if not s.empty]
    if not valid_series:
        return {}

    try:
        returns_df = pd.DataFrame(returns_dict).bfill().ffill().fillna(0.0)
    except Exception:
        # Fallback if pandas rejects the dict (e.g., mismatched shapes or scalars)
        returns_df = pd.DataFrame(returns_dict, index=valid_series[0].index).bfill().ffill().fillna(0.0)

    if returns_df.empty:
        return {}

    # Get benchmark SPY returns or equal-weighted synthetic proxy
    if 'SPY' in returns_df.columns:
        spy_ret = returns_df['SPY']
    else:
        spy_ret = returns_df.mean(axis=1)

    spy_var = float(spy_ret.var())
    if spy_var == 0:
        spy_var = 1e-6

    rf = 0.04
    market_premium = 0.055

    # 7. Rolling 60-day correlation matrix between all tickers
    rolling_60d_ret = returns_df.tail(60)
    corr_matrix = rolling_60d_ret.corr().fillna(0.0)

    raw_metrics = {}
    for ticker in tickers:
        if ticker not in returns_df.columns or ticker not in market_data:
            continue

        asset_ret = returns_df[ticker]
        df = market_data[ticker]
        close = np.squeeze(df['Close'].values)

        # 1. Annualized volatility: sigma = daily_returns.std() * sqrt(252)
        sigma = float(asset_ret.std() * np.sqrt(252))

        # 2. Beta vs SPY: beta = Cov(stock_returns, spy_returns) / Var(spy_returns)
        cov = float(asset_ret.cov(spy_ret))
        beta = cov / spy_var

        # 3. Sharpe ratio: (annualized_return - 0.04) / sigma
        ann_ret = float(asset_ret.mean() * 252)
        sharpe = (ann_ret - rf) / (sigma if sigma != 0 else 1e-6)

        # 4. 20-day momentum: (price_today / price_20d_ago) - 1
        mom_20d = float((close[-1] / close[-20] - 1.0) if len(close) >= 20 else 0.0)

        # 5. 60-day momentum: (price_today / price_60d_ago) - 1
        mom_60d = float((close[-1] / close[-60] - 1.0) if len(close) >= 60 else 0.0)

        # 6. CAPM expected return: 0.04 + beta * 0.055
        expected_return_capm = rf + beta * market_premium

        # Extract correlations for this ticker against all other valid tickers
        correlations = {}
        for other_t in tickers:
            if other_t in corr_matrix.columns and ticker in corr_matrix.index:
                correlations[other_t] = round(float(corr_matrix.loc[ticker, other_t]), 4)
            else:
                correlations[other_t] = 0.0

        raw_metrics[ticker] = {
            "annual_vol": round(sigma, 4),
            "beta": round(beta, 4),
            "sharpe": round(sharpe, 4),
            "momentum_20d": round(mom_20d, 4),
            "momentum_60d": round(mom_60d, 4),
            "expected_return_capm": round(expected_return_capm, 4),
            "correlations": correlations,
            "latest_price": round(float(close[-1]), 2) if len(close) > 0 else 0.0
        }

    # 8. Z-score normalization of all metrics across universe: (x - mean) / std
    metric_keys = ["annual_vol", "beta", "sharpe", "momentum_20d", "momentum_60d", "expected_return_capm"]
    if len(raw_metrics) > 1:
        for k in metric_keys:
            vals = np.array([m[k] for m in raw_metrics.values()])
            mean_val = np.mean(vals)
            std_val = np.std(vals)
            for t in raw_metrics:
                z_val = float((raw_metrics[t][k] - mean_val) / std_val) if std_val > 1e-8 else 0.0
                if "z_scores" not in raw_metrics[t]:
                    raw_metrics[t]["z_scores"] = {}
                raw_metrics[t]["z_scores"][k] = round(z_val, 4)
    else:
        for t in raw_metrics:
            raw_metrics[t]["z_scores"] = {k: 0.0 for k in metric_keys}

    return raw_metrics

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from data.market_data import get_live_market_data
    import config

    data = get_live_market_data()
    ctx = compute_quant_context(config.TICKERS, data)
    for symbol, details in ctx.items():
        print(f"[{symbol}] Vol={details['annual_vol']:.2f}, Beta={details['beta']:.2f}, Sharpe={details['sharpe']:.2f}, CAPM Ret={details['expected_return_capm']:.2%}")
        print(f"  Z-Scores: {details['z_scores']}")
