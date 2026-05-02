"""
BFE ScoringEngine — Internal behavioral composite score.

⚠️ NOT for display. Never shown to user as XP or points.
Used ONLY for:
  - State determination (AdaptiveEngine input)
  - Trend analysis (weekly meta)
  - Pattern detection baseline

Formula (state-adjusted weights from AdaptiveEngine):
  score = (execution × w_exec)
        - (avoidance × w_avoid)    ← penalty
        + (cognitive × w_cog)
        + (emotional × w_emo)
        + (integrity × w_int)
        + (focus × w_foc)

Each component is normalized 0.0–1.0 before weighting.
Output is clamped to [0.0, 1.0].

RetentionSystem:
  Flexible streaks (1–2 miss tolerance)
  Consistency ratio (not perfection)
  Anti-burnout (reduce prompts if usage_too_high)
  Identity reinforcement (language calibrated to trajectory)
  Pattern curiosity (ethical hook, not dopamine)
"""
from typing import Dict, Any, List, Optional
from statistics import mean
from datetime import datetime, timedelta

from app.services.behavioral_feedback_engine.schemas import (
    BehaviorScore, UserSystemState, WeeklyMeta
)
from app.services.behavioral_feedback_engine.adaptive_engine import AdaptiveEngine


class BFEScoringEngine:
    """Stateless behavior score calculator."""

    @staticmethod
    def compute(
        log: Any,
        state: UserSystemState,
        cognitive_features: Optional[Dict[str, Any]] = None,
    ) -> BehaviorScore:
        """
        Compute state-adjusted behavior score for a single log entry.

        Args:
            log:                CognitiveDayLog or DailyInput object
            state:              Current UserSystemState
            cognitive_features: Optional feature dict for cognitive component
        """
        weights = AdaptiveEngine.get_weights(state)

        # ── Component normalization ────────────────────────────────────────

        # Execution: action_taken or habits_completed > 0
        action_taken = getattr(log, "action_taken", None)
        habits_done  = getattr(log, "habits_completed", 0) or 0
        execution    = 1.0 if (action_taken or habits_done > 0) else 0.0

        # Avoidance: penalty (inverted)
        avoided       = getattr(log, "avoided_task", False) or (getattr(log, "habits_skipped", 0) or 0) > 0
        avoidance_pen = 1.0 if avoided else 0.0

        # Cognitive: thought logged + classified
        has_thought      = bool(getattr(log, "thought", None))
        has_distortion   = bool(getattr(log, "cognitive_distortion", None))
        has_reframe      = bool(getattr(log, "reframe", None))
        cognitive = (
            (0.40 if has_thought else 0.0) +
            (0.30 if has_distortion else 0.0) +
            (0.30 if has_reframe else 0.0)
        )

        # Emotional: mood + energy normalized
        mood_raw   = getattr(log, "mood", 5) or 5
        energy_raw = getattr(log, "energy", 5)
        if isinstance(energy_raw, str):
            energy_raw = {"low": 2, "medium": 5, "high": 8}.get(energy_raw, 5)
        energy_raw = energy_raw or 5
        emotional = ((mood_raw / 10) + (energy_raw / 10)) / 2

        # Integrity: self_respect / self_integrity field
        si = getattr(log, "self_integrity", None)
        if si is None:
            sr = getattr(log, "self_respect", None)
            si = {"yes": 1.0, "partial": 0.5, "no": 0.0}.get(sr or "partial", 0.5)
        integrity = float(si)

        # Focus: deep_work / (deep + distracted)
        deep       = getattr(log, "deep_work_minutes", 0) or 0
        distracted = getattr(log, "distraction_minutes", 0) or 0
        total_work = deep + distracted
        focus      = (deep / total_work) if total_work > 0 else 0.50

        # ── Composite score ────────────────────────────────────────────────
        raw_score = (
            execution  * weights["execution"]
            - avoidance_pen * weights["avoidance"]
            + cognitive * weights["cognitive"]
            + emotional * weights["emotional"]
            + integrity * weights["integrity"]
            + focus     * weights["focus"]
        )

        final_score = round(max(0.0, min(raw_score, 1.0)), 4)

        return BehaviorScore(
            score=final_score,
            execution=round(execution, 3),
            avoidance=round(avoidance_pen, 3),
            cognitive=round(cognitive, 3),
            emotional=round(emotional, 3),
            integrity=round(integrity, 3),
            focus=round(focus, 3),
            state_label=state,
        )

    @staticmethod
    def compute_weekly_meta(
        score_history:   List[float],
        logs:            List[Any],
        state:           UserSystemState,
        top_insight_msg: Optional[str] = None,
    ) -> WeeklyMeta:
        """
        Compute weekly behavioral meta from score history + logs.
        """
        if not score_history:
            return WeeklyMeta(
                trend="stable", avg_score=0.0, peak_day=None, lowest_day=None,
                dominant_state=state, pattern_count=0, top_insight=top_insight_msg,
                identity_consistency=0.0,
            )

        from app.services.behavioral_feedback_engine.pattern_engine import PatternEngine
        trend    = PatternEngine.get_weekly_trend(score_history)
        avg_sc   = round(mean(score_history), 3)

        # Peak and lowest day
        if len(score_history) == len(logs):
            peak_idx   = score_history.index(max(score_history))
            lowest_idx = score_history.index(min(score_history))
            peak_day   = _day_label(logs[peak_idx])
            lowest_day = _day_label(logs[lowest_idx])
        else:
            peak_day   = None
            lowest_day = None

        # Identity consistency (% days self_integrity=1 or self_respect=yes)
        int_days = sum(1 for l in logs if _integrity_val(l) >= 0.80)
        identity_consistency = round(int_days / max(1, len(logs)), 3)

        return WeeklyMeta(
            trend=trend,
            avg_score=avg_sc,
            peak_day=peak_day,
            lowest_day=lowest_day,
            dominant_state=state,
            pattern_count=0,   # filled in by BFEService
            top_insight=top_insight_msg,
            identity_consistency=identity_consistency,
        )


