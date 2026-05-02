"""
InsightBuilder — Human-level cognitive insight generation.

This is the output engine of the CognitiveEngine.
It converts features + driver maps + burnout assessments
into specific, evidence-grounded, v2-language insights.

v2 language invariant (ALL insights must follow):
  ✅ Specific: references actual data ("60% of logged days", "3 consecutive")
  ✅ Non-judgmental: no blame, no pressure
  ✅ Evidence-based: explains the psychological mechanism
  ✅ Actionable: ends with a concrete, achievable step
  ❌ No exclamation marks
  ❌ No generic filler ("Great job!", "Keep trying!")
  ❌ No vague observations ("You seem stressed")

Insight types:
  "cognitive"  — thought patterns, distortions, reframing effectiveness
  "driver"     — energy inputs/drains
  "identity"   — self-respect alignment, values-behavior gap
  "behavior"   — avoidance, deep work, consistency
  "burnout"    — burnout risk with specific signals
  "progress"   — growth trajectory, identity evolution
"""
from typing import List, Dict, Any


class InsightBuilder:
    """
    Stateless insight generator.
    Combines all feature signals into a ranked, deduplicated insight list.
    """

    @staticmethod
    def generate(
        features: Dict[str, Any],
        driver_map: Dict[str, Any],
        burnout: Any,   # BurnoutAssessment
        distortions_list: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate the full insight set from all signals.
        Returns insights sorted by confidence (highest first).
        Max 8 insights per run to prevent overload.
        """
        insights: List[Dict[str, Any]] = []
        n = features.get("sample_size", 1)

        # ── 1. Burnout insights (highest priority) ─────────────────────────
        if burnout.detected:
            insights.append({
                "type":       "burnout",
                "category":   "state",
                "message":    burnout.recommended_action,
                "confidence": burnout.confidence,
                "action_hint": "Activate recovery protocol: reduce habit count for 3 days.",
                "signals":    burnout.signals,
            })

        elif burnout.severity == "moderate":
            insights.append({
                "type":       "burnout",
                "category":   "state",
                "message":    "Early depletion signals are present across multiple indicators.",
                "confidence": 0.65,
                "action_hint": "Reduce discretionary commitments this week.",
            })

        # ── 2. Cognitive distortion insights ──────────────────────────────
        neg_ratio = features.get("negative_thought_ratio", 0.0)
        distortions = features.get("distortions_detected", [])

        if neg_ratio > 0.60:
            insights.append({
                "type":       "cognitive",
                "category":   "distortion",
                "message":    (
                    f"In {neg_ratio:.0%} of logged days, your recorded thoughts were classified as harmful. "
                    "Repeated negative self-talk correlates with reduced behavioral consistency."
                ),
                "confidence": 0.80,
                "action_hint": "When you notice a self-critical thought, pause and ask: 'Is this factually accurate?'",
            })

        if "catastrophizing" in distortions:
            insights.append({
                "type":       "cognitive",
                "category":   "distortion",
                "message":    "Catastrophizing patterns are present in your thought logs. This distortion amplifies perceived consequences and increases avoidance.",
                "confidence": 0.78,
                "action_hint": "Practice the 'realistic scenario' exercise: identify the most likely outcome, not the worst.",
            })

        if "all_or_nothing" in distortions:
            insights.append({
                "type":       "cognitive",
                "category":   "distortion",
                "message":    "All-or-nothing thinking is affecting how you evaluate your performance. Partial completion is still behavioral data.",
                "confidence": 0.76,
                "action_hint": "Replace 'I failed' with 'I completed X% — what made the rest harder?'",
            })

        if "labeling" in distortions:
            insights.append({
                "type":       "cognitive",
                "category":   "distortion",
                "message":    "Self-labeling patterns detected. Attaching global identities to single events distorts your progress assessment.",
                "confidence": 0.82,
                "action_hint": "Describe what happened specifically, not what you 'are'. 'I skipped today' vs 'I am lazy'.",
            })

        # Reframing effectiveness
        shift = features.get("avg_belief_shift", 0.0)
        if shift > 0.25:
            insights.append({
                "type":       "cognitive",
                "category":   "growth",
                "message":    f"Your reframing practice is showing measurable effect — an average {shift:.0%} reduction in belief strength after reframing.",
                "confidence": 0.72,
                "action_hint": None,
            })

        # ── 3. Identity alignment insights ────────────────────────────────
        sr = features.get("self_respect_score", 0.5)
        if sr < 0.40:
            insights.append({
                "type":       "identity",
                "category":   "alignment",
                "message":    (
                    f"Your self-respect score of {sr:.0%} indicates that your actions are frequently "
                    "misaligned with your intended identity. This gap is a primary driver of motivation decline."
                ),
                "confidence": 0.85,
                "action_hint": "Identify one action per day that you can take as the person you intend to be — even a 2-minute version.",
            })
        elif sr < 0.55:
            insights.append({
                "type":       "identity",
                "category":   "alignment",
                "message":    "Partial identity alignment detected. On roughly half of tracked days, your actions were not fully consistent with your values.",
                "confidence": 0.70,
                "action_hint": "Pick one high-alignment habit and protect it as a non-negotiable for 7 days.",
            })

        # ── 4. Avoidance / behavior insights ──────────────────────────────
        avoidance = features.get("avoidance_rate", 0.0)
        if avoidance > 0.50:
            insights.append({
                "type":       "behavior",
                "category":   "avoidance",
                "message":    (
                    f"Task avoidance rate of {avoidance:.0%} — more than half of intended behaviors are being skipped. "
                    "Avoidance provides short-term relief but compounds behavioral debt."
                ),
                "confidence": 0.80,
                "action_hint": "For avoided tasks, schedule a 5-minute version only. Start before feeling ready.",
            })

        deep_work = features.get("deep_work_ratio", 0.5)
        if deep_work < 0.30:
            insights.append({
                "type":       "behavior",
                "category":   "focus",
                "message":    f"Deep work represents only {deep_work:.0%} of tracked work time. Fragmented attention reduces output quality and cognitive recovery.",
                "confidence": 0.70,
                "action_hint": "Block one 45-minute deep work session before any meetings or reactive tasks.",
            })

        # ── 5. Driver insights ─────────────────────────────────────────────
        from app.services.cognitive_engine.driver_mapper import DriverMapper
        driver_insights = DriverMapper.generate_driver_insights(driver_map)
        insights.extend(driver_insights)

        # ── 6. Progress insights ───────────────────────────────────────────
        progress = features.get("progress_ratio", 0.5)
        if progress >= 0.75:
            insights.append({
                "type":       "progress",
                "category":   "consistency",
                "message":    f"You moved forward on {progress:.0%} of tracked days. At this frequency, behavioral patterns begin to consolidate into identity-level change.",
                "confidence": 0.75,
                "action_hint": None,
            })
        elif progress < 0.35:
            insights.append({
                "type":       "progress",
                "category":   "consistency",
                "message":    f"Forward progress recorded on only {progress:.0%} of tracked days. This level suggests your current system needs adjustment.",
                "confidence": 0.75,
                "action_hint": "Reduce your daily intention to one non-negotiable behavior.",
            })

        # ── Sort and cap ───────────────────────────────────────────────────
        insights.sort(key=lambda x: x.get("confidence", 0.5), reverse=True)
        return insights[:8]
