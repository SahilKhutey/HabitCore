"""
PatternRules — high-precision rule-based insight detection.

Rules are deterministic: they fire on threshold conditions with high confidence.
Output messages follow the v2 language guide: calm, specific, identity-framed.

Each rule returns None (no insight) or an insight dict:
  {type, category, message, action_hint, confidence, impact, trigger_key}
"""
from typing import List, Dict, Any, Optional


RawInsight = Dict[str, Any]


class PatternRules:
    """
    Rule set ordered by impact. Each rule is a pure function of the
    aggregated feature dict. Rules with trigger_key are deduplicated
    by the InsightStore before persisting.
    """

    # ── Thresholds ──────────────────────────────────────────────────────────

    SLEEP_CRITICAL_HOURS   = 5.5   # below this: high-impact warning
    SLEEP_LOW_HOURS        = 6.5   # below this: moderate warning
    BURNOUT_COMPLETION_LOW = 0.35  # high risk zone
    BURNOUT_RECENT_DROP    = 0.25  # recent trend drop vs. avg
    OVERLOAD_TOTAL_THRESHOLD = 5   # too many habits for current energy
    CONSISTENCY_STRONG     = 0.80  # growth insight territory
    CONSISTENCY_EXCELLENT  = 0.92  # elite territory
    MOOD_LOW_THRESHOLD     = 2.2   # persistent low mood warning
    REFLECTION_BENEFIT_MIN = 0.3   # reflection rate needed to surface benefit insight

    @staticmethod
    def detect(agg: Dict[str, float], extra: Dict[str, Any] = None) -> List[RawInsight]:
        """
        Run all rules against the aggregated feature dict.

        Args:
            agg:   Output of FeatureExtractor.aggregate()
            extra: Optional extra context (habit_count, archetype, etc.)

        Returns:
            List of raw insight dicts (unsaved, unranked).
        """
        extra = extra or {}
        rules = [
            PatternRules._rule_critical_sleep,
            PatternRules._rule_low_sleep,
            PatternRules._rule_high_burnout_risk,
            PatternRules._rule_recent_performance_drop,
            PatternRules._rule_habit_overload,
            PatternRules._rule_low_persistent_mood,
            PatternRules._rule_strong_consistency,
            PatternRules._rule_excellent_consistency,
            PatternRules._rule_reflection_benefit,
            PatternRules._rule_energy_fatigue,
        ]

        insights = []
        for rule in rules:
            result = rule(agg, extra)
            if result is not None:
                insights.append(result)

        return insights

    # ── Individual Rules ─────────────────────────────────────────────────────

    @staticmethod
    def _rule_critical_sleep(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_sleep"] < PatternRules.SLEEP_CRITICAL_HOURS:
            return {
                "type": "warning",
                "category": "sleep",
                "message": (
                    f"Your average sleep is {agg['avg_sleep']:.1f} hours — "
                    "significantly below what your system needs. This directly reduces consistency."
                ),
                "action_hint": "Prioritize 7 hours of sleep before adjusting habits.",
                "confidence": 0.95,
                "impact": 0.90,
                "trigger_key": "sleep_critical",
            }
        return None

    @staticmethod
    def _rule_low_sleep(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if PatternRules.SLEEP_CRITICAL_HOURS <= agg["avg_sleep"] < PatternRules.SLEEP_LOW_HOURS:
            return {
                "type": "warning",
                "category": "sleep",
                "message": (
                    f"Sleep is averaging {agg['avg_sleep']:.1f} hours. "
                    "Behavioral research indicates this range reduces willpower and decision quality."
                ),
                "action_hint": "Add 30–60 minutes to your sleep window this week.",
                "confidence": 0.88,
                "impact": 0.80,
                "trigger_key": "sleep_low",
            }
        return None

    @staticmethod
    def _rule_high_burnout_risk(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_completion"] < PatternRules.BURNOUT_COMPLETION_LOW:
            return {
                "type": "warning",
                "category": "consistency",
                "message": (
                    f"Completion rate is {agg['avg_completion']*100:.0f}% — "
                    "well below sustainable levels. Your system may be overloaded or depleted."
                ),
                "action_hint": "Reduce active habits to 2–3 and focus on fundamentals.",
                "confidence": 0.90,
                "impact": 0.88,
                "trigger_key": "burnout_high",
            }
        return None

    @staticmethod
    def _rule_recent_performance_drop(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        drop = agg["avg_completion"] - agg["recent_completion"]
        if drop > PatternRules.BURNOUT_RECENT_DROP and agg["sample_size"] >= 5:
            return {
                "type": "warning",
                "category": "consistency",
                "message": (
                    f"Your last 3 days show a {drop*100:.0f}% drop in completion "
                    "compared to your baseline. An early intervention is more effective now."
                ),
                "action_hint": "Identify one habit to pause temporarily and assess load.",
                "confidence": 0.82,
                "impact": 0.78,
                "trigger_key": "recent_drop",
            }
        return None

    @staticmethod
    def _rule_habit_overload(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        habit_count = extra.get("habit_count", 0)
        if habit_count > PatternRules.OVERLOAD_TOTAL_THRESHOLD and agg["avg_energy"] < 2.0:
            return {
                "type": "warning",
                "category": "overload",
                "message": (
                    f"You have {habit_count} active habits while your energy is consistently low. "
                    "More habits do not compound — they fragment."
                ),
                "action_hint": f"Archive {habit_count - 3} lower-priority habits this week.",
                "confidence": 0.87,
                "impact": 0.82,
                "trigger_key": "habit_overload",
            }
        return None

    @staticmethod
    def _rule_low_persistent_mood(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_mood"] < PatternRules.MOOD_LOW_THRESHOLD and agg["sample_size"] >= 4:
            return {
                "type": "warning",
                "category": "mood",
                "message": (
                    "Your mood has been consistently low over the past week. "
                    "Sustained low affect reduces behavioral activation — the foundation of habit execution."
                ),
                "action_hint": "Consider a recovery protocol: reduce habit load and add one restorative activity.",
                "confidence": 0.85,
                "impact": 0.75,
                "trigger_key": "mood_low_persistent",
            }
        return None

    @staticmethod
    def _rule_strong_consistency(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if PatternRules.CONSISTENCY_STRONG <= agg["avg_completion"] < PatternRules.CONSISTENCY_EXCELLENT:
            return {
                "type": "growth",
                "category": "consistency",
                "message": (
                    f"Completion rate at {agg['avg_completion']*100:.0f}%. "
                    "At this frequency, behaviors begin automating — "
                    "the hallmark of genuine habit formation."
                ),
                "action_hint": "Maintain this load. Consistency here is more valuable than adding new habits.",
                "confidence": 0.88,
                "impact": 0.70,
                "trigger_key": "consistency_strong",
            }
        return None

    @staticmethod
    def _rule_excellent_consistency(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_completion"] >= PatternRules.CONSISTENCY_EXCELLENT:
            return {
                "type": "growth",
                "category": "consistency",
                "message": (
                    f"Completion rate at {agg['avg_completion']*100:.0f}%. "
                    "This level of consistency is rare. Your behavioral baseline is shifting."
                ),
                "action_hint": "You have capacity to introduce one additional habit aligned to your archetype.",
                "confidence": 0.93,
                "impact": 0.75,
                "trigger_key": "consistency_excellent",
            }
        return None

    @staticmethod
    def _rule_reflection_benefit(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_reflection_rate"] >= PatternRules.REFLECTION_BENEFIT_MIN:
            return {
                "type": "growth",
                "category": "consistency",
                "message": (
                    "You have been logging reflections regularly. "
                    "Users who reflect show measurably higher habit retention over time."
                ),
                "action_hint": None,
                "confidence": 0.78,
                "impact": 0.65,
                "trigger_key": "reflection_benefit",
            }
        return None

    @staticmethod
    def _rule_energy_fatigue(agg: Dict, extra: Dict) -> Optional[RawInsight]:
        if agg["avg_energy"] <= 1.3 and agg["avg_completion"] < 0.6:
            return {
                "type": "warning",
                "category": "energy",
                "message": (
                    "Sustained low energy combined with reduced completion suggests systemic fatigue. "
                    "This is not a motivation issue — it is a recovery issue."
                ),
                "action_hint": "Treat this as a recovery phase. Physical rest precedes behavioral recovery.",
                "confidence": 0.86,
                "impact": 0.83,
                "trigger_key": "energy_fatigue",
            }
        return None
