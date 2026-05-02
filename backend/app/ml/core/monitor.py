"""
Drift Monitor — Detects behavioral shifts in real-time.
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)

def check_feature_drift(current_batch: np.ndarray, training_stats: dict, threshold: float = 0.2):
    """
    Compares current feature distribution against training baseline.
    training_stats: {"means": [avg1, avg2, ...], "stds": [std1, std2, ...]}
    """
    current_means = np.mean(current_batch, axis=0)
    baseline_means = np.array(training_stats["means"])
    
    diff = np.abs(current_means - baseline_means)
    drift_indices = np.where(diff > threshold)[0]
    
    if len(drift_indices) > 0:
        logger.warning(f"Drift detected in features: {drift_indices}")
        return True, drift_indices.tolist()
        
    return False, []
