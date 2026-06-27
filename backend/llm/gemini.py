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

# Gemini REST endpoint — uses direct HTTP to bypass gRPC SSL certificate interception
# Model fallback chain: try gemini-1.5-pro first (per spec), then available alternatives
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODEL_CHAIN = [
    "gemini-1.5-pro",       # Spec-requested model
    "gemini-2.5-flash",     # Best available alternative
    "gemini-2.0-flash",     # Widely available fallback
]

# JSON Schema enforced via Gemini response_schema (structured output)
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "capital": {"type": "number", "description": "Investment capital in USD. Can be 0 if current_holdings provided."},
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
            "type": "object",
            "description": "Mapping of ticker symbol to its holdings data",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "shares": {"type": "number"},
                    "avg_cost": {"type": "number"}
                },
                "required": ["shares", "avg_cost"]
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
    """Construct the Gemini prompt injecting quant_context as formatted JSON context."""

    # Format quant context into a readable block for the LLM
    ctx_lines = []
    for ticker, metrics in quant_context.items():
        if not isinstance(metrics, dict):
            continue
        ctx_lines.append(
            f"  {ticker}: vol={metrics.get('annual_vol', 'N/A')}, "
            f"beta={metrics.get('beta', 'N/A')}, "
            f"sharpe={metrics.get('sharpe', 'N/A')}, "
            f"momentum_20d={metrics.get('momentum_20d', 'N/A')}, "
            f"momentum_60d={metrics.get('momentum_60d', 'N/A')}, "
            f"capm_expected_return={metrics.get('expected_return_capm', 'N/A')}"
        )
    ctx_block = "\n".join(ctx_lines) if ctx_lines else "  No quantitative context available."

    return f"""You are a quantitative finance AI. Extract structured investment parameters from the user's natural language goal.

=== QUANTITATIVE CONTEXT (ground your views in these numbers) ===
{ctx_block}

=== INSTRUCTIONS ===
1. Extract capital (USD), horizon (days), and risk tolerance from the user's text.
2. Extract the user's current holdings. For each holding, extract the ticker, shares, and avg_cost. If they hold a stock but no cost is given, use 0 for avg_cost.
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

=== USER INPUT ===
"{user_input}"

Return a JSON object with: capital (float), horizon_days (int), risk_tolerance (string), max_sell_pct (float), current_holdings (object mapping ticker to shares and avg_cost), and views (array of objects with ticker, type="absolute", expected_return as float)."""


def _call_gemini_api(prompt: str, timeout: float = 15.0) -> Dict[str, Any]:
    """Call Gemini via REST with response_schema. Tries each model in GEMINI_MODEL_CHAIN."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA
        }
    }

    last_error = None
    for model_name in GEMINI_MODEL_CHAIN:
        url = f"{GEMINI_API_BASE}/{model_name}:generateContent?key={config.GEMINI_API_KEY}"
        try:
            resp = requests.post(url, json=payload, timeout=timeout, verify=False)
            if resp.status_code == 404:
                # Model not available on this key, try next
                last_error = f"{model_name} returned 404"
                continue
            resp.raise_for_status()

            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

            # Parse JSON (response_schema guarantees valid JSON, but be safe)
            text = raw_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            print(f"[gemini] Success with model: {model_name}")
            return json.loads(text.strip())

        except requests.exceptions.HTTPError:
            last_error = f"{model_name} HTTP {resp.status_code}"
            continue
        except Exception as e:
            last_error = f"{model_name}: {e}"
            continue

    # All models in chain failed
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


# ---------------------------------------------------------------------------
# Heuristic regex fallback
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
        "current_holdings": {},
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
    if not config.GEMINI_API_KEY:
        print("[gemini] No GEMINI_API_KEY set — using heuristic fallback.")
        return _heuristic_fallback(user_input, quant_context)

    try:
        prompt = _build_prompt(user_input, quant_context)
        result = _call_gemini_api(prompt, timeout=15.0)

        # Validate required fields exist
        result.setdefault("capital", 0.0)
        result.setdefault("horizon_days", 180)
        result.setdefault("risk_tolerance", "moderate")
        result.setdefault("max_sell_pct", 1.0)
        result.setdefault("current_holdings", {})
        result.setdefault("views", [])

        return result

    except requests.exceptions.Timeout:
        print("[gemini] Network timeout — using heuristic fallback.")
        return _heuristic_fallback(user_input, quant_context)

    except requests.exceptions.HTTPError as e:
        print(f"[gemini] HTTP error {e.response.status_code} — using heuristic fallback.")
        return _heuristic_fallback(user_input, quant_context)

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"[gemini] Response parsing failed ({e}) — using heuristic fallback.")
        return _heuristic_fallback(user_input, quant_context)

    except Exception as e:
        print(f"[gemini] Unexpected error ({e}) — using heuristic fallback.")
        return _heuristic_fallback(user_input, quant_context)


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
