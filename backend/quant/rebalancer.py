"""
backend/quant/rebalancer.py

Module for analyzing existing portfolio holdings and generating rebalancing actions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from backend.quant.risk import compute_risk_metrics

def analyze_current_portfolio(
    holdings: Dict[str, Dict[str, float]], 
    current_prices: Dict[str, float],
    market_data: Dict[str, pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Analyze the current portfolio for value, PnL, concentration, and correlation.
    """
    total_value = 0.0
    ticker_values = {}
    current_weights = {}
    pnl = {}
    
    for ticker, data in holdings.items():
        shares = data.get("shares", 0.0)
        avg_cost = data.get("avg_cost", 0.0)
        price = current_prices.get(ticker, avg_cost)
        if price == 0 and market_data and ticker in market_data and not market_data[ticker].empty:
            val = market_data[ticker]["Close"].iloc[-1]
            if isinstance(val, pd.Series):
                val = val.iloc[0]
            price = float(val)
            
        value = shares * price
        total_value += value
        ticker_values[ticker] = value
        pnl[ticker] = (price - avg_cost) * shares if avg_cost > 0 else 0.0
        
    if total_value > 0:
        current_weights = {t: v / total_value for t, v in ticker_values.items()}
        
    concentration_flags = [t for t, w in current_weights.items() if w > 0.30]
    
    correlation_flags = []
    if market_data and len(current_weights) > 1:
        returns_dict = {}
        for t in current_weights.keys():
            if t in market_data and not market_data[t].empty and "Close" in market_data[t].columns:
                close_s = market_data[t]["Close"]
                if isinstance(close_s, pd.DataFrame):
                    close_s = close_s.iloc[:, 0]
                
                rets = close_s.pct_change().dropna()
                # Ensure it's a 1D Series to prevent pd.DataFrame() from crashing
                if isinstance(rets, pd.DataFrame):
                    rets = rets.iloc[:, 0]
                returns_dict[t] = rets
                
        if returns_dict:
            corr_matrix = pd.DataFrame(returns_dict).corr()
            tickers = list(corr_matrix.columns)
            for i in range(len(tickers)):
                for j in range(i+1, len(tickers)):
                    if corr_matrix.iloc[i, j] > 0.80:
                        correlation_flags.append(f"{tickers[i]} & {tickers[j]}")
                        
    health_score = 10
    health_score -= len(concentration_flags)
    health_score -= len(correlation_flags)
    health_score = max(1, min(10, health_score))
    
    return {
        "total_value": round(total_value, 2),
        "current_weights": {k: round(v, 4) for k, v in current_weights.items()},
        "pnl": {k: round(v, 2) for k, v in pnl.items()},
        "concentration_risk": concentration_flags,
        "correlation_warning": correlation_flags,
        "health_score": health_score
    }


