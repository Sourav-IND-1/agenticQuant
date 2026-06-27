from typing import Dict, Any, List
from pathlib import Path
import sys
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.supabase_client import get_supabase_client

# In-memory local cache fallback
_LOCAL_HISTORY = []

def save_strategy_run(prompt: str, regime: str, brief: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a quantitative strategy analysis run to Supabase or local cache."""
    client = get_supabase_client()
    
    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prompt": prompt,
        "regime": regime,
        "capital": brief.get("capital", 100000),
        "expected_return": results.get("metrics", {}).get("expectedReturn", 0.15),
        "sharpe_ratio": results.get("metrics", {}).get("sharpeRatio", 2.0),
        "weights": results.get("weights", {})
    }
    
    if client:
        try:
            res = client.table("strategy_runs").insert(record).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"Supabase insert fallback: {e}")
            
    _LOCAL_HISTORY.insert(0, record)
    return record

def get_strategy_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves past saved strategy analysis runs."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("strategy_runs").select("*").order("id", desc=True).limit(limit).execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"Supabase select fallback: {e}")
            
    return _LOCAL_HISTORY[:limit]

if __name__ == "__main__":
    rec = save_strategy_run("Test Supabase Run", "Bull", {"capital": 50000}, {"metrics": {"expectedReturn": 0.18, "sharpeRatio": 2.4}})
    print("Saved Record:", rec)
