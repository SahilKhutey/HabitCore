"""
Rolling Features — Statistical trends over time windows.
"""
import numpy as np
from typing import List, Dict, Any

def compute_rolling(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes rolling averages and trends for a given history of daily features.
    """
    if len(history) < 3:
        return {}

    mood = [d.get("mood", 5) for d in history]
    avoidance = [d.get("avoidance_flag", 0) for d in history]
    focus_ratios = [d.get("focus_ratio", 0.5) for d in history]

    # Handle potential empty lists or insufficient data
    try:
        avg_mood_7d = np.mean(mood[-7:])
        avoidance_rate_7d = np.mean(avoidance[-7:])
        
        # Trend calculation using linear regression slope
        x = np.arange(len(mood))
        mood_trend = np.polyfit(x, mood, 1)[0]
        focus_trend = np.polyfit(x, focus_ratios, 1)[0]
    except Exception:
        avg_mood_7d = 5.0
        avoidance_rate_7d = 0.0
        mood_trend = 0.0
        focus_trend = 0.0

    return {
        "avg_mood_7d": float(avg_mood_7d),
        "avoidance_rate_7d": float(avoidance_rate_7d),
        "mood_trend": float(mood_trend),
        "focus_trend": float(focus_trend),
        "history_depth": len(history)
    }