class RetentionSystem:
    """
    Ethical retention engine.
    Implements anti-dopamine retention patterns:
      - Pattern curiosity (not mystery boxes)
      - Identity reinforcement (not praise)
      - Flexible streaks (not perfection pressure)
      - Anti-burnout protection (reduce prompts if overuse detected)
    """

    # Flexible streak: allow 1 miss in a 7-day window
    MISS_TOLERANCE = 1

    @staticmethod
    def compute_flexible_streak(logs: List[Any]) -> Dict[str, Any]:
        """
        Streak that tolerates MISS_TOLERANCE misses per 7-day window.
        Returns: streak, consistency_ratio, next_milestone.
        """
        days_executed = sum(
            1 for l in logs
            if getattr(l, "action_taken", False) or (getattr(l, "habits_completed", 0) or 0) > 0
        )
        n = max(1, len(logs))
        consistency_ratio = days_executed / n

        # Flexible streak: count consecutive "acceptable" days
        # A day is acceptable if executed OR it is within miss tolerance
        streak       = 0
        miss_buffer  = RetentionSystem.MISS_TOLERANCE
        for log in reversed(logs):
            executed = (
                getattr(log, "action_taken", False)
                or (getattr(log, "habits_completed", 0) or 0) > 0
            )
            if executed:
                streak += 1
            elif miss_buffer > 0:
                miss_buffer -= 1
                streak += 1   # tolerance used — streak continues
            else:
                break

        next_milestone = RetentionSystem._next_milestone(streak)

        return {
            "streak":             streak,
            "consistency_ratio":  round(consistency_ratio, 3),
            "days_executed":      days_executed,
            "days_tracked":       n,
            "next_milestone":     next_milestone,
        }

    @staticmethod
    def get_identity_signal(consistency_ratio: float, trend: str) -> Optional[str]:
        """
        Identity reinforcement — calibrated to trajectory, not isolated day.
        Returns a calm, factual identity observation. No hype.
        """
        if consistency_ratio >= 0.85 and trend == "improving":
            return "You are becoming more consistent under pressure. This is an identity-level shift, not a lucky streak."

        if consistency_ratio >= 0.70:
            return f"Consistency at {consistency_ratio:.0%} is above the threshold where behavioral patterns begin to consolidate."

        if consistency_ratio >= 0.50 and trend == "improving":
            return "Your consistency is improving. The trend matters more than the current ratio."

        if consistency_ratio < 0.40 and trend == "declining":
            return None   # no identity signal when truly struggling — system should intervene, not reinforce

        return None

    @staticmethod
    def should_reduce_prompts(session_count_today: int, burnout_score: float) -> bool:
        """
        Anti-burnout: reduce system prompts when overuse + burnout detected.
        If user has checked in 3+ times today and burnout is elevated, back off.
        """
        return session_count_today >= 3 and burnout_score > 0.50

    @staticmethod
    def _next_milestone(streak: int) -> Optional[str]:
        """Return the next meaningful milestone message."""
        milestones = {
            7:   "7-day mark — patterns at this frequency begin to stabilize.",
            14:  "14 days — behavioral baseline is shifting.",
            30:  "30 days — structural change at this consistency level.",
            60:  "60 days — this is identity-level behavior now.",
            100: "100-day mark — your behavioral architecture has changed.",
        }
        for threshold, msg in sorted(milestones.items()):
            if streak < threshold:
                days_away = threshold - streak
                return f"{days_away} days to the {threshold}-day mark. {msg}"
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _day_label(log: Any) -> Optional[str]:
    d = getattr(log, "log_date", None) or getattr(log, "timestamp", None)
    if d:
        return d.strftime("%A") if hasattr(d, "strftime") else str(d)
    return None

def _integrity_val(log: Any) -> float:
    si = getattr(log, "self_integrity", None)
    if si is not None:
        return float(si)
    sr = getattr(log, "self_respect", None)
    return {"yes": 1.0, "partial": 0.5, "no": 0.0}.get(sr or "partial", 0.5)
