"""
ScoringEngine — Computes mental metrics from a CognitiveDayLog.

These are NOT XP points. They are behavioral quality scores.
They appear in the UI as:
  "Your Clarity score today: 0.72"
  "Control score this week: 0.61"
  "Integrity score: 0.83"
  "Focus ratio: 0.45"

4 core mental scores:
  Clarity   — quality of thought observation (did they name it? classify it? reframe it?)
  Control   — locus-of-control filter usage (did they separate in/out of control?)
  Integrity — alignment between stated values and actions
  Focus     — deep work as a fraction of total tracked work time

Weekly aggregation provides trend scores for the dashboard.
"""
from typing import Dict, Any, List, Optional
from statistics import mean

from app.services.cognitive_training_system.schemas import MentalScores


class ScoringEngine:
    """Stateless mental metric calculator."""

    @staticmethod
    def compute_daily(log: Any) -> MentalScores:
        """
        Compute mental scores for a single CognitiveDayLog entry.
        Handles missing (partial log) fields gracefully.
        """
        clarity   = ScoringEngine._clarity(log)
        control   = ScoringEngine._control(log)
        integrity = ScoringEngine._integrity(log)
        focus     = ScoringEngine._focus(log)

        return MentalScores(
            clarity=round(clarity, 3),
            control=round(control, 3),
            integrity=round(integrity, 3),
            focus=round(focus, 3),
        )

    @staticmethod
    def compute_weekly(logs: List[Any]) -> Dict[str, Any]:
        """
        Aggregate mental scores across a week.
        Returns averages + trend direction per score.
        """
        if not logs:
            return {
                "clarity":   {"avg": 0.0, "trend": "no_data"},
                "control":   {"avg": 0.0, "trend": "no_data"},
                "integrity": {"avg": 0.0, "trend": "no_data"},
                "focus":     {"avg": 0.0, "trend": "no_data"},
            }

        daily = [ScoringEngine.compute_daily(l) for l in logs]

        def _trend(values: List[float]) -> str:
            if len(values) < 3:
                return "stable"
            mid = len(values) // 2
            early  = mean(values[:mid])
            recent = mean(values[mid:])
            delta  = recent - early
            if delta > 0.07:  return "improving"
            if delta < -0.07: return "declining"
            return "stable"

        clarity_vals   = [d.clarity   for d in daily]
        control_vals   = [d.control   for d in daily]
        integrity_vals = [d.integrity for d in daily]
        focus_vals     = [d.focus     for d in daily]

        return {
            "clarity":   {"avg": round(mean(clarity_vals),   3), "trend": _trend(clarity_vals)},
            "control":   {"avg": round(mean(control_vals),   3), "trend": _trend(control_vals)},
            "integrity": {"avg": round(mean(integrity_vals), 3), "trend": _trend(integrity_vals)},
            "focus":     {"avg": round(mean(focus_vals),     3), "trend": _trend(focus_vals)},
            "days_scored": len(logs),
        }

    # ── Score Calculators ─────────────────────────────────────────────────────

    @staticmethod
    def _clarity(log: Any) -> float:
        """
        Clarity = quality of thought observation.
        Components:
          - Thought logged at all:        +0.25
          - Thought classified (type):    +0.20
          - Distortion identified:        +0.25
          - Reframe attempted:            +0.20
          - Belief shift achieved (>20%): +0.10
        """
        score = 0.0
        if log.thought:               score += 0.25
        if log.thought_type:          score += 0.20
        if log.cognitive_distortion:  score += 0.25
        if log.reframe:               score += 0.20
        if (
            log.belief_strength_before and log.belief_strength_after
            and log.belief_strength_before > 0
            and (log.belief_strength_before - log.belief_strength_after)
                / log.belief_strength_before > 0.20
        ):
            score += 0.10
        return min(score, 1.0)

    @staticmethod
    def _control(log: Any) -> float:
        """
        Control = effective use of locus-of-control filter.
        Components:
          - in_control list non-empty:     +0.40
          - out_of_control list non-empty: +0.40 (identifying what NOT to fight)
          - anxiety_dump completed:        +0.20 (offloading cognitive burden)
        """
        score = 0.0
        if isinstance(log.in_control, list)       and len(log.in_control) > 0:    score += 0.40
        if isinstance(log.out_of_control, list)   and len(log.out_of_control) > 0: score += 0.40
        if log.anxiety_dump:                                                        score += 0.20
        return min(score, 1.0)

    @staticmethod
    def _integrity(log: Any) -> float:
        """
        Integrity = alignment between stated values and actions.
        Components:
          - self_respect="yes":           1.00
          - self_respect="partial":       0.60
          - self_respect="no":            0.20
          - acted_as_intended bonus:      +0.15 if True
          - Tomorrow priority set:        +0.05 (planning as integrity commitment)
        """
        respect_scores = {"yes": 0.80, "partial": 0.55, "no": 0.15}
        score = respect_scores.get(log.self_respect or "partial", 0.55)

        if log.acted_as_intended is True:
            score += 0.15
        if log.tomorrow_priority:
            score += 0.05

        return min(score, 1.0)

    @staticmethod
    def _focus(log: Any) -> float:
        """
        Focus = deep work as fraction of total tracked work time.
        If no work time tracked, returns 0.5 (neutral, not penalized).
        """
        deep        = log.deep_work_minutes    or 0
        distracted  = log.distraction_minutes  or 0
        total       = deep + distracted

        if total == 0:
            return 0.50   # no data — neutral

        return min(deep / total, 1.0)
