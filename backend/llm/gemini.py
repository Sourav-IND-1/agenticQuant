import json
import re
from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

try:
    import google.generativeai as genai
except ImportError:
    genai = None

def _heuristic_fallback_extract(user_input: str, quant_context: Dict[str, Any], ml_predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Intelligent regex and rule-based fallback if Gemini API is unconfigured or offline."""
    text = user_input.lower()
    
    # Capital extraction
    capital = 50000.0
    cap_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|thousand|m|million)?', text)
    if cap_match:
        val_str = cap_match.group(1).replace(',', '')
        try:
            val = float(val_str)
            mult = cap_match.group(2)
            if mult in ['k', 'thousand']: val *= 1000
            elif mult in ['m', 'million']: val *= 1000000
            if val >= 500: capital = val
        except ValueError:
            pass
            
    # Horizon extraction
    horizon_days = 180
    hor_match = re.search(r'(\d+)\s*(day|week|month|year)s?', text)
    if hor_match:
        num = int(hor_match.group(1))
        unit = hor_match.group(2)
        if unit == 'day': horizon_days = num
        elif unit == 'week': horizon_days = num * 7
        elif unit == 'month': horizon_days = num * 30
        elif unit == 'year': horizon_days = num * 365
        
    # Risk tolerance extraction
    risk_tolerance = "moderate"
    if any(w in text for w in ['aggressive', 'high risk', 'growth', 'max return']):
        risk_tolerance = "aggressive"
    elif any(w in text for w in ['conservative', 'low risk', 'safe', 'capital preservation']):
        risk_tolerance = "conservative"
        
    # Extract ticker views
    views = []
    for ticker in config.TICKERS:
        if ticker.lower() in text or ticker in user_input:
            ctx = quant_context.get(ticker, {})
            ml = ml_predictions.get(ticker, {})
            base_ret = ctx.get("capm_expected_return", 0.08)
            alpha = ml.get("expected_alpha", 0.02)
            
            # Adjust view based on sentiment words
            if any(w in text for w in ['bullish', 'surge', 'outperform', 'up', 'buy', 'double']):
                exp_ret = base_ret + abs(alpha) + 0.04
            elif any(w in text for w in ['bearish', 'drop', 'underperform', 'down', 'sell']):
                exp_ret = max(-0.15, base_ret - abs(alpha) - 0.04)
            else:
                exp_ret = base_ret + alpha
                
            views.append({
                "ticker": ticker,
                "type": "absolute",
                "expected_return": round(float(exp_ret), 4)
            })
            
    return {
        "risk_tolerance": risk_tolerance,
        "capital": capital,
        "horizon_days": horizon_days,
        "views": views
    }

def extract_investment_brief(user_input: str, quant_context: Dict[str, Any], ml_predictions: Dict[str, Any], regime: str) -> Dict[str, Any]:
    """Extracts structured investment goals and views using Gemini with intelligent heuristic fallback."""
    if not config.GEMINI_API_KEY or genai is None:
        return _heuristic_fallback_extract(user_input, quant_context, ml_predictions)
        
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
You are a quantitative finance AI expert. Analyze the user's natural language investment goal and extract structured parameters.
Context:
- Current Market Regime: {regime}
- Available Universe: {config.TICKERS}
- User Goal: "{user_input}"

Return EXACTLY a valid JSON object matching this schema:
{{
  "risk_tolerance": "conservative" | "moderate" | "aggressive",
  "capital": float (default 50000.0 if not specified),
  "horizon_days": integer (default 180 if not specified),
  "views": [
    {{
      "ticker": string (must be in universe),
      "type": "absolute",
      "expected_return": float (e.g. 0.12 for 12% annualized return)
    }}
  ]
}}
Do not include markdown code formatting like ```json ... ```, output raw JSON only.
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"Gemini API fallback triggered: {e}")
        return _heuristic_fallback_extract(user_input, quant_context, ml_predictions)

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(backend_dir / "math"))
    from quant_context import compute_quant_context
    from data.market_data import get_live_market_data
    from ml.predictor import predict_alphas
    
    data = get_live_market_data()
    ctx = compute_quant_context(data)
    ml = predict_alphas(data)
    
    sample_query = "I have $100k to invest for 1 year. I'm aggressive and very bullish on NVDA and AAPL."
    brief = extract_investment_brief(sample_query, ctx, ml, "Bull")
    print("Extracted Brief JSON:")
    print(json.dumps(brief, indent=2))
