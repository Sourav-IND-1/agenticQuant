"""
backend/llm/gemini.py
Extracts structured investment parameters from natural language using Gemini 1.5 Pro
with response_schema enforcement, plus a heuristic regex fallback.

Inputs:
    1. user_input  — raw natural language string
    2. quant_context — dict from quant_context.py

Output:
    {
        "capital": float,
        "horizon_days": int,
        "risk_tolerance": "conservative" | "moderate" | "aggressive",
        "views": [{"ticker": str, "type": "absolute", "expected_return": float}]
    }
"""

import json
import re
import requests
import urllib3
from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# Suppress InsecureRequestWarning when using verify=False behind corporate proxies
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Groq API endpoint (OpenAI compatible)
GROQ_API_BASE = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_CHAIN = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

# JSON Schema definition (injected into prompt for Groq JSON mode)
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "capital": {"type": "number", "description": "Investment capital in INR (Indian Rupees). Can be 0 if current_holdings provided."},
        "horizon_days": {"type": "integer", "description": "Investment horizon in days"},
        "risk_tolerance": {
            "type": "string",
            "enum": ["conservative", "moderate", "aggressive"],
            "description": "Risk tolerance level"
        },
        "max_sell_pct": {
            "type": "number",
            "description": "Maximum percentage of portfolio to sell as decimal (e.g. 0.30 for 30%)"
        },
        "current_holdings": {
            "type": "array",
            "description": "List of current holdings with either exact shares or total value.",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, TCS.NS, RELIANCE.NS)"},
                    "shares": {"type": "number", "description": "Number of shares owned (if specified)"},
                    "value": {"type": "number", "description": "Total INR value of the holding (if specified, e.g. 15000 for 15k)"},
                    "avg_cost": {"type": "number", "description": "Average cost basis if known, else 0"}
                },
                "required": ["ticker"]
            }
        },
        "views": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "type": {"type": "string", "enum": ["absolute"]},
                    "expected_return": {
                        "type": "number",
                        "description": "Annualized expected return as decimal (e.g. 0.12 for 12%)"
                    }
                },
                "required": ["ticker", "type", "expected_return"]
            },
            "description": "List of subjective return views per ticker"
        }
    },
    "required": ["capital", "horizon_days", "risk_tolerance", "views", "max_sell_pct", "current_holdings"]
}


def _build_prompt(user_input: str, quant_context: Dict[str, Any]) -> str:
    """Construct the prompt injecting quant_context and JSON schema."""

    ctx_lines = []
    for ticker, metrics in quant_context.items():
        if not isinstance(metrics, dict):
            continue
        ctx_lines.append(
            f"  {ticker}: vol={metrics.get('annual_vol', 'N/A')}, "
            f"beta={metrics.get('beta', 'N/A')}, "
            f"sharpe={metrics.get('sharpe', 'N/A')}, "
            f"momentum_20d={metrics.get('momentum_20d', 'N/A')}, "
            f"capm_expected_return={metrics.get('expected_return_capm', 'N/A')}"
        )
    ctx_block = "\n".join(ctx_lines) if ctx_lines else "  No quantitative context available."

    schema_str = json.dumps(RESPONSE_SCHEMA, indent=2)

    return f"""You are a quantitative finance AI. Extract structured investment parameters from the user's natural language goal.

=== QUANTITATIVE CONTEXT (ground your views in these numbers) ===
{ctx_block}

=== INSTRUCTIONS ===
1. Extract capital (INR ₹), horizon (days), and risk tolerance from the user's text. Treat all monetary values as Indian Rupees. If user says "lakh" or "L", multiply by 100000. If user says "crore" or "Cr", multiply by 10000000.
2. Extract the user's current holdings. If they mention conversational names like "infy", "infosys", "reliance", "tcs", "tata motors", "hdfc", "sbi", "axis", "icici", "bajaj", "maruti", "titan", "asian paints", map them to the official NSE tickers in this universe: {config.TICKERS}.
   - If they say a rupee amount (e.g. "15k in TCS"), extract it as 'value': 15000.
   - If they say shares (e.g. "100 shares of Reliance"), extract it as 'shares': 100.
   - Default avg_cost to 0 if not provided.
3. Extract max_sell_pct if specified (e.g., "don't sell more than 30%" -> 0.30). Default to 1.0 if not specified.
4. For each ticker the user mentions with a view (universe: {config.TICKERS}), generate an "expected_return" view.
5. GROUND your expected_return views in the provided volatility and beta numbers:
   - High-beta stocks should have wider return ranges.
   - Use CAPM expected return as the base, then adjust based on user sentiment.
   - Cap aggressive bullish views at capm_return + 2× annual_vol.
   - Cap bearish views at capm_return - 1.5× annual_vol.
6. If the user doesn't specify capital, default to 0.0 (it will be calculated from holdings).
7. If the user doesn't specify horizon, default to 180 days.
8. If the user doesn't specify risk, default to "moderate".

=== REQUIRED JSON SCHEMA ===
You MUST return ONLY a JSON object that strictly conforms to the following schema:
{schema_str}

=== USER INPUT ===
"{user_input}"
"""


