"""
End-to-end verification of the India migration.
Tests: config, market data, quant context, ML models, HMM regime, optimizer, rebalancer math.
"""
import sys, os, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import config
import numpy as np
import pandas as pd

PASS = "[PASS]"
FAIL = "[FAIL]"
errors = []

def check(name, condition, detail=""):
    if condition:
        print(f"  {PASS}  {name}")
    else:
        print(f"  {FAIL}  {name}  — {detail}")
        errors.append(name)

print("=" * 70)
print("  INDIA MIGRATION — END-TO-END VERIFICATION")
print("=" * 70)

# ─── 1. CONFIG ───────────────────────────────────────────────────────
print("\n[1/7] Config Validation")
check("All tickers are .NS",
      all(t.endswith(".NS") for t in config.TICKERS),
      f"Non-.NS tickers found: {[t for t in config.TICKERS if not t.endswith('.NS')]}")
check("Risk-free rate = 6.5%", config.RISK_FREE_RATE == 0.065, f"Got {config.RISK_FREE_RATE}")
check("Market premium = 5%", config.MARKET_PREMIUM == 0.05, f"Got {config.MARKET_PREMIUM}")
check("Ticker count ≥ 48", len(config.TICKERS) >= 48, f"Got {len(config.TICKERS)}")

# ─── 2. MARKET DATA ─────────────────────────────────────────────────
print("\n[2/7] Market Data Fetch")
from backend.data.market_data import get_live_market_data
t0 = time.time()
market_data = get_live_market_data()
elapsed = time.time() - t0
print(f"  (Fetched in {elapsed:.1f}s)")

fetched_tickers = [t for t in config.TICKERS if t in market_data and not market_data[t].empty]
check(f"Fetched ≥ 45 tickers", len(fetched_tickers) >= 45, f"Only got {len(fetched_tickers)}")
check("^NSEI benchmark present", "^NSEI" in market_data and not market_data["^NSEI"].empty)

# Check prices are in INR range (not USD)
sample_ticker = "RELIANCE.NS"
if sample_ticker in market_data and not market_data[sample_ticker].empty:
    last_price = float(market_data[sample_ticker]["Close"].iloc[-1])
    check(f"RELIANCE.NS price is INR-range (>500)", last_price > 500, f"Got ₹{last_price:.2f}")
else:
    check(f"RELIANCE.NS data available", False, "Missing")

# ─── 3. QUANT CONTEXT ───────────────────────────────────────────────
print("\n[3/7] Quant Context Computation")
from backend.math.quant_context import compute_quant_context
quant_ctx = compute_quant_context(config.TICKERS, market_data)
check("Quant context computed", len(quant_ctx) > 0, "Empty context")
check("^NSEI excluded from context", "^NSEI" not in quant_ctx)
check("RELIANCE.NS in context", "RELIANCE.NS" in quant_ctx)

if "RELIANCE.NS" in quant_ctx:
    rel_ctx = quant_ctx["RELIANCE.NS"]
    check("RELIANCE.NS has volatility", "annual_vol" in rel_ctx, str(rel_ctx.keys()))
    check("RELIANCE.NS has CAPM return", "expected_return_capm" in rel_ctx)
    capm = rel_ctx.get("expected_return_capm", 0)
    check("CAPM return is reasonable (5-25%)", 0.05 <= capm <= 0.25, f"Got {capm:.2%}")

# ─── 4. ML PREDICTIONS ──────────────────────────────────────────────
print("\n[4/7] ML Model Loading & Predictions")
import backend.ml.loader as loader
check("Primary models loaded", loader.PRIMARY_MODELS is not None and len(loader.PRIMARY_MODELS) > 0,
      f"Got {len(loader.PRIMARY_MODELS) if loader.PRIMARY_MODELS else 0} models")
check("Meta models loaded", loader.META_MODELS is not None and len(loader.META_MODELS) > 0)

from backend.ml.predictor import predict_alphas
ml_signals = predict_alphas(market_data)
valid_signals = {t: s for t, s in ml_signals.items() if t in config.TICKERS}
check(f"ML signals for ≥ 40 tickers", len(valid_signals) >= 40, f"Got {len(valid_signals)}")

# Check signal structure
for t, sig in list(valid_signals.items())[:3]:
    has_signal = "signal" in sig
    has_conf = "confidence" in sig
    check(f"  {t} has signal+confidence", has_signal and has_conf, str(sig))

