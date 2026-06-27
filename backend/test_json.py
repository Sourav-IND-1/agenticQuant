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
import json
import traceback

try:
    market_data = get_live_market_data()
    quant_ctx = compute_quant_context(["AAPL", "GOOGL", "MSFT", "NVDA", "XOM", "JPM"], market_data)
    regime = detect_market_regime(market_data)
    ml_preds = predict_alphas(market_data)
    prompt = "Invest $50k over 1 year with moderate risk. Expecting AAPL and GOOGL to outperform."
    brief = extract_investment_brief(prompt, quant_ctx, ml_preds, regime)
    P, Q, validated_views = validate_and_format_views(brief, quant_ctx)
    brief["views"] = validated_views
    weights, metrics = optimize_portfolio(quant_ctx, P, Q, brief)
    results = {
        "status": "success",
        "regime": regime,
        "brief": brief,
        "results": {
            "weights": weights,
            "metrics": metrics,
            "featureImportances": [],
            "backtest": []
        }
    }
    print("Testing JSON serialization...")
    json.dumps(results)
    print("DONE")
except Exception as e:
    traceback.print_exc()
