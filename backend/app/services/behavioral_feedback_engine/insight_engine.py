"""
InsightEngine — Converts patterns + features into meaning.

4 insight types (strictly enforced):
  "pattern"       — a detected behavioral regularity
  "contradiction" — a gap between intention and action
  "progress"      — genuine forward movement
  "warning"       — risk signal requiring attention

UX rule: MAX 2 insights shown per session.
The system selects the 2 highest-confidence insights.

Language rules (v2 invariant):
  ✅ Specific ("on 4 of 7 days")
  ✅ Evidence-referenced ("your logs show")
  ✅ Behaviorally framed (not emotionally charged)
  ❌ No exclamation marks
  ❌ No "Great job!", "Amazing!", "Keep it up!"
  ❌ No vague statements ("You seem stressed")

Ethical retention hook (curiosity, not dopamine):
  "We're tracking this pattern — 2 more days to confirm."
  "This is emerging. Check back tomorrow."
"""
from typing import List, Dict, Any, Optional

from app.services.behavioral_feedback_engine.schemas import (
    BFEInsight, DetectedPattern, UserSystemState
)


INSIGHT_TYPES = ["pattern", "contradiction", "progress", "warning"]


class InsightEngine:
    """Stateless insight generator from patterns + features."""

    @staticmethod
    def generate(
        patterns:  List[DetectedPattern],
        features:  Dict[str, Any],
        state:     UserSystemState,
    ) -> List[BFEInsight]:
        """
        Generate insights from patterns and computed features.
        Returns sorted list (highest confidence first), capped at 5.
        Frontend shows max 2.
        """
        insights: List[BFEInsight] = []

        # ── 1. Pattern insights ────────────────────────────────────────────
        for p in patterns[:3]:   # top 3 patterns → insights
            action = InsightEngine._pattern_to_action(p.type)
            curiosity = InsightEngine._curiosity_hook(p)

            insights.append(BFEInsight(
                type="pattern",
                message=p.message,
                confidence=p.confidence,
                action=action,
                curiosity_hook=curiosity,
            ))

        # ── 2. Contradiction insights ─────────────────────────────────────
        integrity = features.get("integrity_score", 0.5)
        if integrity < 0.40:
            insights.append(BFEInsight(
                type="contradiction",
                message=f"Your actions are misaligned with your stated intentions on {(1-integrity):.0%} of tracked days. This gap is the primary source of reduced self-respect.",
                confidence=0.85,
                action="Pick one specific action — not a system overhaul — that the person you intend to be would take in the next 2 hours.",
            ))
        elif integrity < 0.60:
            insights.append(BFEInsight(
                type="contradiction",
                message="Partial alignment detected. On roughly half of tracked days, you acted against your stated values.",
                confidence=0.72,
                action="Identify the one context where the gap is largest and address only that.",
            ))

        # ── 3. Warning insights ───────────────────────────────────────────
        burnout_risk = features.get("burnout_risk", 0.0)
        if burnout_risk > 0.65:
            insights.append(BFEInsight(
                type="warning",
                message=f"Burnout risk at {burnout_risk:.0%}. Multiple depletion signals are active simultaneously.",
                confidence=0.88,
                action="Reduce tomorrow's intended behaviors to one. Rest is a behavioral strategy.",
            ))
        elif burnout_risk > 0.45:
            insights.append(BFEInsight(
                type="warning",
                message="Early depletion signals present. Sustained input at this load level risks a dropout event.",
                confidence=0.70,
                action="Remove one non-essential behavior from tomorrow's plan.",
            ))

        # Avoidance rate warning
        avoidance_rate = features.get("avoidance_rate", 0.0)
        if avoidance_rate > 0.55:
            insights.append(BFEInsight(
                type="warning",
                message=f"Task avoidance rate is {avoidance_rate:.0%}. At this frequency, avoidance becomes the default behavioral pathway.",
                confidence=0.80,
                action="For the most-avoided task, schedule a 2-minute version only. Execution matters more than duration.",
            ))

        # Relapse pattern warning
        relapse = next((p for p in patterns if p.type == "relapse_pattern"), None)
        if relapse:
            insights.append(BFEInsight(
                type="warning",
                message=relapse.message,
                confidence=relapse.confidence,
                action="When you miss one day, execute one 5-minute version of any habit immediately the next morning. This breaks the dropout cascade.",
            ))

        # ── 4. Progress insights ──────────────────────────────────────────
        progress_ratio = features.get("progress_ratio", 0.0)
        trend          = features.get("trend", "stable")

        if trend == "improving":
            insights.append(BFEInsight(
                type="progress",
                message="Behavioral consistency is trending upward over the tracked period. This trajectory, maintained, produces identity-level change.",
                confidence=0.78,
                action=None,
            ))

        consistency_pattern = next((p for p in patterns if p.type == "consistency_improving"), None)
        if consistency_pattern:
            insights.append(BFEInsight(
                type="progress",
                message=consistency_pattern.message,
                confidence=consistency_pattern.confidence,
                action=None,
            ))

        # ── Sort and cap ───────────────────────────────────────────────────
        insights.sort(key=lambda x: x.confidence, reverse=True)
        return insights[:5]   # system generates up to 5; UX shows 2

    @staticmethod
    def select_top_insight(insights: List[BFEInsight]) -> Optional[BFEInsight]:
        """
        Select the single highest-confidence insight for the primary card.
        Warnings take priority over patterns at equal confidence.
        """
        if not insights:
            return None

        warnings = [i for i in insights if i.type == "warning"]
        if warnings:
            return warnings[0]

        return insights[0]

    @staticmethod
    def _pattern_to_action(pattern_type: str) -> Optional[str]:
        """
        Map pattern type to a specific 1-sentence micro-action.
        This is the intervention layer for patterns (not loops).
        """
        actions = {
            "energy_avoidance_link":    "On your next low-energy day, do a 2-minute version of one intended task before making the avoidance decision.",
            "thought_behavior_link":    "Notice the thought before acting on it. Label it: 'This is a trigger thought.' Then take one small action.",
            "relapse_pattern":          "After any missed day, execute one 5-minute behavior first thing the next morning.",
            "focus_degradation":        "Schedule one 30-minute distraction-free block before any other work tomorrow.",
            "integrity_erosion":        "Identify the one commitment where the gap between intention and action is largest. Address only that.",
            "emotional_behavior_link":  "When that emotion appears, name it explicitly, then take one action — however small — before acting on the avoidance impulse.",
            "consistency_improving":    None,   # progress — no action needed
        }
        return actions.get(pattern_type)

    @staticmethod
    def _curiosity_hook(pattern: DetectedPattern) -> Optional[str]:
        """
        Ethical retention: create behavioral curiosity, not dopamine dependency.
        Only shown for patterns with moderate confidence (not yet fully confirmed).
        """
        if pattern.confidence >= 0.85:
            return None   # already confirmed — no hook needed

        days_to_confirm = max(1, round((0.85 - pattern.confidence) / 0.08))

        hooks = {
            "energy_avoidance_link":  f"This pattern is forming. {days_to_confirm} more days of data will confirm it.",
            "thought_behavior_link":  f"This thought-behavior link is emerging. Track tomorrow to see if it holds.",
            "relapse_pattern":        f"Dropout pattern detected. {days_to_confirm} more days will determine if this is structural.",
            "focus_degradation":      "Focus trend is developing. Tomorrow's data will clarify the direction.",
            "integrity_erosion":      "Alignment trend is forming. One day of recovery shifts this meaningfully.",
        }
        return hooks.get(pattern.type)
