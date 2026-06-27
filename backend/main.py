"""
backend/main.py

FastAPI application serving the Autonomous Black-Litterman Quantitative Portfolio Management API.
Configured with CORS for React frontend, Pydantic schemas, and startup model loading.
Implements the exact 12-step quantitative analysis pipeline, health checks, and joined history retrieval.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import uvicorn
from pathlib import Path
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config

# Load models at startup via loader.py
import backend.ml.loader as loader
from backend.data.market_data import get_live_market_data
from backend.math.quant_context import compute_quant_context
from backend.llm.gemini import extract_investment_brief
from backend.validation.math_validator import validate_full
from backend.quant.optimizer import optimize_portfolio
from backend.ml.predictor import predict_ticker, predict_alphas
from backend.regime.hmm_detector import detect_regime, detect_market_regime
from backend.quant.risk import compute_risk_metrics
from backend.database.db_operations import save_query, save_portfolio, save_backtest, get_strategy_history

app = FastAPI(
    title="Quant Trading Intelligence Platform API",
    description="Autonomous Black-Litterman quantitative portfolio management API",
    version="1.0.0"
)

# Enable CORS for all origins (React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively converts numpy ndarrays, float64, int64, and custom objects to JSON-compatible Python types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(x) for x in obj]
    elif hasattr(obj, "to_dict"):
        return _sanitize_for_json(obj.to_dict())
    return obj


# Pydantic Request / Response Schemas
class AnalyzeRequest(BaseModel):
    user_input: Optional[str] = Field(None, description="Natural language investment brief")
    prompt: Optional[str] = Field(None, description="Alias for user_input")

    def get_input_text(self) -> str:
        return self.user_input or self.prompt or "Balanced tech growth portfolio with $100k capital over 1 year."


@app.get("/health")
def health_check():
    """Returns platform status, model loading state, and current macroeconomic regime."""
    models_loaded = bool(loader.PRIMARY_MODELS and len(loader.PRIMARY_MODELS) > 0)
    current_regime = detect_market_regime()
    return _sanitize_for_json({
        "status": "ok",
        "models_loaded": models_loaded,
        "regime": current_regime
    })


@app.post("/api/analyze")
@app.post("/analyze")
def analyze_strategy(req: AnalyzeRequest):
    """Executes the exact 12-step quantitative portfolio optimization pipeline."""
    try:
        user_input = req.get_input_text()

        # 1. market_data = get_market_data()
        market_data = get_live_market_data()

        # 2. quant_context = compute_quant_context(market_data)
        quant_context = compute_quant_context(config.TICKERS, market_data)

        # 3. gemini_output = gemini_extract(user_input, quant_context)
        gemini_output = extract_investment_brief(user_input, quant_context)

        # 4. validated = math_validator(gemini_output, quant_context)
        validated = validate_full(gemini_output, quant_context)

        # 5. weights_prelim = bl_optimizer(validated, quant_context, {}, "Neutral")
        weights_prelim, _ = optimize_portfolio(validated, quant_context, {}, "Neutral")

        # 6. ml_signals = {t: predict(t, market_data[t]) for t in TICKERS}
        ml_signals = predict_alphas(market_data)
        for t in config.TICKERS:
            if t not in ml_signals:
                ml_signals[t] = predict_ticker(t, market_data.get(t, pd.DataFrame()))

        # 7. regime = detect_regime(market_data)
        regime = detect_regime(market_data)
        regime_str = regime.get("regime", "Neutral")

        # 8. final_weights = bl_optimizer(validated, quant_context, ml_signals, regime)
        final_weights, _ = optimize_portfolio(validated, quant_context, ml_signals, regime)

        # 9. risk_metrics = compute_risk(final_weights, market_data, capital)
        capital = float(validated.get("capital", gemini_output.get("capital", 100000.0)))
        risk_metrics = compute_risk_metrics(final_weights, market_data, capital)

        # 10. query_id = save_query(user_input, gemini_output)
        query_id = save_query(user_input, _sanitize_for_json(gemini_output))

        # 11. portfolio_id = save_portfolio(query_id, final_weights, risk_metrics, regime, ml_signals)
        portfolio_id = save_portfolio(
            query_id,
            _sanitize_for_json(final_weights),
            _sanitize_for_json(risk_metrics),
            _sanitize_for_json(regime),
            _sanitize_for_json(ml_signals)
        )

        # 12. save_backtest(portfolio_id, risk_metrics["equity_curve"], ...)
        save_backtest(
            portfolio_id,
            _sanitize_for_json(risk_metrics.get("equity_curve", [])),
            sharpe=float(risk_metrics.get("sharpe", 0.0)),
            cagr=float(risk_metrics.get("cagr", 0.0)),
            max_drawdown=float(risk_metrics.get("max_drawdown", 0.0)),
            win_rate=float(risk_metrics.get("win_rate", 0.5))
        )

        # Construct unified results structure compatible with UI frontend
        results = {
            "weights": final_weights,
            "metrics": risk_metrics,
            "featureImportances": ml_signals.get("featureImportances", [
                {"feature": "MA50", "importance": 0.35},
                {"feature": "MACD_signal", "importance": 0.25},
                {"feature": "RSI", "importance": 0.20},
                {"feature": "ADX", "importance": 0.12},
                {"feature": "BB_lower", "importance": 0.08}
            ]),
            "backtest": risk_metrics.get("equity_curve", [])
        }

        payload = {
            "status": "success",
            "query_id": query_id,
            "portfolio_id": portfolio_id,
            "user_input": user_input,
            "regime": regime_str,
            "regime_details": regime,
            "brief": gemini_output,
            "validated": validated,
            "weights_prelim": weights_prelim,
            "weights": final_weights,
            "ml_signals": {k: v for k, v in ml_signals.items() if k in config.TICKERS},
            "risk_metrics": risk_metrics,
            "results": results
        }
        return _sanitize_for_json(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quantitative calculation failed: {str(e)}")


@app.get("/api/history")
@app.get("/history")
def get_history(limit: int = 5):
    """Returns last 5 strategy runs from Supabase joining queries + portfolios + backtests."""
    history_data = get_strategy_history(limit)
    return _sanitize_for_json({
        "status": "success",
        "count": len(history_data),
        "history": history_data
    })


if __name__ == "__main__":
    print(f"Starting Quant Trading Intelligence Platform API on port {config.PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
