"""
Statistical Engine — Correlation and Lag Analysis (V1.5).
"""
import numpy as np
from typing import List, Dict, Any

def compute_correlations(history: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Computes Pearson correlations between key behavioral variables.
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
        "distraction_vs_mood": get_corr(distraction, mood),
        "energy_vs_focus": get_corr(energy, focus),
        "mood_vs_focus": get_corr(mood, focus)
    }

def compute_lag_correlations(history: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Computes correlations between today's variable and tomorrow's result (Lag-1).
    """
    if len(history) < 7:
        return {}

    # Distraction today -> Mood tomorrow
    dist_today = np.array([d.get("distraction_minutes", 0) for d in history[:-1]], dtype=float)
    mood_tomorrow = np.array([d.get("mood", 5) for d in history[1:]], dtype=float)

    # Focus today -> Energy tomorrow (Depletion signal)
    focus_today = np.array([d.get("focus_ratio", 0.5) for d in history[:-1]], dtype=float)
    energy_tomorrow = np.array([d.get("energy", 5) for d in history[1:]], dtype=float)

    def get_corr(a, b):
        if np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    return {
        "lag_distraction_mood": get_corr(dist_today, mood_tomorrow),
        "lag_focus_energy": get_corr(focus_today, energy_tomorrow)
    }
