import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config

try:
    from pypfopt import BlackLittermanModel, EfficientFrontier
    from pypfopt.risk_models import sample_cov
except ImportError:
    BlackLittermanModel = None

def optimize_portfolio(quant_context: Dict[str, Any], P: np.ndarray, Q: np.ndarray, brief: Dict[str, Any] = None) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """Calculates optimal Black-Litterman asset allocation weights and portfolio analytics."""
    tickers = [t for t in quant_context.keys() if t != 'SPY' and isinstance(quant_context[t], dict) and 'expected_return_capm' in quant_context[t]]
    if not tickers:
        tickers = config.TICKERS

    n = len(tickers)
    
    # 1. Extract CAPM equilibrium prior returns vector Pi
    pi_list = []
    vol_list = []
    for t in tickers:
        ctx = quant_context.get(t, {})
        pi_list.append(ctx.get("expected_return_capm", 0.08))
        vol_list.append(ctx.get("annual_vol", 0.20))
        
    pi_vec = np.array(pi_list)
    vols = np.array(vol_list)
    
    # Construct diagonal or simplified covariance matrix Sigma
    Sigma = np.diag(vols ** 2)
    
    # 2. Black-Litterman posterior expected return calculation
    if P is not None and Q is not None and len(Q) > 0 and P.shape[1] == n:
        tau = 0.05
        # Uncertainty matrix Omega = diag(P * (tau * Sigma) * P^T)
        omega_diag = np.diag(P @ (tau * Sigma) @ P.T)
        Omega = np.diag(np.maximum(omega_diag, 1e-6))
        
        try:
            inv_tau_sigma = np.linalg.pinv(tau * Sigma)
            inv_omega = np.linalg.pinv(Omega)
            post_cov = np.linalg.pinv(inv_tau_sigma + P.T @ inv_omega @ P)
            post_pi = post_cov @ (inv_tau_sigma @ pi_vec + P.T @ inv_omega @ Q)
        except Exception as e:
            print(f"Matrix inversion warning ({e}), falling back to prior Pi.")
            post_pi = pi_vec
    else:
        post_pi = pi_vec

    # 3. Mean-variance portfolio weights allocation
    # Adjust risk aversion delta based on user brief
    risk_tol = (brief or {}).get("risk_tolerance", "aggressive").lower()
    delta = 2.0 if risk_tol == "aggressive" else (3.5 if risk_tol == "neutral" else 5.0)
    
    try:
        inv_sigma = np.linalg.pinv(Sigma)
        raw_weights = inv_sigma @ post_pi / delta
        # Clip negative weights (long-only) and normalize to sum to 1.0
        raw_weights = np.maximum(raw_weights, 0.01)
        weights_arr = raw_weights / np.sum(raw_weights)
    except Exception:
        weights_arr = np.ones(n) / n

    weights = {tickers[i]: round(float(weights_arr[i]), 4) for i in range(n)}
    
    # 4. Compute Portfolio Performance Metrics
    port_ret = float(np.sum(weights_arr * post_pi))
    port_vol = float(np.sqrt(weights_arr.T @ Sigma @ weights_arr))
    rf = config.RISK_FREE_RATE
    sharpe = round((port_ret - rf) / (port_vol if port_vol > 0 else 1e-6), 2)
    
    # Parametric Daily Value at Risk (95%)
    daily_vol = port_vol / np.sqrt(252)
    var95 = round(-1.645 * daily_vol, 4)
    max_drawdown = round(-2.5 * port_vol, 4)
    capital = (brief or {}).get("capital", 100000)

    metrics = {
        "expectedReturn": round(port_ret, 4),
        "sharpeRatio": sharpe,
        "var95": var95,
        "maxDrawdown": max_drawdown,
        "capital": capital
    }
    
    return weights, metrics

if __name__ == "__main__":
    from backend.data.market_data import get_live_market_data
    from backend.math.quant_context import compute_quant_context
    d = get_live_market_data()
    c = compute_quant_context(config.TICKERS, d)
    w, m = optimize_portfolio(c, None, None, {"capital": 100000, "risk_tolerance": "aggressive"})
    print("Weights:", w)
    print("Metrics:", m)
