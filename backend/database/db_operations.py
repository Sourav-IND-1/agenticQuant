"""
backend/database/db_operations.py

Database persistence layer interfacing with Supabase cloud database and local fallback cache.
Manages inserting queries, updating portfolio allocations, storing backtest curves, and retrieving complete run history.
Matches the exact schema for table 'strategy_runs'.
"""

from typing import Dict, Any, List, Union, Optional
from pathlib import Path
import sys
import datetime
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from backend.database.supabase_client import get_supabase_client

# Local in-memory store fallback mirroring 'strategy_runs' table
_LOCAL_STRATEGY_RUNS: List[Dict[str, Any]] = []


def save_query(user_input: str, extracted_json: Dict[str, Any]) -> str:
    """Inserts initial NLP query and extracted parameters into strategy_runs table. Returns generated uuid."""
    query_id = str(uuid.uuid4())
    client = get_supabase_client()
    
    risk_tol = extracted_json.get("risk_tolerance", "moderate")
    capital = float(extracted_json.get("capital", 100000.0))
    horizon = int(extracted_json.get("horizon_days", 180))
    created_at = datetime.datetime.now().isoformat()
    
    record = {
        "id": query_id,
        "user_input": user_input,
        "extracted_json": extracted_json,
        "risk_tolerance": risk_tol,
        "capital": capital,
        "horizon_days": horizon,
        "created_at": created_at
    }
    
    if client:
        try:
            client.table("strategy_runs").insert(record).execute()
        except Exception as e:
            print(f"[db_operations] Supabase strategy_runs insert fallback: {e}")
            
    _LOCAL_STRATEGY_RUNS.insert(0, record)
    return query_id


def save_portfolio(
    query_id: str,
    weights: Dict[str, float],
    metrics: Dict[str, Any],
    regime: Union[str, Dict[str, Any]],
    ml_signals: Dict[str, Any]
) -> str:
    """Updates strategy_runs row with optimized weights, metrics, regime, and ML signals. Returns portfolio_id."""
    client = get_supabase_client()
    reg_str = regime.get("regime", "Neutral") if isinstance(regime, dict) else str(regime)
    
    update_data = {
        "weights": weights,
        "metrics": metrics,
        "regime": reg_str,
        "ml_signals": ml_signals
    }
    
    if client:
        try:
            client.table("strategy_runs").update(update_data).eq("id", query_id).execute()
        except Exception as e:
            print(f"[db_operations] Supabase strategy_runs portfolio update fallback: {e}")
            
    for item in _LOCAL_STRATEGY_RUNS:
        if item.get("id") == query_id:
            item.update(update_data)
            break
            
    return query_id


def save_backtest(
    portfolio_id: str,
    equity_curve: List[Dict[str, Any]],
    sharpe: float = 0.0,
    cagr: float = 0.0,
    max_drawdown: float = 0.0,
    win_rate: float = 0.5,
    *args,
    **kwargs
):
    """Updates strategy_runs row with backtest simulation equity curve and risk performance ratios."""
    client = get_supabase_client()
    
    update_data = {
        "equity_curve": equity_curve,
        "sharpe": float(sharpe),
        "cagr": float(cagr),
        "max_drawdown": float(max_drawdown),
        "win_rate": float(win_rate)
    }
    
    if client:
        try:
            client.table("strategy_runs").update(update_data).eq("id", portfolio_id).execute()
        except Exception as e:
            print(f"[db_operations] Supabase strategy_runs backtest update fallback: {e}")
            
    for item in _LOCAL_STRATEGY_RUNS:
        if item.get("id") == portfolio_id:
            item.update(update_data)
            break


def get_full_history(limit: int = 5) -> List[Dict[str, Any]]:
    """Selects last N strategy_runs ordered by created_at desc formatted for UI HistoryPanel."""
    client = get_supabase_client()
    raw_runs = []
    
    if client:
        try:
            res = client.table("strategy_runs").select("*").order("created_at", desc=True).limit(limit).execute()
            if res.data and len(res.data) > 0:
                raw_runs = res.data
        except Exception as e:
            print(f"[db_operations] Supabase strategy_runs query fallback: {e}")
            
    if not raw_runs:
        raw_runs = _LOCAL_STRATEGY_RUNS[:limit]
        
    formatted_list = []
    for row in raw_runs:
        weights = row.get("weights") or {}
        top_holding = "None"
        if isinstance(weights, dict) and weights:
            top_holding = max(weights.items(), key=lambda x: x[1])[0]
            
        metrics = row.get("metrics") or {}
        exp_ret = metrics.get("annualized_return", metrics.get("expectedReturn", 0.15))
        sharpe_val = row.get("sharpe") or metrics.get("sharpe", 1.5)
        
        created_str = str(row.get("created_at", ""))[:16].replace("T", " ")
        if not created_str:
            created_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
        formatted_list.append({
            "id": str(row.get("id", "")),
            "timestamp": created_str,
            "created_at": row.get("created_at", ""),
            "prompt": row.get("user_input", "Automated Strategy"),
            "user_input": row.get("user_input", ""),
            "regime": row.get("regime", "Neutral"),
            "risk_tolerance": row.get("risk_tolerance", "moderate"),
            "riskTolerance": row.get("risk_tolerance", "moderate"),
            "capital": float(row.get("capital", 100000.0)),
            "horizon_days": int(row.get("horizon_days", 180)),
            "top_holding": top_holding,
            "expectedReturn": float(exp_ret),
            "sharpeRatio": float(sharpe_val),
            "sharpe": float(sharpe_val),
            "cagr": float(row.get("cagr", 0.0)),
            "max_drawdown": float(row.get("max_drawdown", 0.0)),
            "win_rate": float(row.get("win_rate", 0.5)),
            "weights": weights,
            "metrics": metrics,
            "equity_curve": row.get("equity_curve") or [],
            "ml_signals": row.get("ml_signals") or {}
        })
        
    return formatted_list


# Backward-compatible alias for main.py
get_strategy_history = get_full_history


if __name__ == "__main__":
    qid = save_query("Test Strategy Run", {"risk_tolerance": "aggressive", "capital": 50000, "horizon_days": 90})
    save_portfolio(qid, {"NVDA": 0.6, "AAPL": 0.4}, {"expectedReturn": 0.22, "sharpe": 2.1}, "Bull", {})
    save_backtest(qid, [{"date": "2024-01-01", "strategy": 100, "spy": 100}], sharpe=2.1, cagr=0.25, max_drawdown=-0.08, win_rate=0.62)
    print("History:", get_full_history(2))
