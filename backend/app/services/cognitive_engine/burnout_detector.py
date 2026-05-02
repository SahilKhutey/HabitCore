"""
BurnoutDetector — multi-signal cognitive burnout detection.

v2: Burnout is not just habit failure. It is a cognitive-behavioral state.
Detection uses BOTH behavioral signals (HabitEngine) AND
cognitive signals (CognitiveDayLog) for higher precision.

Outputs:
  BurnoutAssessment dataclass with:
    detected: bool
    confidence: float
    severity: "low_risk" | "moderate" | "high" | "critical"
    signals: list of what triggered it
    recommended_action: string (v2 language)

Used by:
  StateEngine  → set UserMode.BURNOUT or RECOVERY
  InsightBuilder → generate burnout insights
  AICoachService → calibrate tone
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class BurnoutAssessment:
    detected:            bool
    confidence:          float
    severity:            str    # "none" | "low_risk" | "moderate" | "high" | "critical"
    signals:             List[str]
    recommended_action:  str
    behavioral_score:    float  # 0.0–1.0 from habit data
    cognitive_score:     float  # 0.0–1.0 from cognitive logs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected":           self.detected,
            "confidence":         round(self.confidence, 3),
            "severity":           self.severity,
            "signals":            self.signals,
            "recommended_action": self.recommended_action,
            "behavioral_score":   round(self.behavioral_score, 3),
            "cognitive_score":    round(self.cognitive_score, 3),
        }


class BurnoutDetector:
    """
    Stateless burnout detector.
    Combines behavioral features (from BehavioralInsightEngine) with
    cognitive features (from FeatureBuilder) for a dual-signal assessment.
    """

    # Thresholds
    BURNOUT_THRESHOLD  = 0.60
    CRITICAL_THRESHOLD = 0.80
    MODERATE_THRESHOLD = 0.45

    @staticmethod
    def assess(
        cognitive_features: Dict[str, Any],
        behavioral_burnout_score: float = 0.0,
    ) -> BurnoutAssessment:
        """
        Compute burnout assessment from combined signals.

        Args:
            cognitive_features:       Output of FeatureBuilder.build()
            behavioral_burnout_score: PsychologicalEngine.calculate_burnout_score()
        """
        signals: List[str] = []
        cognitive_score = 0.0

        # ── Cognitive signals (from CognitiveDayLog) ──────────────────────

        # Low energy trend
        if cognitive_features.get("avg_energy") == "low":
            cognitive_score += 0.30
            signals.append("Sustained low energy across tracked days.")

        # High stress trend
        avg_stress = cognitive_features.get("avg_stress", 3.0)
        stress_trend = cognitive_features.get("stress_trend", "stable")
        if avg_stress >= 7 and stress_trend == "increasing":
            cognitive_score += 0.25
            signals.append("Stress trend is increasing with elevated baseline.")
        elif avg_stress >= 7:
            cognitive_score += 0.15
            signals.append("Elevated stress levels detected.")

        # Low self-respect score (identity misalignment)
        self_respect = cognitive_features.get("self_respect_score", 0.5)
        if self_respect < 0.40:
            cognitive_score += 0.20
            signals.append("Self-respect score below threshold — actions not aligning with values.")
        elif self_respect < 0.55:
            cognitive_score += 0.10
            signals.append("Partial identity alignment detected.")

        # Negative thought ratio
        neg_ratio = cognitive_features.get("negative_thought_ratio", 0.0)
        if neg_ratio > 0.65:
            cognitive_score += 0.15
            signals.append(f"High negative thought ratio ({neg_ratio:.0%}) in recorded logs.")
        elif neg_ratio > 0.45:
            cognitive_score += 0.08

        # Low progress ratio
        progress = cognitive_features.get("progress_ratio", 0.5)
        if progress < 0.30:
            cognitive_score += 0.10
            signals.append("Fewer than 30% of days logged as 'moved forward'.")

        # High avoidance
        avoidance = cognitive_features.get("avoidance_rate", 0.0)
        if avoidance > 0.55:
            cognitive_score += 0.10
            signals.append(f"High avoidance rate ({avoidance:.0%}) — consistent task-skipping pattern.")

        # High anxiety dump rate
        anxiety_rate = cognitive_features.get("anxiety_rate", 0.0)
        if anxiety_rate > 0.60:
            cognitive_score += 0.10
            signals.append("Anxiety dumps present on majority of logged days.")

        # Catastrophizing distortions
        distortions = cognitive_features.get("distortions_detected", [])
        if "catastrophizing" in distortions or "labeling" in distortions:
            cognitive_score += 0.10
            signals.append("Severe cognitive distortions (catastrophizing/labeling) detected in thought logs.")

        # Mood decline
        if cognitive_features.get("mood_trend") == "decreasing":
            cognitive_score += 0.10
            signals.append("Mood trend is declining over the tracked period.")

        cognitive_score = min(cognitive_score, 1.0)

        # ── Combined score (60% behavioral, 40% cognitive) ─────────────────
        # Behavioral signal is more time-dense; cognitive is richer per data point
        combined = (behavioral_burnout_score * 0.60) + (cognitive_score * 0.40)

        # ── Severity classification ────────────────────────────────────────
        detected = combined >= BurnoutDetector.BURNOUT_THRESHOLD

        if combined >= BurnoutDetector.CRITICAL_THRESHOLD:
            severity = "critical"
            action   = (
                "Your cognitive and behavioral signals both indicate severe depletion. "
                "Reduce to one essential habit. Prioritize sleep and one restorative activity."
            )
        elif combined >= BurnoutDetector.BURNOUT_THRESHOLD:
            severity = "high"
            action   = (
                "Multiple burnout indicators are active. "
                "Reduce habit load by 50% for 3 days. Avoid performance pressure."
            )
        elif combined >= BurnoutDetector.MODERATE_THRESHOLD:
            severity = "moderate"
            action   = (
                "Early burnout signals present. Maintain current load "
                "and avoid adding new commitments this week."
            )
        else:
            severity = "none" if combined < 0.25 else "low_risk"
            action   = "No burnout detected. Monitor energy levels if stress trend continues."

        return BurnoutAssessment(
            detected=detected,
            confidence=round(min(combined + 0.10, 0.98), 3),
            severity=severity,
            signals=signals,
            recommended_action=action,
            behavioral_score=round(behavioral_burnout_score, 3),
            cognitive_score=round(cognitive_score, 3),
        )

    @staticmethod
    def quick_check(avg_energy: str, stress_trend: str, self_respect_score: float) -> bool:
        """
        Fast burnout check for real-time use (e.g., after morning check-in).
        Returns True if immediate intervention warranted.
        """
        return (
            avg_energy == "low"
            and stress_trend == "increasing"
            and self_respect_score < 0.40
        )
