"""
FeatureBuilder — extracts numerical features from CognitiveDayLog history.

This is the feature engineering layer — the bridge between raw logs
and the pattern detection engines (InsightBuilder, BurnoutDetector).

All features are normalized to a comparable scale.
Missing data is handled gracefully (partial logs are valid).

Output feeds:
  BurnoutDetector   — burnout risk computation
  InsightBuilder    — cognitive insight generation
  DriverMapper      — energy pattern extraction
  AICoachService    — DailyCognitiveSummary context injection
"""
from typing import List, Dict, Any, Optional
from statistics import mean, stdev
import re


ENERGY_NUMERIC = {"low": 1, "medium": 2, "high": 3}


class FeatureBuilder:
    """
    Stateless feature extractor for CognitiveDayLog records.
    Requires a list of CognitiveDayLog ORM objects.
    """

    @staticmethod
    def build(logs: List[Any]) -> Dict[str, Any]:
        """
        Build the full feature dict from a list of CognitiveDayLog records.
        Partial logs (missing evening fields) are handled with safe defaults.
        """
        if not logs:
            return FeatureBuilder._empty_features()

        n = len(logs)

        # ── Mood features ─────────────────────────────────────────────────
        moods = [l.mood for l in logs if l.mood is not None]
        evening_moods = [l.evening_mood for l in logs if l.evening_mood is not None]

        avg_mood = mean(moods) if moods else 5.0
        mood_trend = FeatureBuilder._trend(moods) if len(moods) >= 3 else "stable"
        mood_volatility = stdev(moods) if len(moods) >= 2 else 0.0

        # ── Energy features ───────────────────────────────────────────────
        energies = [ENERGY_NUMERIC.get(l.energy, 2) for l in logs if l.energy]
        avg_energy_num = mean(energies) if energies else 2.0
        avg_energy = FeatureBuilder._energy_label(avg_energy_num)

        # ── Stress features ───────────────────────────────────────────────
        stresses = [l.stress for l in logs if l.stress is not None]
        avg_stress = mean(stresses) if stresses else 3.0
        stress_trend = FeatureBuilder._trend(stresses) if len(stresses) >= 3 else "stable"

        # ── Thought / Distortion features ────────────────────────────────
        thoughts = [l for l in logs if l.thought]
        harmful_thoughts = [l for l in thoughts if l.thought_type == "harmful"]
        negative_thought_ratio = len(harmful_thoughts) / max(1, len(thoughts))

        distortions_present = [
            l.cognitive_distortion for l in logs
            if l.cognitive_distortion
        ]

        # Belief shift: average reduction in belief strength after reframing
        shifts = []
        for l in logs:
            if l.belief_strength_before and l.belief_strength_after:
                before = l.belief_strength_before
                shift = (before - l.belief_strength_after) / max(1, before)
                shifts.append(shift)
        avg_belief_shift = mean(shifts) if shifts else 0.0

        # ── Behavior features ─────────────────────────────────────────────
        completed = [l.habits_completed or 0 for l in logs]
        skipped   = [l.habits_skipped   or 0 for l in logs]
        total_attempted = sum(completed) + sum(skipped)
        avoidance_rate = sum(skipped) / max(1, total_attempted)

        deep_work  = [l.deep_work_minutes    or 0 for l in logs]
        distracted = [l.distraction_minutes  or 0 for l in logs]
        total_work = sum(deep_work) + sum(distracted)
        deep_work_ratio = sum(deep_work) / max(1, total_work)

        # ── Driver features ───────────────────────────────────────────────
        all_drainers: List[str] = []
        all_givers:   List[str] = []
        for l in logs:
            if isinstance(l.energy_drainers, list):
                all_drainers.extend(l.energy_drainers)
            if isinstance(l.energy_givers, list):
                all_givers.extend(l.energy_givers)

        # ── Identity features ─────────────────────────────────────────────
        respect_map = {"yes": 1.0, "partial": 0.5, "no": 0.0}
        respect_scores = [
            respect_map.get(l.self_respect, 0.5)
            for l in logs if l.self_respect
        ]
        self_respect_score = mean(respect_scores) if respect_scores else 0.5

        alignment_scores = [
            l.identity_alignment_score
            for l in logs if l.identity_alignment_score is not None
        ]
        avg_alignment = mean(alignment_scores) if alignment_scores else 0.5

        # ── Progress features ─────────────────────────────────────────────
        forward_days = sum(1 for l in logs if l.moved_forward)
        progress_ratio = forward_days / n

        # ── Anxiety / cognitive load ──────────────────────────────────────
        anxiety_days = sum(1 for l in logs if l.anxiety_dump)
        cognitive_load_scores = [
            l.cognitive_load_score
            for l in logs if l.cognitive_load_score is not None
        ]
        avg_cognitive_load = mean(cognitive_load_scores) if cognitive_load_scores else 0.5

        return {
            # Mood
            "avg_mood":               round(avg_mood, 2),
            "mood_trend":             mood_trend,
            "mood_volatility":        round(mood_volatility, 3),

            # Energy
            "avg_energy":             avg_energy,
            "avg_energy_num":         round(avg_energy_num, 2),

            # Stress
            "avg_stress":             round(avg_stress, 2),
            "stress_trend":           stress_trend,

            # Thought
            "negative_thought_ratio": round(negative_thought_ratio, 3),
            "distortions_detected":   list(set(distortions_present)),
            "distortion_frequency":   len(distortions_present) / n,
            "avg_belief_shift":       round(avg_belief_shift, 3),
            "reframing_active":       avg_belief_shift > 0.1,

            # Behavior
            "avoidance_rate":         round(avoidance_rate, 3),
            "deep_work_ratio":        round(deep_work_ratio, 3),

            # Drivers
            "top_drainers":           FeatureBuilder._top_n(all_drainers, 3),
            "top_givers":             FeatureBuilder._top_n(all_givers, 3),

            # Identity
            "self_respect_score":     round(self_respect_score, 3),
            "avg_identity_alignment": round(avg_alignment, 3),

            # Progress
            "progress_ratio":         round(progress_ratio, 3),

            # Cognitive load
            "avg_cognitive_load":     round(avg_cognitive_load, 3),
            "anxiety_rate":           round(anxiety_days / n, 3),

            # Metadata
            "sample_size":            n,
        }

    @staticmethod
    def _trend(values: List[float]) -> str:
        """Simple linear trend: compare last third vs. first third."""
        n = len(values)
        if n < 3:
            return "stable"
        third = max(1, n // 3)
        early  = mean(values[:third])
        recent = mean(values[-third:])
        delta  = recent - early
        if delta > 0.5:   return "increasing"
        if delta < -0.5:  return "decreasing"
        return "stable"

    @staticmethod
    def _energy_label(numeric: float) -> str:
        if numeric >= 2.5: return "high"
        if numeric >= 1.5: return "medium"
        return "low"

    @staticmethod
    def _top_n(items: List[str], n: int) -> List[str]:
        """Return top-N most frequent items from a flat list."""
        if not items:
            return []
        freq: Dict[str, int] = {}
        for item in items:
            freq[item.lower().strip()] = freq.get(item.lower().strip(), 0) + 1
        return [k for k, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]]

    @staticmethod
    def _empty_features() -> Dict[str, Any]:
        return {
            "avg_mood": 5.0, "mood_trend": "stable", "mood_volatility": 0.0,
            "avg_energy": "medium", "avg_energy_num": 2.0,
            "avg_stress": 3.0, "stress_trend": "stable",
            "negative_thought_ratio": 0.0, "distortions_detected": [],
            "distortion_frequency": 0.0, "avg_belief_shift": 0.0, "reframing_active": False,
            "avoidance_rate": 0.0, "deep_work_ratio": 0.5,
            "top_drainers": [], "top_givers": [],
            "self_respect_score": 0.5, "avg_identity_alignment": 0.5,
            "progress_ratio": 0.5, "avg_cognitive_load": 0.5, "anxiety_rate": 0.0,
            "sample_size": 0,
        }
