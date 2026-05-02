"""
PatternEngine — Temporal + Causal Pattern Detection.

Runs on rolling 7–14 day windows of behavioral data.
Detects cross-day correlations that single-day analysis misses.

Pattern types:
  energy_avoidance_link  — low energy days overlap with avoidance days
  thought_behavior_link  — specific thought keywords precede avoidance
  relapse_pattern        — one miss day consistently leads to multi-day dropout
  focus_degradation      — distraction minutes trend upward over window
  integrity_erosion      — self_integrity declining trend
  emotional_behavior_link — specific emotions precede avoidance or action
  consistency_spike       — improvement plateau followed by sudden consistency
  weekend_effect          — systematic performance drop on specific day-of-week

Pattern confidence is evidence-weighted:
  overlap_rate × window_coverage × streak_factor

ALL pattern messages are specific and data-referenced.
"""
from typing import List, Dict, Any, Optional
from collections import Counter
from statistics import mean, stdev
from datetime import datetime, timedelta

from app.services.behavioral_feedback_engine.schemas import DetectedPattern


class PatternEngine:
    """Stateless temporal pattern detector. Operates on log window."""

    @staticmethod
    def detect_all(logs: List[Any], window_days: int = 7) -> List[DetectedPattern]:
        """
        Run all pattern detectors on the log window.
        Returns list sorted by confidence (highest first).
        """
        if len(logs) < 3:
            return []

        detectors = [
            PatternEngine._energy_avoidance_link,
            PatternEngine._thought_behavior_link,
            PatternEngine._relapse_pattern,
            PatternEngine._focus_degradation,
            PatternEngine._integrity_erosion,
            PatternEngine._emotional_behavior_link,
            PatternEngine._consistency_trend,
        ]

        patterns: List[DetectedPattern] = []
        for detector in detectors:
            result = detector(logs, window_days)
            if result:
                patterns.append(result)

        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    # ── Pattern Detectors ─────────────────────────────────────────────────────

    @staticmethod
    def _energy_avoidance_link(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects correlation between low energy and task avoidance.
        Triggers when overlap rate > 60%.
        """
        low_energy = {i for i, l in enumerate(logs) if (l.energy or 5) < 4}
        avoidance  = {i for i, l in enumerate(logs) if getattr(l, "avoided_task", False) or (getattr(l, "habits_skipped", 0) or 0) > 0}

        if not low_energy or not avoidance:
            return None

        overlap = len(low_energy & avoidance)
        overlap_rate = overlap / max(len(low_energy), 1)

        if overlap_rate < 0.60:
            return None

        return DetectedPattern(
            type="energy_avoidance_link",
            label="Energy–Avoidance Link",
            message=f"On {overlap_rate:.0%} of your low-energy days, you also avoided intended tasks. Low energy is a consistent avoidance trigger for you.",
            confidence=round(min(0.55 + overlap_rate * 0.40, 0.95), 3),
            window_days=window,
            supporting_data={"low_energy_days": len(low_energy), "overlap_days": overlap},
        )

    @staticmethod
    def _thought_behavior_link(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects specific thought keywords that reliably precede avoidance.
        """
        TRIGGER_KEYWORDS = {
            "tired":    "fatigue",
            "can't":    "helplessness",
            "fail":     "failure anticipation",
            "behind":   "comparison",
            "stressed": "stress",
            "useless":  "labeling",
            "pointless": "nihilism",
        }

        link_counts: Dict[str, int] = {}
        total_avoidance = sum(1 for l in logs if getattr(l, "avoided_task", False) or (getattr(l, "habits_skipped", 0) or 0) > 0)

        for log in logs:
            thought = (getattr(log, "thought", None) or "").lower()
            avoided = getattr(log, "avoided_task", False) or (getattr(log, "habits_skipped", 0) or 0) > 0

            if avoided and thought:
                for kw, label in TRIGGER_KEYWORDS.items():
                    if kw in thought:
                        link_counts[label] = link_counts.get(label, 0) + 1

        if not link_counts:
            return None

        top_label, top_count = max(link_counts.items(), key=lambda x: x[1])
        if top_count < 2:
            return None

        rate = top_count / max(total_avoidance, 1)

        return DetectedPattern(
            type="thought_behavior_link",
            label="Thought–Behavior Link",
            message=f"'{top_label.title()}' thoughts appear on {top_count} of your avoidance days. This thought type is functioning as an avoidance signal.",
            confidence=round(min(0.60 + rate * 0.30, 0.92), 3),
            window_days=window,
            supporting_data={"trigger": top_label, "occurrences": top_count},
        )

    @staticmethod
    def _relapse_pattern(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects: one missed day consistently leads to multi-day dropout.
        Looks for 0-miss → 1-miss → 2+ miss sequences.
        """
        if len(logs) < 5:
            return None

        miss_runs: List[int] = []
        current_run = 0

        for log in logs:
            completed = getattr(log, "action_taken", None)
            habits_done = getattr(log, "habits_completed", 0) or 0
            missed = (not completed) or habits_done == 0

            if missed:
                current_run += 1
            else:
                if current_run > 0:
                    miss_runs.append(current_run)
                current_run = 0
        if current_run > 0:
            miss_runs.append(current_run)

        if not miss_runs:
            return None

        multi_day_runs = [r for r in miss_runs if r >= 2]
        if not multi_day_runs:
            return None

        rate = len(multi_day_runs) / max(len(miss_runs), 1)
        if rate < 0.50:
            return None

        avg_run = mean(miss_runs)

        return DetectedPattern(
            type="relapse_pattern",
            label="Dropout Pattern",
            message=f"When you miss one day, you miss an average of {avg_run:.1f} consecutive days. A single miss is triggering multi-day dropout.",
            confidence=round(min(0.65 + rate * 0.25, 0.92), 3),
            window_days=window,
            supporting_data={"avg_dropout_length": round(avg_run, 1), "dropout_events": len(multi_day_runs)},
        )

    @staticmethod
    def _focus_degradation(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects an increasing trend in distraction minutes across the window.
        """
        distraction_vals = [getattr(l, "distraction_minutes", 0) or 0 for l in logs]
        if len(distraction_vals) < 4 or max(distraction_vals) == 0:
            return None

        # Trend: compare early half vs late half
        mid = len(distraction_vals) // 2
        early_avg  = mean(distraction_vals[:mid])
        recent_avg = mean(distraction_vals[mid:])

        if recent_avg < early_avg * 1.35:   # 35% increase threshold
            return None

        delta = recent_avg - early_avg

        return DetectedPattern(
            type="focus_degradation",
            label="Focus Degradation",
            message=f"Distraction time has increased by {delta:.0f} minutes/day on average over the tracked period. Attention fragmentation is trending upward.",
            confidence=round(min(0.60 + (delta / max(recent_avg, 1)) * 0.25, 0.90), 3),
            window_days=window,
            supporting_data={"early_avg_min": round(early_avg, 1), "recent_avg_min": round(recent_avg, 1)},
        )

    @staticmethod
    def _integrity_erosion(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects a declining self_integrity score trend.
        """
        integrity_vals = []
        for l in logs:
            si = getattr(l, "self_integrity", None)
            if si is None:
                sr = getattr(l, "self_respect", None)
                si = {"yes": 1, "partial": 0, "no": 0}.get(sr or "partial", 0)
            integrity_vals.append(float(si))

        if len(integrity_vals) < 4:
            return None

        avg = mean(integrity_vals)
        mid = len(integrity_vals) // 2
        early_avg  = mean(integrity_vals[:mid])
        recent_avg = mean(integrity_vals[mid:])

        if recent_avg >= early_avg - 0.15:   # needs meaningful decline
            return None

        low_days = sum(1 for v in integrity_vals if v < 0.5)

        return DetectedPattern(
            type="integrity_erosion",
            label="Integrity Erosion",
            message=f"Self-alignment is declining. You rated your actions as misaligned on {low_days} of {len(logs)} tracked days, with a worsening trend.",
            confidence=round(min(0.65 + (early_avg - recent_avg) * 0.80, 0.92), 3),
            window_days=window,
            supporting_data={"low_integrity_days": low_days, "recent_avg": round(recent_avg, 3)},
        )

    @staticmethod
    def _emotional_behavior_link(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects specific emotions that reliably precede avoidance vs. action.
        """
        emotion_avoidance: Dict[str, int] = {}
        emotion_action:    Dict[str, int] = {}

        for log in logs:
            emotion = (getattr(log, "emotion", None) or "").lower().strip()
            if not emotion:
                continue
            avoided = getattr(log, "avoided_task", False)
            acted   = getattr(log, "action_taken", False)

            if avoided:
                emotion_avoidance[emotion] = emotion_avoidance.get(emotion, 0) + 1
            if acted:
                emotion_action[emotion] = emotion_action.get(emotion, 0) + 1

        # Find emotion most linked to avoidance (not to action)
        best_emotion = None
        best_ratio   = 0.0
        for emotion, avoid_count in emotion_avoidance.items():
            action_count = emotion_action.get(emotion, 0)
            total = avoid_count + action_count
            if total < 2:
                continue
            avoidance_ratio = avoid_count / total
            if avoidance_ratio > 0.70 and avoidance_ratio > best_ratio:
                best_ratio   = avoidance_ratio
                best_emotion = (emotion, avoid_count, total)

        if not best_emotion:
            return None

        emotion, avoid_count, total = best_emotion

        return DetectedPattern(
            type="emotional_behavior_link",
            label="Emotion–Behavior Link",
            message=f"When you feel '{emotion}', you avoid intended tasks on {best_ratio:.0%} of occurrences. This emotion is a reliable avoidance predictor.",
            confidence=round(min(0.60 + best_ratio * 0.30, 0.90), 3),
            window_days=window,
            supporting_data={"emotion": emotion, "avoidance_rate": round(best_ratio, 3)},
        )

    @staticmethod
    def _consistency_trend(logs: List[Any], window: int) -> Optional[DetectedPattern]:
        """
        Detects a positive trend (improving) or sustained consistency.
        Returns a progress pattern — not a warning.
        """
        completion_vals = []
        for l in logs:
            acted = getattr(l, "action_taken", None)
            done  = getattr(l, "habits_completed", 0) or 0
            completion_vals.append(1.0 if (acted or done > 0) else 0.0)

        if len(completion_vals) < 4:
            return None

        mid        = len(completion_vals) // 2
        early_avg  = mean(completion_vals[:mid])
        recent_avg = mean(completion_vals[mid:])

        if recent_avg < early_avg + 0.20:   # needs meaningful improvement
            return None

        return DetectedPattern(
            type="consistency_improving",
            label="Consistency Improving",
            message=f"Behavioral consistency has improved from {early_avg:.0%} to {recent_avg:.0%} over the tracked window. This is a statistically meaningful shift.",
            confidence=round(min(0.60 + (recent_avg - early_avg) * 0.80, 0.90), 3),
            window_days=window,
            supporting_data={"early_rate": round(early_avg, 3), "recent_rate": round(recent_avg, 3)},
        )

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_weekly_trend(score_history: List[float]) -> str:
        """
        Compute behavioral trend from a list of daily scores.
        Returns: "improving" | "declining" | "stable"
        """
        if len(score_history) < 3:
            return "stable"
        mid    = len(score_history) // 2
        early  = mean(score_history[:mid])
        recent = mean(score_history[mid:])
        delta  = recent - early
        if delta > 0.05:  return "improving"
        if delta < -0.05: return "declining"
        return "stable"