# ─── 5. HMM REGIME ──────────────────────────────────────────────────
print("\n[5/7] HMM Regime Detection")
from backend.regime.hmm_detector import detect_regime
regime = detect_regime(market_data)
regime_str = regime.get("regime", "MISSING")
check("Regime detected", regime_str in ["Bull", "Neutral", "Bear"], f"Got '{regime_str}'")
print(f"  → Current regime: {regime_str}")

# ─── 6. BLACK-LITTERMAN OPTIMIZER ────────────────────────────────────
print("\n[6/7] Black-Litterman Portfolio Optimization")
from backend.validation.math_validator import validate_full

mock_brief = {
    "capital": 500000.0,    # ₹5 lakh
    "horizon_days": 90,
    "risk_tolerance": "aggressive",
    "max_sell_pct": 1.0,
    "current_holdings": {},
    "views": [
        {"ticker": "RELIANCE.NS", "type": "absolute", "expected_return": 0.20},
        {"ticker": "TCS.NS", "type": "absolute", "expected_return": 0.15},
    ]
}
validated = validate_full(mock_brief, quant_ctx)
check("Validator passed", validated is not None)

from backend.quant.optimizer import optimize_portfolio
weights, metrics = optimize_portfolio(validated, quant_ctx, ml_signals, regime_str)

check("Weights returned", len(weights) > 0, f"Got {len(weights)} weights")
total_w = sum(weights.values())
check(f"Weights sum ≈ 1.0", abs(total_w - 1.0) < 0.02, f"Sum = {total_w:.4f}")
check("All weight tickers are .NS", all(t.endswith(".NS") for t in weights), 
      f"Non-.NS: {[t for t in weights if not t.endswith('.NS')]}")

exp_ret = metrics.get("expected_return", 0)
vol = metrics.get("volatility", 0)
sharpe = metrics.get("sharpe", 0)
check(f"Expected return > 0", exp_ret > 0, f"Got {exp_ret:.2%}")
check(f"Volatility in range (5-50%)", 0.05 <= vol <= 0.50, f"Got {vol:.2%}")
check(f"Sharpe ratio > -1", sharpe > -1, f"Got {sharpe:.2f}")

print(f"  → Expected Return: {exp_ret:.2%}")
print(f"  → Volatility:      {vol:.2%}")
print(f"  → Sharpe Ratio:    {sharpe:.2f}")

# Top 5 allocations
sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:5]
print(f"  → Top 5 allocations:")
for t, w in sorted_w:
    print(f"      {t:>20s}  {w:.1%}  (₹{w * 500000:,.0f})")

# ─── 7. REBALANCER MATH ─────────────────────────────────────────────
print("\n[7/7] Rebalancer — Capital Allocation Math")
from backend.quant.rebalancer import generate_rebalancing_actions

# Simulate: user holds 10 shares of HDFCBANK.NS, has ₹10,000 capital
current_holdings = {
    "HDFCBANK.NS": {"shares": 10, "avg_cost": 0}
}
current_prices = {}
for t in config.TICKERS:
    if t in market_data and not market_data[t].empty:
        try:
            val = market_data[t]["Close"].iloc[-1]
            current_prices[t] = float(val) if not isinstance(val, pd.Series) else float(val.iloc[0])
        except:
            pass

hdfc_price = current_prices.get("HDFCBANK.NS", 1700)
holdings_value = 10 * hdfc_price
cash = 10000
total_capital = holdings_value + cash
print(f"  HDFC price: ₹{hdfc_price:,.0f}")
print(f"  Holdings value: ₹{holdings_value:,.0f}")
print(f"  Cash: ₹{cash:,.0f}")
print(f"  Total capital: ₹{total_capital:,.0f}")

actions = generate_rebalancing_actions(current_holdings, weights, current_prices, max_sell_pct=1.0)
check("Rebalancing actions generated", len(actions) > 0, f"Got {len(actions)} actions")

total_buy = sum(a.get("dollar_amount", 0) for a in actions if "BUY" in a.get("action", ""))
total_sell = sum(abs(a.get("dollar_amount", 0)) for a in actions if "SELL" in a.get("action", ""))
check(f"Buy/sell amounts are INR-scale (>100)", total_buy > 100 or total_sell > 100, 
      f"Buy=₹{total_buy:.0f} Sell=₹{total_sell:.0f}")

# ─── SUMMARY ─────────────────────────────────────────────────────────
print("\n" + "=" * 70)
if errors:
    print(f"  ⚠️  {len(errors)} TESTS FAILED: {errors}")
else:
    print("  🎉  ALL TESTS PASSED — India migration is fully operational!")
print("=" * 70)
