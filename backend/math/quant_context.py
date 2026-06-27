import numpy as np
import pandas as pd
from typing import Dict, Any

def compute_quant_context(market_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
    """Computes foundational quantitative financial metrics for each asset.

    Returns dictionary containing:
        - annualized_volatility
        - beta
        - sharpe_ratio
        - momentum_20d
        - momentum_60d
        - capm_expected_return
    """
    returns_dict = {}
    for ticker, df in market_data.items():
        if not df.empty and 'Close' in df.columns:
            returns_dict[ticker] = df['Close'].pct_change().dropna()
            
    if not returns_dict:
        return {}
        
    # Align returns into a unified dataframe
    returns_df = pd.DataFrame(returns_dict).dropna()
    if returns_df.empty:
        return {}
        
    # Use equal-weighted universe mean return as synthetic SPY benchmark proxy
    market_ret = returns_df.mean(axis=1)
    market_var = market_ret.var()
    if market_var == 0:
        market_var = 1e-6
        
    rf = 0.04  # 4% risk-free rate
    market_premium = 0.05  # 5% equity risk premium
    
    context = {}
    for ticker in market_data.keys():
        if ticker not in returns_df.columns:
            continue
            
        asset_ret = returns_df[ticker]
        df = market_data[ticker]
        
        # Annualized Volatility
        ann_vol = float(asset_ret.std() * np.sqrt(252))
        
        # Annualized Mean Return
        ann_ret = float(asset_ret.mean() * 252)
        
        # Beta vs Benchmark
        cov = float(asset_ret.cov(market_ret))
        beta = cov / market_var
        
        # Sharpe Ratio
        sharpe = (ann_ret - rf) / (ann_vol if ann_vol != 0 else 1e-6)
        
        # CAPM Expected Return
        capm_ret = rf + beta * market_premium
        
        # Momentum 20 day and 60 day
        close = df['Close'].values
        mom_20 = float((close[-1] / close[-20] - 1.0) if len(close) >= 20 else 0.0)
        mom_60 = float((close[-1] / close[-60] - 1.0) if len(close) >= 60 else 0.0)
        
        context[ticker] = {
            "annualized_volatility": round(ann_vol, 4),
            "beta": round(beta, 4),
            "sharpe_ratio": round(sharpe, 4),
            "momentum_20d": round(mom_20, 4),
            "momentum_60d": round(mom_60, 4),
            "capm_expected_return": round(capm_ret, 4),
            "latest_price": round(float(close[-1]), 2)
        }
        
    return context

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from data.market_data import get_live_market_data
    
    data = get_live_market_data()
    ctx = compute_quant_context(data)
    for t, metrics in ctx.items():
        print(f"{t}: Vol={metrics['annualized_volatility']:.1%}, Beta={metrics['beta']:.2f}, CAPM Ret={metrics['capm_expected_return']:.1%}, Sharpe={metrics['sharpe_ratio']:.2f}")
