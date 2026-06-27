import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.data.market_data import get_live_market_data
from backend.math.quant_context import compute_quant_context
from backend.regime.hmm_detector import detect_market_regime
from backend.ml.predictor import predict_alphas
from backend.llm.gemini import extract_investment_brief
from backend.validation.math_validator import validate_and_format_views
from backend.quant.optimizer import optimize_portfolio
from backend.database.db_operations import save_strategy_run
import traceback

try:
    print("1. market data")
    market_data = get_live_market_data()
    print("2. quant context")
    quant_ctx = compute_quant_context(["AAPL", "GOOGL", "MSFT", "NVDA", "XOM", "JPM"], market_data)
    print("3. regime")
    regime = detect_market_regime(market_data)
    print("4. ml preds")
    ml_preds = predict_alphas(market_data)
    print("5. brief")
    prompt = "Invest $50k over 1 year with moderate risk. Expecting AAPL and GOOGL to outperform."
    brief = extract_investment_brief(prompt, quant_ctx, ml_preds, regime)
    print("6. validate")
    P, Q, validated_views = validate_and_format_views(brief, quant_ctx)
    brief["views"] = validated_views
    print("7. optimize")
    weights, metrics = optimize_portfolio(quant_ctx, P, Q, brief)
    results = {
        "weights": weights,
        "metrics": metrics,
        "featureImportances": [],
        "backtest": []
    }
    print("8. save")
    save_strategy_run(prompt, regime, brief, results)
    print("DONE")
except Exception as e:
    traceback.print_exc()
