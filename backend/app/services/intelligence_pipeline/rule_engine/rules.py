"""
Rule Engine — Deterministic behavioral rules (V1).
"""
from typing import List, Dict, Any

def detect_rules(features_window: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Applies deterministic rules to a window of daily features.
    Returns list of detected patterns.
    """
    patterns = []
    
    if not features_window:
        return []

    # Rule 1: Low energy → avoidance (Consistently low energy on avoidance days)
    low_energy_avoidance = sum(
        1 for d in features_window 
        if d.get("energy", 5) < 4 and d.get("avoidance_flag", 0) == 1
    )
    
    if low_energy_avoidance >= 3:
        patterns.append({
            "type": "energy_avoidance",
            "confidence": 0.85,
            "description": f"You avoid tasks when energy is low. This pattern appeared {low_energy_avoidance} times in the last window."
        })

    # Rule 2: High distraction → mood drop (Next day impact)
    for i in range(len(features_window) - 1):
        today = features_window[i]
        tomorrow = features_window[i+1]
        
        if (today.get("distraction_minutes", 0) > 90 and 
            tomorrow.get("mood", 5) < today.get("mood", 5)):
            patterns.append({
                "type": "distraction_mood_drop",
                "confidence": 0.80,
                "description": "High distraction today is consistently linked to a mood drop tomorrow."
            })
            break # Avoid duplicating the same pattern type for the same window

    # Rule 3: Missing reframe on negative thought days
    neg_days = [d for d in features_window if d.get("negative_thought_count", 0) > 0]
    if neg_days:
        reframe_rate = sum(d.get("reframe_attempted", 0) for d in neg_days) / len(neg_days)
        if reframe_rate < 0.3:
            patterns.append({
                "type": "low_cognitive_resilience",
                "confidence": 0.75,
                "description": "You rarely reframe negative thoughts when they appear. This reinforces negative loops."
            })

    return patterns
