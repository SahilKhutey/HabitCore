"""
Pattern Orchestrator — Merges Rule, Statistical, and ML layers.
"""
from typing import List, Dict, Any
from app.services.intelligence_pipeline.rule_engine.rules import detect_rules
from app.services.intelligence_pipeline.statistical_engine.analysis import compute_correlations, compute_lag_correlations
from app.services.intelligence_pipeline.ml_engine.avoidance import AvoidanceModel

def generate_patterns(history_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Orchestrates the layered intelligence pipeline to detect patterns.
    Rules → Statistical → ML.
    """
    patterns = []
    
    if not history_features:
        return []

    # 1. Rule-based (Deterministic)
    patterns += detect_rules(history_features)

    # 2. Statistical (Correlations)
    correlations = compute_correlations(history_features)
    if correlations.get("distraction_vs_mood", 0) < -0.5:
        patterns.append({
            "type": "statistical_pattern",
            "description": f"Statistical link detected: Higher distraction levels are negatively impacting your mood (corr: {correlations['distraction_vs_mood']:.2f}).",
            "confidence": abs(correlations["distraction_vs_mood"])
        })
    
    if correlations.get("energy_vs_focus", 0) > 0.6:
        patterns.append({
            "type": "statistical_pattern",
            "description": "Your focus level is highly dependent on your energy state. Managing energy is your highest leverage for productivity.",
            "confidence": correlations["energy_vs_focus"]
        })

    # 3. Lag Analysis (Next-day impact)
    lags = compute_lag_correlations(history_features)
    if lags.get("lag_distraction_mood", 0) < -0.4:
        patterns.append({
            "type": "lag_effect",
            "description": "Evidence shows that distraction today significantly reduces your mood tomorrow.",
            "confidence": abs(lags["lag_distraction_mood"])
        })

    # 4. ML Prediction (Probabilistic - V2)
    model = AvoidanceModel()
    if model.is_ready(len(history_features)):
        # Prep features for prediction (today's features)
        today = history_features[-1]
        x = [
            float(today.get("energy", 5)),
            float(today.get("stress", 5)),
            float(today.get("focus_ratio", 0.5)),
            float(today.get("avoidance_rate_7d", 0.0)) # This should come from rolling features
        ]
        prob = model.predict_proba(x)
        if prob > 0.7:
            patterns.append({
                "type": "ml_prediction",
                "description": f"High probability of avoidance tomorrow ({prob:.0%}) based on current state. Immediate intervention suggested.",
                "confidence": prob
            })

    return patterns