def generate_rebalancing_actions(
    current_holdings: Dict[str, Dict[str, float]], 
    target_weights: Dict[str, float], 
    current_prices: Dict[str, float], 
    max_sell_pct: float
) -> List[Dict[str, Any]]:
    """
    Compare current weights vs Black-Litterman target weights and output exact actions.
    """
    # Calculate total value and current weights
    total_value = 0.0
    ticker_values = {}
    for ticker, data in current_holdings.items():
        shares = data.get("shares", 0.0)
        avg_cost = data.get("avg_cost", 0.0)
        price = current_prices.get(ticker, avg_cost)
        val = shares * price
        ticker_values[ticker] = val
        total_value += val
        
    if total_value == 0:
        actions = []
        for t, w in target_weights.items():
            if w > 0.01:
                actions.append({
                    "ticker": t,
                    "action": "BUY",
                    "dollar_amount": 0, 
                    "reason": "New allocation"
                })
        return actions

    current_weights = {t: v / total_value for t, v in ticker_values.items()}
    
    all_tickers = set(current_weights.keys()).union(set(target_weights.keys()))
    
    raw_actions = []
    total_sell_amount_proposed = 0.0
    
    for ticker in all_tickers:
        curr_w = current_weights.get(ticker, 0.0)
        tgt_w = target_weights.get(ticker, 0.0)
        
        curr_val = ticker_values.get(ticker, 0.0)
        tgt_val = total_value * tgt_w
        
        diff_w = tgt_w - curr_w
        dollar_diff = tgt_val - curr_val
        
        if tgt_w < 1e-4 and curr_w > 0:
            raw_actions.append({
                "ticker": ticker,
                "action": "SELL FULL",
                "dollar_amount": curr_val,
                "reason": "Stock not in target portfolio"
            })
            total_sell_amount_proposed += curr_val
        elif diff_w < -0.01:
            raw_actions.append({
                "ticker": ticker,
                "action": "SELL PARTIAL",
                "dollar_amount": abs(dollar_diff),
                "reason": f"Overweight by {abs(diff_w)*100:.1f}%"
            })
            total_sell_amount_proposed += abs(dollar_diff)
        elif diff_w > 0.01:
            raw_actions.append({
                "ticker": ticker,
                "action": "BUY MORE",
                "dollar_amount": dollar_diff,
                "reason": f"Underweight by {diff_w*100:.1f}%"
            })
        else:
            if curr_w > 0 or tgt_w > 0:
                raw_actions.append({
                    "ticker": ticker,
                    "action": "HOLD",
                    "dollar_amount": curr_val,
                    "reason": "Within 1% of target"
                })

    max_sell_dollars = total_value * max_sell_pct
    
    scale_factor = 1.0
    if total_sell_amount_proposed > max_sell_dollars and total_sell_amount_proposed > 0:
        scale_factor = max_sell_dollars / total_sell_amount_proposed
        
    final_actions = []
    for action in raw_actions:
        act = action["action"]
        amt = action["dollar_amount"]
        
        if "SELL" in act:
            amt = amt * scale_factor
        elif "BUY" in act:
            amt = amt * scale_factor
            
        final_actions.append({
            "ticker": action["ticker"],
            "action": act,
            "dollar_amount": round(amt, 2),
            "reason": action["reason"] + (f" (Scaled by {scale_factor:.2f} due to max sell limit)" if scale_factor < 1.0 and "HOLD" not in act else "")
        })
        
    return final_actions


def calculate_before_after_metrics(
    current_holdings: Dict[str, Dict[str, float]], 
    new_weights: Dict[str, float], 
    market_data: Dict[str, pd.DataFrame],
    current_prices: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate risk metrics for BOTH current and recommended portfolio.
    """
    total_value = 0.0
    ticker_values = {}
    for ticker, data in current_holdings.items():
        shares = data.get("shares", 0.0)
        avg_cost = data.get("avg_cost", 0.0)
        price = current_prices.get(ticker, avg_cost)
        if price == 0 and market_data and ticker in market_data and not market_data[ticker].empty:
            val = market_data[ticker]["Close"].iloc[-1]
            if isinstance(val, pd.Series):
                val = val.iloc[0]
            price = float(val)
        val = shares * price
        ticker_values[ticker] = val
        total_value += val
        
    if total_value > 0:
        current_weights = {t: v / total_value for t, v in ticker_values.items()}
    else:
        current_weights = {}

    before_metrics = compute_risk_metrics(current_weights, market_data, capital=total_value if total_value > 0 else 100000.0)
    after_metrics = compute_risk_metrics(new_weights, market_data, capital=total_value if total_value > 0 else 100000.0)
    
    def calc_div(w_dict):
        if not w_dict: return "Low"
        hhi = sum(w**2 for w in w_dict.values())
        if hhi < 0.15: return "High"
        if hhi < 0.25: return "Moderate"
        return "Low"
        
    before_metrics["diversification"] = calc_div(current_weights)
    after_metrics["diversification"] = calc_div(new_weights)

    return {
        "before": before_metrics,
        "after": after_metrics
    }
