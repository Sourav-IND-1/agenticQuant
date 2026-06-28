"""
backend/validation/math_validator.py

Validates and transforms Gemini LLM output into bounded, horizon-scaled
Black-Litterman matrices (P, Q) grounded in quantitative volatility constraints.

Inputs:
    1. gemini_output  — dict from gemini.py  (capital, horizon_days, risk_tolerance, views)
    2. quant_context  — dict from quant_context.py  (per-ticker annual_vol, beta, etc.)

Pipeline (executed in order):
    1. Cap views at 2× annualized volatility
    2. Map risk tolerance → target portfolio volatility
    3. Scale views by investment horizon  (√(horizon_days / 252))
    4. Construct Black-Litterman P matrix (K×N) and Q vector (K,)

Returns:
    Tuple of (P, Q, validated_views)   — called from main.py
    Full result dict available via validate_full()
"""

import numpy as np
from typing import Dict, Any, Tuple, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


# Step 2: Risk tolerance → target portfolio volatility mapping
RISK_MAP = {
    "conservative": 0.10,
    "moderate": 0.20,
    "aggressive": 0.35,
}


def validate_full(gemini_output: Dict[str, Any],
                  quant_context: Dict[str, Any]) -> Dict[str, Any]:
    """Full validation pipeline returning the complete result dictionary.

    Returns:
        {
            "validated_views": list of validated view dicts,
            "target_vol": float,
            "P": np.ndarray (K, N),
            "Q": np.ndarray (K,),
            "capital": float,
            "horizon_days": int,
            "risk_tolerance": str
        }
    """
    views = gemini_output.get("views", [])
    capital = float(gemini_output.get("capital", 50000.0))
    horizon_days = max(1, int(gemini_output.get("horizon_days", 180)))
    risk_tolerance = gemini_output.get("risk_tolerance", "moderate").lower()

    tickers = config.TICKERS
    N = len(tickers)

    # ──────────────────────────────────────────────────────────────────────
    # Step 2: MAP RISK TOLERANCE TO TARGET VOLATILITY
    # ──────────────────────────────────────────────────────────────────────
    target_vol = RISK_MAP.get(risk_tolerance, 0.20)

    # ──────────────────────────────────────────────────────────────────────
    # Step 3: HORIZON SCALING FACTOR
    #   scale = √(horizon_days / 252)
    # ──────────────────────────────────────────────────────────────────────
    scale = np.sqrt(horizon_days / 252.0)

    # ──────────────────────────────────────────────────────────────────────
    # Steps 1 + 3 applied per view
    # ──────────────────────────────────────────────────────────────────────
    validated_views: List[Dict[str, Any]] = []

    for v in views:
        ticker = v.get("ticker", "").upper()
        if ticker not in tickers:
            continue

        raw_return = float(v.get("expected_return", 0.08))
        ctx = quant_context.get(ticker, {})

        # Resolve annual_vol
        annual_vol = ctx.get("annual_vol", 0.25)

        # ── Step 1: CAP VIEWS AT 2× ANNUALIZED VOLATILITY ──────────────
        cap = 2.0 * annual_vol
        if abs(raw_return) > cap:
            capped_return = np.sign(raw_return) * cap
        else:
            capped_return = raw_return

        # ── Step 3: SCALE VIEWS BY HORIZON ──────────────────────────────
        #   scaled_return = expected_return × √(horizon_days / 252)
        scaled_return = capped_return * scale

        validated_views.append({
            "ticker": ticker,
            "type": "absolute",
            "expected_return": round(float(scaled_return), 4),
            "original_return": round(raw_return, 4),
            "capped_return": round(float(capped_return), 4),
            "capped": abs(raw_return - capped_return) > 1e-6,
            "horizon_scaled": True,
        })

    # ──────────────────────────────────────────────────────────────────────
    # Step 4: CONSTRUCT BLACK-LITTERMAN MATRICES
    #   P matrix: shape (K, N)  — pick matrix linking views to assets
    #   Q vector: shape (K,)    — bounded return expectations
    # ──────────────────────────────────────────────────────────────────────
    K = len(validated_views)

    if K == 0:
        P = np.zeros((0, N))
        Q = np.zeros(0)
    else:
        P = np.zeros((K, N))
        Q = np.zeros(K)

        for k, vw in enumerate(validated_views):
            t_idx = tickers.index(vw["ticker"])
            P[k, t_idx] = 1.0
            Q[k] = vw["expected_return"]

    return {
        "validated_views": validated_views,
        "target_vol": target_vol,
        "P": P,
        "Q": Q,
        "capital": capital,
        "horizon_days": horizon_days,
        "risk_tolerance": risk_tolerance,
    }


# ──────────────────────────────────────────────────────────────────────────
# Backward-compatible wrapper used by main.py
# ──────────────────────────────────────────────────────────────────────────

def validate_and_format_views(
    gemini_output: Dict[str, Any],
    quant_context: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """Convenience wrapper returning (P, Q, validated_views) for main.py."""
    result = validate_full(gemini_output, quant_context)
    return result["P"], result["Q"], result["validated_views"]


# ──────────────────────────────────────────────────────────────────────────
# CLI test harness
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    from backend.data.market_data import get_live_market_data
    from backend.math.quant_context import compute_quant_context

    data = get_live_market_data()
    ctx = compute_quant_context(config.TICKERS, data)

    # Simulate a Gemini output
    mock_gemini = {
        "capital": 100000.0,
        "horizon_days": 365,
        "risk_tolerance": "aggressive",
        "views": [
            {"ticker": "NVDA", "type": "absolute", "expected_return": 0.80},
            {"ticker": "AAPL", "type": "absolute", "expected_return": 0.25},
            {"ticker": "XOM",  "type": "absolute", "expected_return": -0.40},
        ]
    }

    result = validate_full(mock_gemini, ctx)

    print("=== Validation Results ===")
    print(f"Target Vol:    {result['target_vol']}")
    print(f"Capital:       ${result['capital']:,.0f}")
    print(f"Horizon:       {result['horizon_days']} days")
    print(f"Risk:          {result['risk_tolerance']}")
    print(f"P shape:       {result['P'].shape}")
    print(f"Q vector:      {result['Q']}")
    print()
    for vw in result["validated_views"]:
        flag = " [CAPPED]" if vw["capped"] else ""
        print(f"  {vw['ticker']}: original={vw['original_return']:.4f} -> "
              f"capped={vw['capped_return']:.4f} -> "
              f"horizon_scaled={vw['expected_return']:.4f}{flag}")
