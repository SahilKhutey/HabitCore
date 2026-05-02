"""
Statistical Engine — Deeper behavioral correlation analysis.
"""
import numpy as np
from typing import List, Dict, Any

def compute_stats(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes statistical correlations between behavioral variables.
    """
    if len(history) < 5:
        return {}

    mood = np.array([d.get("mood", 5) for d in history], dtype=float)
    distraction = np.array([d.get("distraction_minutes", 0) for d in history], dtype=float)
    energy = np.array([d.get("energy", 5) for d in history], dtype=float)
    focus = np.array([d.get("focus_ratio", 0.5) for d in history], dtype=float)

    def get_corr(a, b):
        if np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    return {
        "distraction_mood_corr": get_corr(distraction, mood),
        "energy_focus_corr": get_corr(energy, focus),
        "mood_focus_corr": get_corr(mood, focus)
    }
