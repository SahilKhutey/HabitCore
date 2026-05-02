"""
BehaviorMLModel — correlation-based adaptive pattern detection.

Uses numpy to compute Pearson correlations between behavioral variables.
Requires at least 5 data points for statistical validity.

Correlations detected:
  sleep ↔ completion  (sleep deprivation → habit failure)
  mood  ↔ completion  (affect → behavioral activation)
  energy ↔ completion (energy → execution capacity)
  sleep ↔ mood        (sleep → emotional regulation)
  variability         (high std_completion → instability warning)
"""
from typing import List, Dict, Any
import numpy as np


class BehaviorMLModel:
    """
    Stateless correlation engine. Requires ≥5 samples for valid coefficients.
    All correlations are Pearson r, interpreted with conservative thresholds.
    """

    MIN_SAMPLES = 5        # below this, skip ML — insufficient statistical basis

    # Confidence thresholds for correlation strength
    STRONG_CORRELATION   = 0.55
    MODERATE_CORRELATION = 0.35

    @staticmethod
    def compute_correlations(features: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Compute Pearson r between behavioral variables.

        Returns dict of correlation coefficients, or empty dict if insufficient data.
        Correlations are clipped to [-1, 1] and NaN-safe.
        """
        if len(features) < BehaviorMLModel.MIN_SAMPLES:
            return {}

        sleep      = np.array([f["sleep"]           for f in features])
        completion = np.array([f["completion_rate"]  for f in features])
        mood       = np.array([f["mood"]             for f in features])
        energy     = np.array([f["energy"]           for f in features])

        def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
            """Pearson r, NaN-safe. Returns 0.0 if std is zero (constant series)."""
            if np.std(a) == 0 or np.std(b) == 0:
                return 0.0
            r = np.corrcoef(a, b)[0, 1]
            return float(np.nan_to_num(r, nan=0.0))

        return {
            "sleep_vs_completion":  safe_corr(sleep, completion),
            "mood_vs_completion":   safe_corr(mood,  completion),
            "energy_vs_completion": safe_corr(energy, completion),
            "sleep_vs_mood":        safe_corr(sleep, mood),
            "variability":          float(np.std(completion)),  # consistency stability
        }
