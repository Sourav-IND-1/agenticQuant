from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
from pathlib import Path
import sys

# Ensure project root is on sys.path to avoid collision with standard library 'math'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config
from backend.data.market_data import get_live_market_data
from backend.math.quant_context import compute_quant_context
from backend.regime.hmm_detector import detect_market_regime
from backend.ml.predictor import predict_alphas
from backend.llm.gemini import extract_investment_brief
from backend.validation.math_validator import validate_and_format_views
from backend.quant.optimizer import optimize_portfolio
from backend.database.db_operations import save_strategy_run, get_strategy_history

app = FastAPI(
    title="Quant Trading Intelligence Platform API",
    description="Autonomous Black-Litterman quantitative portfolio management API",
    version="1.0.0"
)

# Enable CORS for React frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": config.ENVIRONMENT, "universe": config.TICKERS}

@app.post("/api/analyze")
def analyze_strategy(req: AnalyzeRequest):
    """Full quantitative pipeline: NLP Brief -> Market Data -> Regime -> ML -> Black-Litterman -> Allocation."""
    try:
        # 1. Fetch live market data (sub-100ms from cache)
        market_data = get_live_market_data()
        
        # 2. Compute foundational quantitative context & rolling correlations
        quant_ctx = compute_quant_context(config.TICKERS, market_data)
        
        # 3. Detect macroeconomic HMM regime
        regime = detect_market_regime(market_data)
        
        # 4. Generate ML alpha predictions & feature importances
        ml_preds = predict_alphas(market_data)
        
        # 5. Extract investment brief & subjective views via Gemini / Heuristic NLP
        brief = extract_investment_brief(req.prompt, quant_ctx, ml_preds, regime)
        
        # 6. Validate views against historical volatility & build Black-Litterman matrices P, Q
        P, Q, validated_views = validate_and_format_views(brief, quant_ctx)
        brief["views"] = validated_views
        
        # 7. Execute mean-variance optimization & compute VaR / Drawdown analytics
        weights, metrics = optimize_portfolio(quant_ctx, P, Q, brief)
        
        results = {
            "weights": weights,
            "metrics": metrics,
            "featureImportances": ml_preds.get("featureImportances", [
                {"feature": "MACD_signal", "importance": 0.24},
                {"feature": "MA20", "importance": 0.18},
                {"feature": "ADX", "importance": 0.14},
                {"feature": "Volume_change", "importance": 0.11}
            ]),
            "backtest": metrics.get("backtest", [])
        }
        
        # 8. Persist run to Supabase cloud storage / local archives
        save_strategy_run(req.prompt, regime, brief, results)
        
        return {
            "status": "success",
            "regime": regime,
            "brief": brief,
            "results": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quantitative calculation failed: {str(e)}")

@app.get("/api/history")
def get_history(limit: int = 20):
    """Retrieve past quantitative strategy runs from Supabase or local cache."""
    return {"status": "success", "history": get_strategy_history(limit)}

if __name__ == "__main__":
    print(f"Starting Quant Trading Intelligence Platform API on port {config.PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
