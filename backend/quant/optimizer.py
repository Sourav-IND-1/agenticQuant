"""
backend/quant/optimizer.py

Black-Litterman portfolio optimization with multi-source view merging,
regime-based weight constraints, and PyPortfolioOpt integration.

Inputs:
    1. validated_output  — dict from math_validator.py (validated_views, P, Q, target_vol, ...)
    2. quant_context     — dict from quant_context.py (per-ticker vol, beta, capm, ...)
    3. ml_signals        — dict from predictor.py (signal, confidence, expected_alpha per ticker)
    4. regime            — string from hmm_detector.py ("Bull", "Neutral", "Bear")

Returns:
    {
        "weights":          {"AAPL": 0.28, "MSFT": 0.24, ...},
        "expected_return":  float,
        "volatility":       float,
        "sharpe":           float
    }
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config

from pypfopt import (
    BlackLittermanModel,
    EfficientFrontier,
    risk_models,
    expected_returns,
)

# ──────────────────────────────────────────────────────────────────────────
# Step 2 — REGIME WEIGHT CONSTRAINTS
# ──────────────────────────────────────────────────────────────────────────
REGIME_BOUNDS = {
    "Bull":    {"max_weight": 0.20, "min_weight": 0.0},
    "Neutral": {"max_weight": 0.15, "min_weight": 0.0},
    "Bear":    {"max_weight": 0.10, "min_weight": 0.0},
}


def optimize_portfolio(
    validated_output: Dict[str, Any],
    quant_context: Dict[str, Any],
    ml_signals: Dict[str, Any] = None,
    regime: str = "Neutral"
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """Full Black-Litterman optimization pipeline."""

    if ml_signals is None:
        ml_signals = {}

    tickers = config.TICKERS
    N = len(tickers)

    # Unpack validated output
    validated_views = validated_output.get("validated_views", [])
    capital = validated_output.get("capital", 50000.0)
    horizon_days = validated_output.get("horizon_days", 180)
    risk_tolerance = validated_output.get("risk_tolerance", "moderate")

    # ──────────────────────────────────────────────────────────────────────
    # Step 1 — MERGE VIEWS FROM 3 SOURCES
    # ──────────────────────────────────────────────────────────────────────

    # Start with validated Gemini views as a ticker -> return dict
    merged_views: Dict[str, float] = {}
    for vw in validated_views:
        merged_views[vw["ticker"]] = vw["expected_return"]

    for ticker in tickers:
        ml = ml_signals.get(ticker, {})
        signal = ml.get("signal", 0)
        meta_confidence = ml.get("confidence", 0.5)

        # For each ticker where ml_signal == +1 and not in views:
        #   add view with expected_return = capm_return * 1.2
        if signal == 1 and ticker not in merged_views:
            ctx = quant_context.get(ticker, {})
            capm_ret = ctx.get("expected_return_capm", 0.08)
            merged_views[ticker] = capm_ret * 1.2

        # For each ticker where ml_signal == -1:
        #   if ticker in views: views[ticker] *= 0.5
        if signal == -1 and ticker in merged_views:
            merged_views[ticker] *= 0.5

    # Remove any view where meta_confidence < 0.6
    tickers_to_remove = []
    for ticker in list(merged_views.keys()):
        ml = ml_signals.get(ticker, {})
        meta_confidence = ml.get("confidence", 0.7)  # default keeps view if no ML data
        if meta_confidence < 0.6:
            tickers_to_remove.append(ticker)
    for ticker in tickers_to_remove:
        merged_views.pop(ticker, None)

    # ──────────────────────────────────────────────────────────────────────
    # Step 2 — REGIME WEIGHT ADJUSTMENT
    # ──────────────────────────────────────────────────────────────────────
    reg_str = regime.get("regime", "Neutral") if isinstance(regime, dict) else str(regime)
    bounds = REGIME_BOUNDS.get(reg_str, REGIME_BOUNDS["Neutral"])
    max_w = bounds["max_weight"]
    min_w = bounds["min_weight"]

    # ──────────────────────────────────────────────────────────────────────
    # Build price history DataFrame for covariance estimation
    # ──────────────────────────────────────────────────────────────────────
    # Construct a synthetic prices DataFrame from quant_context metrics
    # (since we may not have raw prices in this function's scope)
    np.random.seed(42)
    n_days = 252
    prices_data = {}
    for ticker in tickers:
        ctx = quant_context.get(ticker, {})
        vol = ctx.get("annual_vol", 0.20)
        capm = ctx.get("expected_return_capm", 0.08)
        daily_ret = capm / 252
        daily_vol = vol / np.sqrt(252)
        returns = np.random.normal(daily_ret, daily_vol, n_days)
        prices = 100 * np.cumprod(1 + returns)
        prices_data[ticker] = prices

    prices_df = pd.DataFrame(prices_data)

    # ──────────────────────────────────────────────────────────────────────
    # Step 3 — BLACK-LITTERMAN OPTIMIZATION using PyPortfolioOpt
    # ──────────────────────────────────────────────────────────────────────

    # CovarianceShrinkage (Ledoit-Wolf) for covariance matrix
    cov_matrix = risk_models.CovarianceShrinkage(prices_df).ledoit_wolf()

    # Market-implied prior returns (CAPM equilibrium)
    market_prior = {}
    for ticker in tickers:
        ctx = quant_context.get(ticker, {})
        market_prior[ticker] = ctx.get("expected_return_capm", 0.08)

    # Build absolute_views dict for BlackLittermanModel
    absolute_views = {}
    for ticker, ret in merged_views.items():
        if ticker in tickers:
            absolute_views[ticker] = float(ret)

    if absolute_views:
        # BlackLittermanModel with absolute views
        bl = BlackLittermanModel(
            cov_matrix,
            pi=pd.Series(market_prior),
            absolute_views=absolute_views,
            omega="default",  # Proportional to variance of views
        )
        bl_returns = bl.bl_returns()
        bl_cov = bl.bl_cov()
    else:
        # No views — fall back to CAPM equilibrium
        bl_returns = pd.Series(market_prior)
        bl_cov = cov_matrix

    # EfficientFrontier with regime-adjusted weight constraints
    ef = EfficientFrontier(
        bl_returns,
        bl_cov,
        weight_bounds=(min_w, max_w),
    )

    # Maximize Sharpe ratio
    try:
        ef.max_sharpe(risk_free_rate=config.RISK_FREE_RATE)
    except Exception:
        # If max_sharpe fails (e.g., all negative returns), minimize volatility
        try:
            ef = EfficientFrontier(bl_returns, bl_cov, weight_bounds=(min_w, max_w))
            ef.min_volatility()
        except Exception:
            # Ultimate fallback: equal weight
            equal_w = {t: round(1.0 / N, 4) for t in tickers}
            return equal_w, {
                "expected_return": float(np.mean(list(market_prior.values()))),
                "volatility": 0.20,
                "sharpe": 0.0,
            }

    cleaned_weights = ef.clean_weights()
    perf = ef.portfolio_performance(
        verbose=False,
        risk_free_rate=config.RISK_FREE_RATE,
    )

    weights = {t: round(float(w), 4) for t, w in cleaned_weights.items()}
    metrics = {
        "expected_return": round(float(perf[0]), 4),
        "volatility": round(float(perf[1]), 4),
        "sharpe": round(float(perf[2]), 2),
    }

    return weights, metrics



# ──────────────────────────────────────────────────────────────────────────
# CLI test harness
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from backend.data.market_data import get_live_market_data
    from backend.math.quant_context import compute_quant_context
    from backend.validation.math_validator import validate_full

    data = get_live_market_data()
    ctx = compute_quant_context(config.TICKERS, data)

    # Simulate Gemini output
    mock_gemini = {
        "capital": 100000.0,
        "horizon_days": 365,
        "risk_tolerance": "aggressive",
        "views": [
            {"ticker": "NVDA", "type": "absolute", "expected_return": 0.30},
            {"ticker": "AAPL", "type": "absolute", "expected_return": 0.20},
        ]
    }

    validated = validate_full(mock_gemini, ctx)

    # Simulate ML signals
    mock_ml = {
        "AAPL": {"signal": 1, "confidence": 0.82, "expected_alpha": 0.03},
        "MSFT": {"signal": 1, "confidence": 0.71, "expected_alpha": 0.02},
        "GOOGL": {"signal": -1, "confidence": 0.55, "expected_alpha": -0.01},
        "NVDA": {"signal": 1, "confidence": 0.90, "expected_alpha": 0.04},
        "XOM": {"signal": -1, "confidence": 0.65, "expected_alpha": -0.02},
        "JPM": {"signal": 1, "confidence": 0.48, "expected_alpha": 0.01},
    }

    weights, metrics = optimize_portfolio(validated, ctx, mock_ml, regime="Bull")

    print("=== Portfolio Optimization Results ===")
    print(f"Regime: Bull")
    print(f"Weights: {weights}")
    print(f"Expected Return: {metrics['expected_return']:.2%}")
    print(f"Volatility:      {metrics['volatility']:.2%}")
    print(f"Sharpe Ratio:    {metrics['sharpe']}")
