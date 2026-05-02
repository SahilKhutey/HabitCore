"""
Rule Engine — Deterministic behavioral pattern detection.
"""
from typing import List, Dict, Any

def detect_patterns(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes historical features to identify specific psychological or behavioral patterns.
    """
    patterns = []
    if not history:
        return []

    # Pattern 1: Low Energy -> Avoidance
    # If energy is low (< 4) and avoidance is flagged for 3 or more days in the window
    energy_avoidance_count = sum(1 for d in history if d.get("energy", 5) < 4 and d.get("avoidance_flag", 0) == 1)
    if energy_avoidance_count >= 3:
        patterns.append({
            "type": "energy_avoidance",
            "confidence": 0.85,
            "message": "Low energy is consistently leading to task avoidance. Your system might be overtaxed."
        })

    # Pattern 2: Distraction -> Next-day Mood Drop
    # High distraction (> 90 mins) followed by a drop in mood the next day
    for i in range(len(history) - 1):
        if history[i].get("distraction_minutes", 0) > 90:
            if history[i+1].get("mood", 5) < history[i].get("mood", 5):
                patterns.append({
                    "type": "distraction_mood_impact",
                    "confidence": 0.8,
                    "message": "High distraction levels are followed by a measurable drop in mood the next day."
                })
                break

    # Pattern 3: Negative Thought Spiral
    # Multiple days of negative thoughts without reframing
    neg_unframed = sum(1 for d in history if d.get("negative_thought", 0) == 1 and d.get("reframe", 0) == 0)
    if neg_unframed >= 3:
        patterns.append({
            "type": "unframed_negativity_loop",
            "confidence": 0.75,
            "message": "You are experiencing a cluster of negative thoughts without active reframing. This risks a cognitive loop."
        })

    return patterns
