"""
Core Feature Builder — The single source of truth for behavior features.
Used by training, batch pipelines, and real-time inference.
"""
from typing import Dict, Any, List

def build_behavioral_features(record: Dict[str, Any]) -> List[float]:
    """
    Standardizes a behavioral record into a feature vector.
    Input format: {
        "energy": int (1-10),
        "focus_ratio": float (0-1),
        "distraction_minutes": float,
        "integrity_score": float
    }
    """
    # 1. Extraction with defaults
    energy = float(record.get("energy", 5.0))
    focus_ratio = float(record.get("focus_ratio", 0.5))
    distraction = float(record.get("distraction_minutes", 0.0))
    integrity = float(record.get("integrity_score", 5.0))
    
    # 2. Return ordered vector
    # Order: [Energy, Focus, Distraction, Integrity]
    return [energy, focus_ratio, distraction, integrity]

def get_feature_names() -> List[str]:
    return ["energy", "focus_ratio", "distraction_minutes", "integrity_score"]

def get_feature_version() -> str:
    return "v2.0_behavior_aware"
