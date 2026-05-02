"""
FeatureExtractor — converts raw DailyBehaviorData into numerical feature vectors.

Responsibilities:
  - Normalize mood strings → ordinal integers
  - Normalize energy strings → ordinal integers
  - Estimate sleep hours from sleep_quality
  - Compute per-day completion rates
  - Aggregate into summary statistics for rule-based detection
"""
from typing import List, Dict, Any
import numpy as np
from .schemas import DailyBehaviorData


# ── Normalization maps (aligned to DailyCheckin model) ─────────────────────

MOOD_SCALE: Dict[str, int] = {
    "happy":   5,
    "excited": 5,
    "neutral": 3,
    "tired":   2,
    "sad":     1,
    "angry":   1,
}

ENERGY_SCALE: Dict[str, int] = {
    "high":   3,
    "medium": 2,
    "low":    1,
}

# sleep_quality (1–5) → estimated hours of sleep
SLEEP_QUALITY_TO_HOURS: Dict[int, float] = {
    1: 4.5,
    2: 5.5,
    3: 6.5,
    4: 7.5,
    5: 8.5,
}


class FeatureExtractor:
    """
    Converts a list of DailyBehaviorData records into per-day feature dicts
    and an aggregated summary dict used by PatternRules and MLModel.
    """

    @staticmethod
    def normalize_mood(mood: Any) -> int:
        """Map mood string or int to 1–5 scale."""
        if isinstance(mood, int):
            return max(1, min(5, mood))
        return MOOD_SCALE.get(str(mood).lower(), 3)

    @staticmethod
    def normalize_energy(energy: Any) -> int:
        """Map energy string or int to 1–3 scale."""
        if isinstance(energy, int):
            return max(1, min(3, energy))
        return ENERGY_SCALE.get(str(energy).lower(), 2)

    @staticmethod
    def estimate_sleep_hours(sleep_quality: int, sleep_hours: float) -> float:
        """
        Use explicit sleep_hours if provided and realistic,
        otherwise estimate from sleep_quality rating.
        """
        if 3.0 <= sleep_hours <= 12.0:
            return sleep_hours
        return SLEEP_QUALITY_TO_HOURS.get(max(1, min(5, sleep_quality)), 6.5)

    @staticmethod
    def extract(user_data: List[DailyBehaviorData]) -> List[Dict[str, float]]:
        """
        Convert raw daily records to normalized per-day feature vectors.

        Returns:
            List of dicts with keys:
              completion_rate, mood, energy, sleep, has_reflection
        """
        features = []
        for day in user_data:
            completion_rate = (
                day.habits_completed / day.habits_total
                if day.habits_total > 0 else 0.0
            )
            features.append({
                "completion_rate": round(completion_rate, 4),
                "mood":            FeatureExtractor.normalize_mood(day.mood),
                "energy":          FeatureExtractor.normalize_energy(day.energy),
                "sleep":           FeatureExtractor.estimate_sleep_hours(
                                       day.sleep_quality, day.sleep_hours
                                   ),
                "has_reflection":  1.0 if day.reflection else 0.0,
            })
        return features

    @staticmethod
    def aggregate(features: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Compute aggregate statistics across all days.

        Returns:
            Dict with avg_*, std_*, min_*, and recent_* values.
            recent_* = last 3 days average (trend detection).
        """
        if not features:
            return {
                "avg_completion": 0.0, "avg_mood": 3.0,
                "avg_energy": 2.0,     "avg_sleep": 6.5,
                "avg_reflection_rate": 0.0,
                "std_completion": 0.0,
                "min_sleep": 6.5,
                "recent_completion": 0.0,
                "recent_mood": 3.0,
                "sample_size": 0,
            }

        cr    = [f["completion_rate"] for f in features]
        mood  = [f["mood"]            for f in features]
        nrg   = [f["energy"]          for f in features]
        slp   = [f["sleep"]           for f in features]
        refl  = [f["has_reflection"]  for f in features]

        recent = features[-3:] if len(features) >= 3 else features

        return {
            "avg_completion":       round(float(np.mean(cr)),   4),
            "avg_mood":             round(float(np.mean(mood)),  4),
            "avg_energy":           round(float(np.mean(nrg)),   4),
            "avg_sleep":            round(float(np.mean(slp)),   4),
            "avg_reflection_rate":  round(float(np.mean(refl)),  4),
            "std_completion":       round(float(np.std(cr)),     4),
            "min_sleep":            round(float(np.min(slp)),    4),
            "recent_completion":    round(float(np.mean([f["completion_rate"] for f in recent])), 4),
            "recent_mood":          round(float(np.mean([f["mood"]            for f in recent])), 4),
            "sample_size":          len(features),
        }
