"""
StateEngine — v2 Production-Grade User Mode System

The StateEngine is the global behavioral control plane.
It determines USER MODE which cascades to ALL other layers:
  - Intelligence Layer: AI tone and context
  - Experience Layer: reward intensity, gamification pressure
  - Adaptive Layer: habit difficulty, notification frequency
  - UI Layer: calm/normal/high-performance visual mode

State Transition Rules:
  ANY → BURNOUT        burnout_score > 0.6
  BURNOUT → RECOVERY   auto on burnout detection
  RECOVERY → NORMAL    after 3 days + burnout_score < 0.3
  NORMAL → HIGH_PERF   streak >= 14 AND completion >= 0.90 AND engagement >= 85
  HIGH_PERF → NORMAL   streak broken OR completion < 0.75

CRITICAL: Experience Layer CANNOT override state-driven limits.
  e.g. BURNOUT mode disables streak pressure, gamification pressure, new habit suggestions.
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class UserMode(str, Enum):
    NORMAL       = "normal"
    BURNOUT      = "burnout"
    RECOVERY     = "recovery"
    HIGH_PERF    = "high_performance"


@dataclass
class UserState:
    """
    Complete user behavioral state snapshot.
    Computed by StateEngine, consumed by all other layers.
    """
    mode: UserMode
    burnout_score: float          # 0.0–1.0
    engagement_score: float       # 0.0–100.0
    completion_rate: float        # 0.0–1.0
    streak: int
    energy_level: str             # "high" | "medium" | "low"

    # Mode-derived controls (consumed by experience + AI layers)
    max_active_habits: int
    ai_tone: str                  # "supportive" | "analytical" | "gentle" | "challenging"
    reward_intensity: str         # "minimal" | "normal" | "elevated"
    notification_frequency: str   # "minimal" | "low" | "normal" | "high"
    streak_pressure: bool         # False in BURNOUT/RECOVERY
    allow_new_habits: bool

    # Metadata
    computed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "burnout_score": round(self.burnout_score, 3),
            "engagement_score": round(self.engagement_score, 1),
            "completion_rate": round(self.completion_rate, 3),
            "streak": self.streak,
            "energy_level": self.energy_level,
            "controls": {
                "max_active_habits": self.max_active_habits,
                "ai_tone": self.ai_tone,
                "reward_intensity": self.reward_intensity,
                "notification_frequency": self.notification_frequency,
                "streak_pressure": self.streak_pressure,
                "allow_new_habits": self.allow_new_habits,
            },
            "computed_at": self.computed_at,
        }


# ── State configuration matrix ────────────────────────────────────────────────

_STATE_CONFIG: Dict[UserMode, Dict[str, Any]] = {
    UserMode.NORMAL: {
        "max_active_habits":      10,
        "ai_tone":                "analytical",
        "reward_intensity":       "normal",
        "notification_frequency": "normal",
        "streak_pressure":        True,
        "allow_new_habits":       True,
    },
    UserMode.BURNOUT: {
        "max_active_habits":      3,
        "ai_tone":                "gentle",
        "reward_intensity":       "minimal",
        "notification_frequency": "low",
        "streak_pressure":        False,
        "allow_new_habits":       False,
    },
    UserMode.RECOVERY: {
        "max_active_habits":      2,
        "ai_tone":                "supportive",
        "reward_intensity":       "minimal",
        "notification_frequency": "minimal",
        "streak_pressure":        False,
        "allow_new_habits":       False,
    },
    UserMode.HIGH_PERF: {
        "max_active_habits":      15,
        "ai_tone":                "challenging",
        "reward_intensity":       "elevated",
        "notification_frequency": "high",
        "streak_pressure":        True,
        "allow_new_habits":       True,
    },
}

# ── Thresholds ────────────────────────────────────────────────────────────────

BURNOUT_THRESHOLD    = 0.60   # v2: lowered from 0.70 for earlier intervention
RECOVERY_CLEAR_SCORE = 0.30   # below this = cleared from burnout
HIGH_PERF_STREAK     = 14
HIGH_PERF_COMPLETION = 0.90
HIGH_PERF_ENGAGEMENT = 85.0


class StateEngine:
    """
    v2 StateEngine — globally controls system behavior based on user's behavioral state.
    Stateless: computes UserState from raw metrics on every call.
    """

    @staticmethod
    def compute(
        burnout_score: float,
        completion_rate: float,
        streak: int,
        energy_level: str = "medium",
        recovery_plan_active: bool = False,
        session_frequency: float = 5.0,
        recent_activity: int = 8,
    ) -> UserState:
        """
        Compute full UserState from behavioral metrics.
        This is the single source of truth for system behavior mode.
        """
        engagement_score = StateEngine._compute_engagement(
            streak, completion_rate, session_frequency, recent_activity
        )

        mode = StateEngine._determine_mode(
            burnout_score, completion_rate, streak, engagement_score, recovery_plan_active
        )

        config = _STATE_CONFIG[mode]

        return UserState(
            mode=mode,
            burnout_score=burnout_score,
            engagement_score=engagement_score,
            completion_rate=completion_rate,
            streak=streak,
            energy_level=energy_level,
            **config,
        )

    @staticmethod
    def _determine_mode(
        burnout_score: float,
        completion_rate: float,
        streak: int,
        engagement: float,
        recovery_active: bool,
    ) -> UserMode:
        """Mode selection cascade — order matters."""
        if recovery_active:
            return UserMode.RECOVERY

        if burnout_score >= BURNOUT_THRESHOLD:
            return UserMode.BURNOUT

        if (
            streak >= HIGH_PERF_STREAK
            and completion_rate >= HIGH_PERF_COMPLETION
            and engagement >= HIGH_PERF_ENGAGEMENT
        ):
            return UserMode.HIGH_PERF

        return UserMode.NORMAL

    @staticmethod
    def _compute_engagement(
        streak: int,
        completion_rate: float,
        session_frequency: float,
        recent_activity: int,
    ) -> float:
        """Weighted engagement score 0–100."""
        score = (
            min(streak, 30) / 30 * 30 +
            completion_rate * 40 +
            min(session_frequency, 7) / 7 * 20 +
            min(recent_activity, 10) / 10 * 10
        )
        return round(min(score, 100.0), 2)

    @staticmethod
    def get_ai_context(state: UserState) -> Dict[str, str]:
        """
        Returns AI prompt context directives derived from state.
        Consumed by AICoachService to calibrate response tone.
        """
        tone_directives = {
            "gentle":      "The user is in a low state. Be calm, brief, and compassionate. No pressure.",
            "supportive":  "The user is recovering. Acknowledge progress, suggest minimal action.",
            "analytical":  "Provide behavioral analysis. Be specific and evidence-based.",
            "challenging": "The user is performing well. You can suggest ambitious next steps.",
        }
        return {
            "tone_directive":  tone_directives.get(state.ai_tone, tone_directives["analytical"]),
            "mode":            state.mode.value,
            "burnout_context": f"Burnout score: {state.burnout_score:.0%}" if state.burnout_score > 0.3 else "Burnout not detected.",
            "streak_context":  f"Current streak: {state.streak} days.",
        }

    @staticmethod
    def apply_recovery_controls(habits: List[Any], state: UserState) -> List[Any]:
        """
        In BURNOUT or RECOVERY mode, returns only the top N habits by priority.
        Enforces max_active_habits limit. Called before rendering today's habit list.
        """
        if state.mode in (UserMode.BURNOUT, UserMode.RECOVERY):
            return habits[: state.max_active_habits]
        return habits