def _call_llm_api(prompt: str, timeout: float = 15.0) -> Dict[str, Any]:
    """Call Groq API using JSON mode."""

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    last_error = None
    for model_name in GROQ_MODEL_CHAIN:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"}
        }

        try:
            resp = requests.post(GROQ_API_BASE, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()

            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]

            print(f"[llm] Success with model: {model_name}")
            return json.loads(raw_text.strip())

        except requests.exceptions.HTTPError as e:
            last_error = f"{model_name} HTTP {resp.status_code} - {e.response.text if hasattr(e, 'response') else ''}"
            print(f"[llm debug] Error on {model_name}: {last_error}")
            continue
        except Exception as e:
            last_error = f"{model_name}: {e}"
            print(f"[llm debug] Exception on {model_name}: {last_error}")
            continue

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")


# ---------------------------------------------------------------------------
# Heuristic fallback
# ---------------------------------------------------------------------------

def _heuristic_fallback(user_input: str, quant_context: Dict[str, Any]) -> Dict[str, Any]:
    """Regex + rule-based fallback activated when Gemini API is unavailable.

    Parses common patterns:
        - Dollar amounts:  "$10k", "$100,000", "10000 dollars"
        - Horizon:         "6 months", "1 year", "90 days"
        - Risk words:      "aggressive", "conservative", "moderate"
        - Ticker mentions: any of AAPL MSFT GOOGL NVDA XOM JPM
    """
    text = user_input.lower()

    # --- Capital extraction ---------------------------------------------------
    capital = 50000.0
    # Match patterns like "$100k", "$10,000", "50000 dollars", "$1.5m"
    cap_patterns = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|thousand|m|million|b|billion)?',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|thousand|m|million|b|billion)?\s*(?:dollars?|usd)',
    ]
    for pat in cap_patterns:
        cap_match = re.search(pat, text)
        if cap_match:
            val_str = cap_match.group(1).replace(',', '')
            try:
                val = float(val_str)
                mult = cap_match.group(2)
                if mult in ('k', 'thousand'):
                    val *= 1_000
                elif mult in ('m', 'million'):
                    val *= 1_000_000
                elif mult in ('b', 'billion'):
                    val *= 1_000_000_000
                if val >= 100:
                    capital = val
            except ValueError:
                pass
            break

    # --- Horizon extraction ---------------------------------------------------
    horizon_days = 180
    hor_match = re.search(r'(\d+)\s*(day|week|month|year)s?', text)
    if hor_match:
        num = int(hor_match.group(1))
        unit = hor_match.group(2)
        if unit == 'day':
            horizon_days = num
        elif unit == 'week':
            horizon_days = num * 7
        elif unit == 'month':
            horizon_days = num * 30
        elif unit == 'year':
            horizon_days = num * 365

    # --- Risk tolerance extraction --------------------------------------------
    risk_tolerance = "moderate"
    aggressive_words = ['aggressive', 'high risk', 'growth', 'max return', 'yolo', 'risky']
    conservative_words = ['conservative', 'low risk', 'safe', 'capital preservation', 'stable', 'defensive']
    if any(w in text for w in aggressive_words):
        risk_tolerance = "aggressive"
    elif any(w in text for w in conservative_words):
        risk_tolerance = "conservative"

    # --- Ticker view extraction (grounded in quant_context) -------------------
    bullish_words = ['bullish', 'surge', 'outperform', 'up', 'buy', 'long', 'double', 'moon', 'rally']
    bearish_words = ['bearish', 'drop', 'underperform', 'down', 'sell', 'short', 'crash', 'decline']

    views = []
    for ticker in config.TICKERS:
        if ticker.lower() in text or ticker in user_input:
            ctx = quant_context.get(ticker, {})
            base_ret = ctx.get("expected_return_capm", ctx.get("capm_expected_return", 0.08))
            vol = ctx.get("annual_vol", ctx.get("annualized_volatility", 0.20))
            beta = ctx.get("beta", 1.0)

            # Ground views in volatility and beta
            if any(w in text for w in bullish_words):
                # Bullish: base + scaled adjustment capped at capm + 2×vol
                exp_ret = min(base_ret + 1.5 * vol, base_ret + 2.0 * vol)
            elif any(w in text for w in bearish_words):
                # Bearish: base - scaled adjustment floored at capm - 1.5×vol
                exp_ret = max(base_ret - 1.2 * vol, base_ret - 1.5 * vol)
            else:
                # Neutral: slight alpha over CAPM scaled by beta
                exp_ret = base_ret + 0.02 * beta

            views.append({
                "ticker": ticker,
                "type": "absolute",
                "expected_return": round(float(exp_ret), 4)
            })
            
    # --- Max Sell Pct extraction ---
    max_sell_pct = 1.0
    pct_match = re.search(r'not sell more than (\d+)', text)
    if pct_match:
        max_sell_pct = float(pct_match.group(1)) / 100.0

    return {
        "capital": capital,
        "horizon_days": horizon_days,
        "risk_tolerance": risk_tolerance,
        "max_sell_pct": max_sell_pct,
        "current_holdings": [],
        "views": views
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_investment_brief(user_input: str, quant_context: Dict[str, Any],
                             ml_predictions: Dict[str, Any] = None,
                             regime: str = "Unknown") -> Dict[str, Any]:
    """Extract structured investment brief from natural language.

    Tries Gemini 1.5 Pro first (with response_schema). Falls back to heuristic
    regex parser if:
        - API key is missing
        - Gemini API call fails (network error, timeout, quota)
        - JSON parsing fails
    """

    # Guard: no API key → immediate fallback
    if not config.GROQ_API_KEY:
        print("[llm] No GROQ_API_KEY set — using heuristic fallback.")
        result = _heuristic_fallback(user_input, quant_context)
    else:
        try:
            prompt = _build_prompt(user_input, quant_context)
            result = _call_llm_api(prompt, timeout=15.0)

        except requests.exceptions.Timeout:
            print("[llm] Network timeout — using heuristic fallback.")
            result = _heuristic_fallback(user_input, quant_context)

        except requests.exceptions.HTTPError as e:
            print(f"[llm] HTTP error {e.response.status_code} — using heuristic fallback.")
            result = _heuristic_fallback(user_input, quant_context)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"[llm] Response parsing failed ({e}) — using heuristic fallback.")
            result = _heuristic_fallback(user_input, quant_context)

        except Exception as e:
            print(f"[llm] Unexpected error ({e}) — using heuristic fallback.")
            result = _heuristic_fallback(user_input, quant_context)

    # Validate required fields exist and coerce types
    try:
        result["capital"] = float(result.get("capital", 0.0))
    except (ValueError, TypeError):
        result["capital"] = 0.0
        
    try:
        result["horizon_days"] = int(result.get("horizon_days", 180))
    except (ValueError, TypeError):
        result["horizon_days"] = 180
        
    result.setdefault("risk_tolerance", "moderate")
    
    try:
        result["max_sell_pct"] = float(result.get("max_sell_pct", 1.0))
    except (ValueError, TypeError):
        result["max_sell_pct"] = 1.0
        
    result.setdefault("current_holdings", [])
    result.setdefault("views", [])
    
    for view in result.get("views", []):
        try:
            view["expected_return"] = float(view.get("expected_return", 0.0))
        except (ValueError, TypeError):
            view["expected_return"] = 0.0
    
    # Process current holdings (Convert Gemini Array to expected Backend Dictionary format)
    # and handle value vs shares logic.
    raw_holdings = result.get("current_holdings", [])
    processed_holdings = {}
    
    if isinstance(raw_holdings, list):
        for item in raw_holdings:
            ticker = item.get("ticker")
            if not ticker: continue
                
            try:
                shares = float(item["shares"]) if item.get("shares") is not None else None
            except (ValueError, TypeError):
                shares = None
                
            try:
                value = float(item["value"]) if item.get("value") is not None else None
            except (ValueError, TypeError):
                value = None
            
            # Use real-time price if available, else a fallback guess
            current_price = 100.0
            if ticker in quant_context and "current_price" in quant_context[ticker]:
                 current_price = quant_context[ticker]["current_price"]
                 
            # Convert value to shares if shares aren't explicitly provided
            if shares is None and value is not None:
                 shares = float(value / current_price)
            elif shares is None:
                 shares = 0.0
                 
            try:
                avg_cost = float(item.get("avg_cost", 0.0))
            except (ValueError, TypeError):
                avg_cost = 0.0
                 
            processed_holdings[ticker] = {
                "shares": shares,
                "avg_cost": avg_cost
            }
            
        result["current_holdings"] = processed_holdings

    return result


# ---------------------------------------------------------------------------
# CLI test harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    from backend.data.market_data import get_live_market_data
    from backend.math.quant_context import compute_quant_context

    data = get_live_market_data()
    ctx = compute_quant_context(config.TICKERS, data)

    test_queries = [
        "I have $100k to invest for 1 year. I'm aggressive and very bullish on NVDA and AAPL.",
        "Put $10,000 into safe stocks for 6 months",
        "Invest 50k dollars, bearish on XOM, bullish on GOOGL, 90 days horizon",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        brief = extract_investment_brief(q, ctx)
        print(json.dumps(brief, indent=2))
