"""
Feature Engine — Builds daily behavioral features.
"""
from collections import defaultdict
from typing import List, Dict, Any

def build_daily_features(events: List[Dict[str, Any]], log: Any) -> Dict[str, Any]:
    """
    Standardizes raw events and logs into a flat feature dictionary.
    """
    features = defaultdict(float)
    
    for e in events:
        e_type = e.get("event_type") if isinstance(e, dict) else getattr(e, "event_type", None)
        e_val = e.get("event_value", 0) if isinstance(e, dict) else getattr(e, "event_value", 0)
        
        if e_type == "deep_work":
            features["deep_work_minutes"] += float(e_val)
        elif e_type == "distraction":
            features["distraction_minutes"] += float(e_val)

    total = features["deep_work_minutes"] + features["distraction_minutes"] + 1
    
    # Extract from log (model or dict)
    def get_attr(obj, attr, default=0):
        return getattr(obj, attr, default) if not isinstance(obj, dict) else obj.get(attr, default)

    return {
        "mood": get_attr(log, "mood", 5),
        "energy": get_attr(log, "energy", 5),
        "stress": get_attr(log, "stress", 5),
        "deep_work_minutes": features["deep_work_minutes"],
        "distraction_minutes": features["distraction_minutes"],
        "focus_ratio": features["deep_work_minutes"] / total,
        "avoidance_flag": int(get_attr(log, "avoidance_flag", False)),
        "negative_thought": int(get_attr(log, "thought_label") == "negative"),
        "reframe": int(bool(get_attr(log, "reframe")))
    }
