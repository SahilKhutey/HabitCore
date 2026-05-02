"""
InsightGenerator — converts ML correlation coefficients into human-readable insights.

All messages are calibrated to the v2 language guide:
  ✅ Specific, evidence-referenced, calm
  ✅ Identity-anchored where possible
  ❌ No exclamation marks
  ❌ No motivational filler ("You got this!")
  ❌ No vague generics ("Keep trying!")

Correlations use confidence = |r| value directly as the confidence score.
"""
from typing import List, Dict, Any, Optional


RawInsight = Dict[str, Any]

# Minimum |r| to surface a correlation-based insight
STRONG_THRESHOLD   = 0.55
MODERATE_THRESHOLD = 0.35


class InsightGenerator:
    """
    Generates typed insight dicts from correlation coefficients.
    Each method maps one correlation to zero or one insight.
    """

    @staticmethod
    def from_correlations(corr: Dict[str, float]) -> List[RawInsight]:
        """
        Run all correlation → insight mappings.
        Only surfaces insights where correlation exceeds the moderate threshold.
        """
        if not corr:
            return []

        generators = [
            InsightGenerator._from_sleep_completion,
            InsightGenerator._from_mood_completion,
            InsightGenerator._from_energy_completion,
            InsightGenerator._from_sleep_mood,
            InsightGenerator._from_variability,
        ]

        insights = []
        for gen in generators:
            result = gen(corr)
            if result is not None:
                insights.append(result)
        return insights

    # ── Individual correlation mappings ──────────────────────────────────────

    @staticmethod
    def _from_sleep_completion(corr: Dict) -> Optional[RawInsight]:
        r = corr.get("sleep_vs_completion", 0.0)
        if r > STRONG_THRESHOLD:
            return {
                "type": "pattern",
                "category": "sleep",
                "message": (
                    "Your data shows a strong correlation between sleep and habit completion. "
                    "When you sleep well, you execute. This is physiological, not motivational."
                ),
                "action_hint": "Sleep is a performance input. Protect it as you would your best habit.",
                "confidence": round(abs(r), 3),
                "impact": 0.90,
                "trigger_key": "ml_sleep_completion_strong",
            }
        elif r > MODERATE_THRESHOLD:
            return {
                "type": "pattern",
                "category": "sleep",
                "message": (
                    "There is a moderate link in your data between sleep quality and habit completion. "
                    "Better rest tends to correlate with better follow-through."
                ),
                "action_hint": "Track sleep quality for 7 more days to confirm this pattern.",
                "confidence": round(abs(r), 3),
                "impact": 0.75,
                "trigger_key": "ml_sleep_completion_moderate",
            }
        return None

    @staticmethod
    def _from_mood_completion(corr: Dict) -> Optional[RawInsight]:
        r = corr.get("mood_vs_completion", 0.0)
        if r > STRONG_THRESHOLD:
            return {
                "type": "pattern",
                "category": "mood",
                "message": (
                    "Your completion data correlates strongly with mood. "
                    "Emotional state is functioning as a primary driver — "
                    "not just a backdrop — of your behavioral output."
                ),
                "action_hint": (
                    "Consider mood regulation as a direct habit. "
                    "A morning check-in or brief reflection may stabilize your baseline."
                ),
                "confidence": round(abs(r), 3),
                "impact": 0.85,
                "trigger_key": "ml_mood_completion_strong",
            }
        elif r > MODERATE_THRESHOLD:
            return {
                "type": "pattern",
                "category": "mood",
                "message": (
                    "Your mood shows a moderate influence on daily habit completion. "
                    "On lower-mood days, your follow-through tends to decrease."
                ),
                "action_hint": "Log mood daily. Awareness of the pattern reduces its impact.",
                "confidence": round(abs(r), 3),
                "impact": 0.70,
                "trigger_key": "ml_mood_completion_moderate",
            }
        return None

    @staticmethod
    def _from_energy_completion(corr: Dict) -> Optional[RawInsight]:
        r = corr.get("energy_vs_completion", 0.0)
        if r > STRONG_THRESHOLD:
            return {
                "type": "pattern",
                "category": "energy",
                "message": (
                    "Energy level is your strongest predictor of habit completion. "
                    "Your system runs on energy as its core fuel — not willpower."
                ),
                "action_hint": (
                    "Identify what precedes high-energy mornings. "
                    "Replicate those inputs rather than relying on discipline alone."
                ),
                "confidence": round(abs(r), 3),
                "impact": 0.88,
                "trigger_key": "ml_energy_completion_strong",
            }
        return None

    @staticmethod
    def _from_sleep_mood(corr: Dict) -> Optional[RawInsight]:
        r = corr.get("sleep_vs_mood", 0.0)
        if r > STRONG_THRESHOLD:
            return {
                "type": "pattern",
                "category": "sleep",
                "message": (
                    "In your data, sleep quality predicts your mood the following day. "
                    "This is a cascade: sleep → mood → behavioral output."
                ),
                "action_hint": "Optimizing sleep addresses two downstream variables simultaneously.",
                "confidence": round(abs(r), 3),
                "impact": 0.82,
                "trigger_key": "ml_sleep_mood_cascade",
            }
        return None

    @staticmethod
    def _from_variability(corr: Dict) -> Optional[RawInsight]:
        std = corr.get("variability", 0.0)
        if std > 0.35:
            return {
                "type": "pattern",
                "category": "consistency",
                "message": (
                    "Your completion rate shows high day-to-day variation — "
                    "some days strong, others absent. Instability at this level "
                    "prevents habit consolidation regardless of streak length."
                ),
                "action_hint": (
                    "Focus on reducing the lows rather than maximizing the highs. "
                    "A floor of 50% every day outperforms 100% / 0% cycles."
                ),
                "confidence": 0.80,
                "impact": 0.78,
                "trigger_key": "ml_variability_high",
            }
        return None
