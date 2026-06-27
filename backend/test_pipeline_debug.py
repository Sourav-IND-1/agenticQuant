import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.data.market_data import get_live_market_data
from backend.math.quant_context import compute_quant_context

market_data = get_live_market_data()
print("AAPL type:", type(market_data["AAPL"]))
print("AAPL empty:", market_data["AAPL"].empty)
if not market_data["AAPL"].empty:
    print("AAPL columns:", market_data["AAPL"].columns)
    ret = market_data["AAPL"]['Close'].pct_change().dropna()
    print("AAPL ret type:", type(ret))
    print("AAPL ret len:", len(ret))
    if len(ret) > 0:
        print("AAPL ret head:", ret.head())

import pandas as pd
returns_dict = {}
for ticker, df in market_data.items():
    if not df.empty and 'Close' in df.columns:
        returns_dict[ticker] = df['Close'].pct_change().dropna()
print("returns_dict keys:", returns_dict.keys())
for k, v in returns_dict.items():
    print(k, type(v), len(v))

try:
    df = pd.DataFrame(returns_dict)
    print("DF shape:", df.shape)
except Exception as e:
    print("ERROR:", str(e))
