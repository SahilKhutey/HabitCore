"""
Feature Engine — Daily and Rolling feature builders.
"""
from typing import List, Dict, Any
import numpy as np
from datetime import date

class DailyFeatureBuilder:
    @staticmethod
    def build(events: List[Any], log: Any) -> Dict[str, Any]:
        """
        Builds features for a single day based on events and log.
        """
        # Event-based metrics
        # Use .get or getattr depending on if events are dicts or models
        def get_val(e, key):
            return e.get(key) if isinstance(e, dict) else getattr(e, key, 0)

        deep_work = sum(get_val(e, "event_value") for e in events if get_val(e, "event_type") == "deep_work")
        distraction = sum(get_val(e, "event_value") for e in events if get_val(e, "event_type") == "distraction")

        # Log-based metrics
        mood = getattr(log, "mood", 5) or 5
        energy = getattr(log, "energy", 5) or 5
        stress = getattr(log, "stress", 5) or 5
        
        avoidance_flag = getattr(log, "avoidance_flag", False)
        thought_label = getattr(log, "thought_label", "neutral")
        reframe = getattr(log, "reframe", "")

        return {
            "mood": mood,
            "energy": energy,
            "stress": stress,
            "deep_work_minutes": deep_work,
            "distraction_minutes": distraction,
            "focus_ratio": deep_work / (deep_work + distraction + 1.0),
            "avoidance_flag": int(avoidance_flag),
            "negative_thought_count": 1 if thought_label == "negative" else 0,
            "reframe_attempted": 1 if bool(reframe) else 0
        }

class RollingFeatureBuilder:
    @staticmethod
    def build(history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds aggregate/rolling features from a window of daily features.
        """
        if not history:
            return {}

        # 7-day averages
        window_7d = history[-7:]
        avg_mood_7d = np.mean([d["mood"] for d in window_7d])
        avoidance_rate_7d = np.mean([d["avoidance_flag"] for d in window_7d])

        # Focus Trend (Linear regression slope)
        if len(history) >= 3:
            y = [d["focus_ratio"] for d in history]
            x = range(len(y))
            focus_trend = np.polyfit(x, y, 1)[0]
        else:
            focus_trend = 0.0

        return {
            "avg_mood_7d": float(avg_mood_7d),
            "avoidance_rate_7d": float(avoidance_rate_7d),
            "focus_trend": float(focus_trend),
            "window_size": len(history)
        }
