import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.market_data import get_live_market_data

def run_debug():
    print("Fetching market data...")
    market_data = get_live_market_data()
    df = market_data["TCS.NS"]
    print(f"Columns: {list(df.columns)}")
    print(df.head(2))

    print("\nCalling analyze_current_portfolio...")
    try:
        current_holdings = {
            "TCS.NS": {"shares": 150.0, "avg_cost": 0},
            "INFY.NS": {"shares": 200.0, "avg_cost": 0},
            "HDFCBANK.NS": {"shares": 300.0, "avg_cost": 0}
        }
        current_prices = {"TCS.NS": 3800.0, "INFY.NS": 1500.0, "HDFCBANK.NS": 1600.0}
        portfolio_health = analyze_current_portfolio(current_holdings, current_prices, market_data)
        print("Success:", portfolio_health)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_debug()
