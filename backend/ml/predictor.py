import numpy as np
import pandas as pd
from typing import Dict, Any
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
sys.path.append(str(backend_dir / "math"))
from pre_modeling import transform_live_features
from ml.loader import load_ml_models

def predict_alphas(market_data: Dict[str, pd.DataFrame], models: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
    """Generates alpha prediction signals (1 for Up, -1 for Down) weighted by meta-model probability."""
    if models is None:
        models = load_ml_models()
        
    primary_dict = models.get("primary", {})
    meta_dict = models.get("meta", {})
    params_dict = models.get("transform_params", {})
    
    predictions = {}
    for ticker, df in market_data.items():
        if df.empty:
            continue
            
        t_params = params_dict.get(ticker, {})
        X = transform_live_features(df, t_params)
        if X.empty:
            continue
            
        latest_X = X.iloc[[-1]]
        primary_model = primary_dict.get(ticker)
        meta_model = meta_dict.get(ticker)
        
        signal = 1
        confidence = 0.60
        
        if primary_model is not None and hasattr(primary_model, "predict_proba"):
            try:
                p_probs = primary_model.predict_proba(latest_X.values)
                up_prob = float(p_probs[0, 1])
                signal = 1 if up_prob >= 0.5 else -1
                
                if meta_model is not None and hasattr(meta_model, "predict_proba"):
                    m_probs = meta_model.predict_proba(p_probs)
                    confidence = float(m_probs[0, 1])
                else:
                    confidence = max(up_prob, 1 - up_prob)
            except Exception as e:
                pass
                
        # Calculate expected alpha return ensuring directional alignment with signal
        magnitude = max(confidence, 1.0 - confidence)
        expected_alpha = float(signal * 0.04 * magnitude)
        
        predictions[ticker] = {
            "signal": int(signal),
            "confidence": round(confidence, 4),
            "expected_alpha": round(expected_alpha, 4)
        }
        
    return predictions

if __name__ == "__main__":
    from data.market_data import get_live_market_data
    data = get_live_market_data()
    preds = predict_alphas(data)
    for t, p in preds.items():
        print(f"{t}: Signal={p['signal']}, Conf={p['confidence']:.1%}, Alpha={p['expected_alpha']:.2%}")
