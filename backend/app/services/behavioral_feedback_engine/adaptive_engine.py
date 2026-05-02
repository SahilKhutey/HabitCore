"""
AdaptiveEngine — The System Brain.

Determines user's behavioral state and produces SystemDirectives
that change how the ENTIRE app behaves.

This is not a feature flag system.
This is a psychological state machine.

4 States:
  stable      — consistent execution, moderate burnout risk
  struggling  — high avoidance, low integrity, declining trend
  overwhelmed — burnout risk active, depletion signals
  improving   — upward trend, above-threshold consistency

State determines:
  - How many check-in fields are shown
  - Whether streak pressure is applied
  - How much guidance the AI coach provides
  - Whether challenges and notifications are active
  - What focus_mode is applied to the UX

State-Adaptive Weights:
  The behavior score formula changes by state.
  When struggling, avoidance penalty is reduced (system is gentler).
  When stable, full accountability weights apply.

Critical design rule:
  The system NEVER applies streak pressure to an overwhelmed user.
  The system NEVER reduces guidance for a struggling user.
  The system NEVER increases challenge for an overwhelmed user.
"""
from typing import Dict, Any

from app.services.behavioral_feedback_engine.schemas import (
    UserSystemState, SystemDirectives
)


# ── Weight Tables (state-adjusted) ───────────────────────────────────────────

BASE_WEIGHTS = {
    "execution":  0.30,
    "avoidance":  0.20,   # penalty
    "cognitive":  0.15,
    "emotional":  0.10,
    "integrity":  0.15,
    "focus":      0.10,
}

STATE_WEIGHT_OVERRIDES: Dict[str, Dict[str, float]] = {
    "overwhelmed": {
        "execution":  0.25,
        "avoidance":  0.05,   # greatly reduced penalty — system is supportive
        "cognitive":  0.20,
        "emotional":  0.20,   # emotional signals weighted higher in crisis
        "integrity":  0.20,
        "focus":      0.10,
    },
    "struggling": {
        "execution":  0.30,
        "avoidance":  0.10,   # reduced penalty
        "cognitive":  0.20,
        "emotional":  0.15,
        "integrity":  0.15,
        "focus":      0.10,
    },
    "improving": {
        "execution":  0.30,
        "avoidance":  0.25,   # higher accountability
        "cognitive":  0.15,
        "emotional":  0.08,
        "integrity":  0.15,
        "focus":      0.07,
    },
    "stable": BASE_WEIGHTS,
}


class AdaptiveEngine:
    """
    Stateless state machine. Computes UserSystemState from features,
    then produces SystemDirectives consumed by frontend.
    """

    @staticmethod
    def determine_state(features: Dict[str, Any]) -> UserSystemState:
        """
        Classify user into one of 4 behavioral states.
        Priority order: overwhelmed > struggling > improving > stable.
        """
        burnout_risk    = features.get("burnout_risk", 0.0)
        avoidance_rate  = features.get("avoidance_rate", 0.0)
        trend           = features.get("trend", "stable")
        integrity_score = features.get("integrity_score", 0.5)
        avg_energy_num  = features.get("avg_energy_num", 2.0)
        progress_ratio  = features.get("progress_ratio", 0.5)

        # overwhelmed: burnout active OR multiple depletion signals
        if burnout_risk > 0.60:
            return UserSystemState.OVERWHELMED

        high_avoidance  = avoidance_rate > 0.50
        low_integrity   = integrity_score < 0.40
        low_energy      = avg_energy_num < 1.5
        declining_trend = trend == "declining"

        if sum([high_avoidance, low_integrity, low_energy, declining_trend]) >= 2:
            return UserSystemState.OVERWHELMED

        # struggling: two or more risk factors
        if sum([high_avoidance, low_integrity, declining_trend]) >= 2:
            return UserSystemState.STRUGGLING

        if avoidance_rate > 0.40 or integrity_score < 0.50:
            return UserSystemState.STRUGGLING

        # improving: clear upward trajectory
        if trend == "improving" and progress_ratio >= 0.65:
            return UserSystemState.IMPROVING

        return UserSystemState.STABLE

    @staticmethod
    def produce_directives(state: UserSystemState) -> SystemDirectives:
        """
        Map state to full system directives.
        These directives control frontend behavior completely.
        """
        if state == UserSystemState.OVERWHELMED:
            return SystemDirectives(
                state=state,
                reduce_inputs=True,
                max_input_fields=4,               # morning-level minimal input
                disable_streak_pressure=True,
                disable_notifications=True,
                disable_challenges=True,
                increase_guidance=True,
                show_intervention=True,
                increase_challenge=False,
                focus_mode="recovery",
                micro_tasks_only=True,
            )

        if state == UserSystemState.STRUGGLING:
            return SystemDirectives(
                state=state,
                reduce_inputs=False,
                max_input_fields=6,
                disable_streak_pressure=True,
                disable_notifications=False,
                disable_challenges=True,
                increase_guidance=True,
                show_intervention=True,
                increase_challenge=False,
                focus_mode="reflection",
                micro_tasks_only=True,
            )

        if state == UserSystemState.IMPROVING:
            return SystemDirectives(
                state=state,
                reduce_inputs=False,
                max_input_fields=8,
                disable_streak_pressure=False,
                disable_notifications=False,
                disable_challenges=False,
                increase_guidance=False,
                show_intervention=False,
                increase_challenge=True,
                focus_mode="growth",
                micro_tasks_only=False,
            )

        # STABLE (default)
        return SystemDirectives(
            state=state,
            reduce_inputs=False,
            max_input_fields=8,
            disable_streak_pressure=False,
            disable_notifications=False,
            disable_challenges=False,
            increase_guidance=False,
            show_intervention=False,
            increase_challenge=False,
            focus_mode="action",
            micro_tasks_only=False,
        )

    @staticmethod
    def get_weights(state: UserSystemState) -> Dict[str, float]:
        """Get state-adjusted scoring weights."""
        return STATE_WEIGHT_OVERRIDES.get(state.value, BASE_WEIGHTS)

    @staticmethod
    def get_state_label(state: UserSystemState) -> str:
        labels = {
            UserSystemState.STABLE:      "Stable",
            UserSystemState.STRUGGLING:  "Struggling",
            UserSystemState.OVERWHELMED: "Overwhelmed",
            UserSystemState.IMPROVING:   "Improving",
        }
        return labels.get(state, "Unknown")
