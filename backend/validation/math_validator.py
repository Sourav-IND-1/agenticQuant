import numpy as np
from typing import Dict, Any, Tuple, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def validate_and_format_views(brief: Dict[str, Any], quant_context: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """Validates and bounds LLM views against quantitative volatility caps and scales by horizon.

    Returns:
        P: Link matrix of shape (K, N) where K is valid views, N is total assets.
        Q: View vector of shape (K,).
        validated_views: Cleaned list of view dicts for dashboard logging.
    """
    views = brief.get("views", [])
    horizon_days = max(1, brief.get("horizon_days", 180))
    horizon_factor = np.sqrt(horizon_days / 252.0)
    
    valid_views = []
    tickers = config.TICKERS
    
    for v in views:
        ticker = v.get("ticker", "").upper()
        if ticker not in tickers:
            continue
            
        raw_ret = float(v.get("expected_return", 0.08))
        ctx = quant_context.get(ticker, {})
        ann_vol = ctx.get("annualized_volatility", 0.25)
        
        # Cap absolute return expectations to 2x the stock's annualized volatility
        max_cap = 2.0 * ann_vol
        capped_ret = np.clip(raw_ret, -max_cap, max_cap)
        
        # Scale view if needed or keep annualized
        valid_views.append({
            "ticker": ticker,
            "type": "absolute",
            "expected_return": round(float(capped_ret), 4),
            "original_return": round(raw_ret, 4),
            "capped": abs(raw_ret - capped_ret) > 1e-4
        })
        
    K = len(valid_views)
    N = len(tickers)
    
    if K == 0:
        return np.array([]), np.array([]), []
        
    P = np.zeros((K, N))
    Q = np.zeros(K)
    
    for k, v in enumerate(valid_views):
        t_idx = tickers.index(v["ticker"])
        P[k, t_idx] = 1.0
        Q[k] = v["expected_return"]
        
    return P, Q, valid_views

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(backend_dir / "math"))
    from quant_context import compute_quant_context
    from data.market_data import get_live_market_data
    from llm.gemini import extract_investment_brief
    from ml.predictor import predict_alphas
    
    data = get_live_market_data()
    ctx = compute_quant_context(data)
    ml = predict_alphas(data)
    
    brief = extract_investment_brief("Bullish on NVDA anticipating 80% return over 6 months with $50k", ctx, ml, "Bull")
    P, Q, val_views = validate_and_format_views(brief, ctx)
    print("Validated Views:", val_views)
    print(f"P shape: {P.shape}, Q: {Q}")
