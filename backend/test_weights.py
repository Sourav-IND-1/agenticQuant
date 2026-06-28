import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import config
from backend.data.market_data import get_live_market_data
from backend.math.quant_context import compute_quant_context
from backend.ml.predictor import predict_alphas
from backend.regime.hmm_detector import detect_regime
from backend.validation.math_validator import validate_full
from backend.quant.optimizer import optimize_portfolio

market_data = get_live_market_data()
quant_ctx = compute_quant_context(config.TICKERS, market_data)
ml_signals = predict_alphas(market_data)
regime = detect_regime(market_data)
regime_str = regime.get('regime', 'Neutral')

mock = {
    'capital': 500000.0,
    'horizon_days': 90,
    'risk_tolerance': 'aggressive',
    'max_sell_pct': 1.0,
    'current_holdings': {},
    'views': [
        {'ticker': 'RELIANCE.NS', 'type': 'absolute', 'expected_return': 0.25},
        {'ticker': 'TCS.NS', 'type': 'absolute', 'expected_return': 0.18},
    ]
}
validated = validate_full(mock, quant_ctx)
weights, metrics = optimize_portfolio(validated, quant_ctx, ml_signals, regime_str)

er = metrics['expected_return']
vol = metrics['volatility']
sr = metrics['sharpe']
print(f'Regime: {regime_str}')
print(f'Expected Return: {er:.2%}')
print(f'Volatility:      {vol:.2%}')
print(f'Sharpe Ratio:    {sr:.2f}')
print()
sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
print('Top 10 allocations:')
for t, w in sorted_w[:10]:
    amt = w * 500000
    print(f'  {t:>20s}  {w:.1%}  (Rs {amt:>10,.0f})')
print('...')
print('Bottom 5:')
for t, w in sorted_w[-5:]:
    amt = w * 500000
    print(f'  {t:>20s}  {w:.1%}  (Rs {amt:>10,.0f})')
total = sum(weights.values())
unique = len(set(round(w,4) for w in weights.values()))
print(f'Total weight: {total:.4f}')
print(f'Unique weight levels: {unique}')
