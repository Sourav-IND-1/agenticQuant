"""
backend/database/db_operations.py

Database persistence layer supporting Supabase cloud database and in-memory local cache.
Handles saving queries, portfolio allocations, backtest equity curves, and retrieving joined run history.
"""

from typing import Dict, Any, List, Union
from pathlib import Path
import sys
import datetime
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from backend.database.supabase_client import get_supabase_client

# In-memory local cache tables for offline mode / fast fallback
_LOCAL_QUERIES: List[Dict[str, Any]] = []
_LOCAL_PORTFOLIOS: List[Dict[str, Any]] = []
_LOCAL_BACKTESTS: List[Dict[str, Any]] = []
_LOCAL_JOINED_HISTORY: List[Dict[str, Any]] = []


def save_query(user_input: str, gemini_output: Dict[str, Any]) -> str:
    """Saves natural language query and extracted NLP parameters. Returns query_id."""
    query_id = str(uuid.uuid4())[:8]
    client = get_supabase_client()
    
    record = {
        "id": query_id,
        "created_at": datetime.datetime.now().isoformat(),
        "user_input": user_input,
        "capital": gemini_output.get("capital", 100000.0),
        "horizon_days": gemini_output.get("horizon_days", 180),
        "risk_tolerance": gemini_output.get("risk_tolerance", "moderate"),
        "views": gemini_output.get("views", [])
    }
    
    if client:
        try:
            client.table("queries").insert(record).execute()
        except Exception as e:
            print(f"[db_operations] Supabase queries insert fallback: {e}")
            
    _LOCAL_QUERIES.insert(0, record)
    return query_id


def save_portfolio(
    query_id: str,
    weights: Dict[str, float],
    risk_metrics: Dict[str, Any],
    regime: Union[str, Dict[str, Any]],
    ml_signals: Dict[str, Any]
) -> str:
    """Saves final optimized portfolio allocation and risk metrics. Returns portfolio_id."""
    portfolio_id = str(uuid.uuid4())[:8]
    client = get_supabase_client()
    
    reg_str = regime.get("regime", "Neutral") if isinstance(regime, dict) else str(regime)
    
    record = {
        "id": portfolio_id,
        "query_id": query_id,
        "created_at": datetime.datetime.now().isoformat(),
        "regime": reg_str,
        "weights": weights,
        "expected_return": risk_metrics.get("annualized_return", risk_metrics.get("expectedReturn", 0.15)),
        "volatility": risk_metrics.get("annualized_vol", risk_metrics.get("volatility", 0.10)),
        "sharpe_ratio": risk_metrics.get("sharpe", 1.5),
        "cvar_95": risk_metrics.get("cvar_95", 0.0),
        "max_drawdown": risk_metrics.get("max_drawdown", 0.0),
        "cagr": risk_metrics.get("cagr", 0.0),
        "win_rate": risk_metrics.get("win_rate", 0.5)
    }
    
    if client:
        try:
            client.table("portfolios").insert(record).execute()
        except Exception as e:
            print(f"[db_operations] Supabase portfolios insert fallback: {e}")
            
    _LOCAL_PORTFOLIOS.insert(0, record)
    return portfolio_id


def save_backtest(portfolio_id: str, equity_curve: List[Dict[str, Any]], *args) -> str:
    """Saves walk-forward backtest equity curve. Returns backtest_id."""
    backtest_id = str(uuid.uuid4())[:8]
    client = get_supabase_client()
    
    record = {
        "id": backtest_id,
        "portfolio_id": portfolio_id,
        "created_at": datetime.datetime.now().isoformat(),
        "data_points": len(equity_curve),
        "equity_curve": equity_curve[:100]  # Store subset or full curve
    }
    
    if client:
        try:
            client.table("backtests").insert(record).execute()
        except Exception as e:
            print(f"[db_operations] Supabase backtests insert fallback: {e}")
            
    _LOCAL_BACKTESTS.insert(0, record)
    
    # Also construct joined record for fast history retrieval
    _build_joined_history_record(portfolio_id, equity_curve)
    return backtest_id


def _build_joined_history_record(portfolio_id: str, equity_curve: List[Dict[str, Any]]):
    """Helper to join query + portfolio + backtest into unified record."""
    port = next((p for p in _LOCAL_PORTFOLIOS if p["id"] == portfolio_id), {})
    query_id = port.get("query_id", "")
    query = next((q for q in _LOCAL_QUERIES if q["id"] == query_id), {})
    
    joined = {
        "id": portfolio_id,
        "timestamp": port.get("created_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "prompt": query.get("user_input", "Automated Strategy"),
        "regime": port.get("regime", "Neutral"),
        "capital": query.get("capital", 100000.0),
        "expected_return": port.get("expected_return", 0.15),
        "sharpe_ratio": port.get("sharpe_ratio", 1.5),
        "weights": port.get("weights", {}),
        "query": query,
        "portfolio": port,
        "backtest": {"equity_curve": equity_curve}
    }
    _LOCAL_JOINED_HISTORY.insert(0, joined)


def save_strategy_run(prompt: str, regime: str, brief: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
    """Backward-compatible helper wrapping query/portfolio/backtest saves."""
    qid = save_query(prompt, brief)
    pid = save_portfolio(qid, results.get("weights", {}), results.get("metrics", {}), regime, {})
    save_backtest(pid, results.get("metrics", {}).get("equity_curve", []))
    return _LOCAL_JOINED_HISTORY[0] if _LOCAL_JOINED_HISTORY else {}


def get_strategy_history(limit: int = 5) -> List[Dict[str, Any]]:
    """Return last `limit` strategy runs from Supabase joining queries + portfolios + backtests."""
    client = get_supabase_client()
    if client:
        try:
            # Query joined tables if configured or fetch portfolios and attach queries
            res = client.table("portfolios").select("*").order("created_at", desc=True).limit(limit).execute()
            if res.data and len(res.data) > 0:
                joined_list = []
                for p in res.data:
                    qid = p.get("query_id")
                    pid = p.get("id")
                    
                    q_res = client.table("queries").select("*").eq("id", qid).execute() if qid else None
                    q_data = q_res.data[0] if (q_res and q_res.data) else {}
                    
                    b_res = client.table("backtests").select("*").eq("portfolio_id", pid).execute() if pid else None
                    b_data = b_res.data[0] if (b_res and b_res.data) else {}
                    
                    joined_list.append({
                        "id": pid,
                        "timestamp": p.get("created_at", ""),
                        "prompt": q_data.get("user_input", "Strategy Run"),
                        "regime": p.get("regime", "Neutral"),
                        "capital": q_data.get("capital", 100000.0),
                        "expected_return": p.get("expected_return", 0.15),
                        "sharpe_ratio": p.get("sharpe_ratio", 1.5),
                        "weights": p.get("weights", {}),
                        "query": q_data,
                        "portfolio": p,
                        "backtest": b_data
                    })
                return joined_list
        except Exception as e:
            print(f"[db_operations] Supabase history join query fallback: {e}")
            
    return _LOCAL_JOINED_HISTORY[:limit]


if __name__ == "__main__":
    qid = save_query("Test input", {"capital": 100000, "views": []})
    pid = save_portfolio(qid, {"AAPL": 0.5, "NVDA": 0.5}, {"sharpe": 2.1}, "Bull", {})
    bid = save_backtest(pid, [{"date": "2024-01-01", "strategy": 100, "spy": 100}])
    print("History:", get_strategy_history(2))
