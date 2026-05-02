"""
LoopDetector — Real-time harmful psychological loop detection.

A loop = a repeated pattern of thought or behavior that sustains dysfunction.
Unlike a single event, loops are cross-day patterns requiring interruption.

This is the system's core differentiator:
  Most apps: observe behavior
  CBTS: detect harmful LOOPS and interrupt them

7 loop types detected:
  negative_thought_loop    — repeated harmful self-narrative
  avoidance_loop           — habitual task-avoidance
  energy_depletion_loop    — chronic low energy with no recovery
  identity_erosion_loop    — consistent self-respect failures
  rumination_loop          — same thought type recurring without reframe
  catastrophizing_loop     — catastrophizing distortions recurring
  validation_seeking_loop  — negative social influence + low self-respect

Loop confidence is evidence-weighted:
  More days active = higher confidence
  Threshold checks = more signals = higher confidence
"""
from typing import List, Dict, Any, Optional
from collections import Counter

from app.services.cognitive_training_system.schemas import DetectedLoop


# ── Thresholds ────────────────────────────────────────────────────────────────

LOOP_THRESHOLDS = {
    "negative_thought_loop":   3,   # harmful thoughts on N+ days in window
    "avoidance_loop":          0.5, # 50% avoidance rate
    "energy_depletion_loop":   3,   # low energy on N+ consecutive days
    "identity_erosion_loop":   2,   # self_respect="no" on N+ days
    "rumination_loop":         2,   # same distortion type on N+ days
    "catastrophizing_loop":    2,   # catastrophizing distortion N+ days
    "validation_seeking_loop": 2,   # negative social influence + low sr
}


class LoopDetector:
    """
    Stateless loop detector. Operates on a window of CognitiveDayLog records.
    Minimum 3 days of data for reliable loop detection.
    """

    @staticmethod
    def detect(logs: List[Any], window_days: int = 7) -> List[DetectedLoop]:
        """
        Run all loop detectors on the given log window.
        Returns a ranked list of active loops (highest confidence first).
        """
        if len(logs) < 2:
            return []

        loops: List[DetectedLoop] = []

        detectors = [
            LoopDetector._negative_thought_loop,
            LoopDetector._avoidance_loop,
            LoopDetector._energy_depletion_loop,
            LoopDetector._identity_erosion_loop,
            LoopDetector._rumination_loop,
            LoopDetector._catastrophizing_loop,
            LoopDetector._validation_seeking_loop,
        ]

        for detector in detectors:
            result = detector(logs)
            if result:
                loops.append(result)

        loops.sort(key=lambda x: x.confidence, reverse=True)
        return loops

    # ── Individual Detectors ──────────────────────────────────────────────────

    @staticmethod
    def _negative_thought_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects repeated harmful self-narrative across days.
        Triggers when 3+ days of harmful thought_type.
        """
        harmful_days = [l for l in logs if l.thought_type == "harmful" and l.thought]
        count = len(harmful_days)
        if count < LOOP_THRESHOLDS["negative_thought_loop"]:
            return None

        # Find common themes
        thoughts = [l.thought for l in harmful_days if l.thought]
        themes = LoopDetector._extract_themes(thoughts)
        evidence = [f"Harmful thought recorded on {count} of {len(logs)} days."]
        if themes:
            evidence.append(f"Recurring themes: {', '.join(themes[:2])}.")

        return DetectedLoop(
            type="negative_thought_loop",
            label="Negative Thought Loop",
            message=f"You are repeating the same negative narrative on {count} of the last {len(logs)} days. This pattern is not a reflection of reality — it is a trained response.",
            confidence=round(min(0.55 + (count - 3) * 0.10, 0.95), 3),
            evidence=evidence,
            days_active=count,
        )

    @staticmethod
    def _avoidance_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects habitual task-avoidance pattern.
        Triggers when skipped habits exceed 50% of total attempted.
        """
        total_completed = sum(l.habits_completed or 0 for l in logs)
        total_skipped   = sum(l.habits_skipped   or 0 for l in logs)
        total = total_completed + total_skipped
        if total == 0:
            return None

        avoidance_rate = total_skipped / total
        if avoidance_rate < LOOP_THRESHOLDS["avoidance_loop"]:
            return None

        avoided_tasks = [l.avoided_task for l in logs if l.avoided_task]
        evidence = [f"Avoidance rate: {avoidance_rate:.0%} over {len(logs)} days."]
        if avoided_tasks:
            common_avoid = Counter(avoided_tasks).most_common(1)
            evidence.append(f"Most avoided: '{common_avoid[0][0]}'.")

        return DetectedLoop(
            type="avoidance_loop",
            label="Avoidance Loop",
            message=f"Avoidance is becoming structural. At {avoidance_rate:.0%}, skipping is no longer occasional — it is the default response.",
            confidence=round(min(0.60 + (avoidance_rate - 0.5) * 0.80, 0.95), 3),
            evidence=evidence,
            days_active=sum(1 for l in logs if (l.habits_skipped or 0) > 0),
        )

    @staticmethod
    def _energy_depletion_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects chronic low-energy pattern with no recovery days.
        Triggers when 3+ consecutive low-energy days detected.
        """
        low_energy_streak = 0
        max_streak = 0
        for log in logs:
            if log.energy == "low":
                low_energy_streak += 1
                max_streak = max(max_streak, low_energy_streak)
            else:
                low_energy_streak = 0

        if max_streak < LOOP_THRESHOLDS["energy_depletion_loop"]:
            return None

        total_low = sum(1 for l in logs if l.energy == "low")
        evidence = [
            f"Low energy on {total_low} of {len(logs)} days.",
            f"Longest consecutive low-energy streak: {max_streak} days.",
        ]

        return DetectedLoop(
            type="energy_depletion_loop",
            label="Energy Depletion Loop",
            message=f"Your energy has been consistently low for {max_streak} consecutive days with no recovery. Sustained depletion directly reduces decision quality and behavioral follow-through.",
            confidence=round(min(0.65 + (max_streak - 3) * 0.08, 0.95), 3),
            evidence=evidence,
            days_active=total_low,
        )

    @staticmethod
    def _identity_erosion_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects consistent self-respect failures.
        Triggers when 'no' self-respect on 2+ days.
        """
        no_respect_days = [l for l in logs if l.self_respect == "no"]
        count = len(no_respect_days)
        if count < LOOP_THRESHOLDS["identity_erosion_loop"]:
            return None

        evidence = [
            f"Self-respect flagged as 'no' on {count} of {len(logs)} days.",
            "Actions are not aligning with stated values.",
        ]

        return DetectedLoop(
            type="identity_erosion_loop",
            label="Identity Erosion Loop",
            message=f"On {count} of the last {len(logs)} days, your actions did not align with who you intend to be. Repeated identity-behavior gaps compound over time.",
            confidence=round(min(0.65 + (count - 2) * 0.10, 0.92), 3),
            evidence=evidence,
            days_active=count,
        )

    @staticmethod
    def _rumination_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects the same distortion type repeating without successful reframe.
        A failed reframe = belief_strength_after >= belief_strength_before.
        """
        distortions = [l.cognitive_distortion for l in logs if l.cognitive_distortion]
        if len(distortions) < LOOP_THRESHOLDS["rumination_loop"]:
            return None

        most_common = Counter(distortions).most_common(1)[0]
        dtype, freq  = most_common

        # Check if reframes are actually working
        reframe_fails = sum(
            1 for l in logs
            if l.cognitive_distortion == dtype
            and l.belief_strength_before is not None
            and l.belief_strength_after is not None
            and l.belief_strength_after >= l.belief_strength_before
        )

        evidence = [
            f"'{dtype.replace('_', ' ').title()}' distortion detected on {freq} of {len(logs)} days.",
        ]
        if reframe_fails > 0:
            evidence.append(f"Reframing has not reduced belief strength on {reframe_fails} occasion(s).")

        return DetectedLoop(
            type="rumination_loop",
            label="Rumination Loop",
            message=f"The '{dtype.replace('_', ' ')}' thought pattern is recurring across {freq} days. Repetition without interruption deepens the neural pathway.",
            confidence=round(min(0.60 + (freq - 2) * 0.10, 0.90), 3),
            evidence=evidence,
            days_active=freq,
        )

    @staticmethod
    def _catastrophizing_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """Specifically flags catastrophizing as a high-severity loop."""
        catastro_days = [
            l for l in logs
            if l.cognitive_distortion == "catastrophizing"
        ]
        count = len(catastro_days)
        if count < LOOP_THRESHOLDS["catastrophizing_loop"]:
            return None

        return DetectedLoop(
            type="catastrophizing_loop",
            label="Catastrophizing Loop",
            message=f"Catastrophizing detected on {count} of {len(logs)} days. This distortion amplifies threat perception and significantly increases anxiety and avoidance.",
            confidence=round(min(0.72 + (count - 2) * 0.08, 0.95), 3),
            evidence=[f"Catastrophizing distortion present on {count} days."],
            days_active=count,
        )

    @staticmethod
    def _validation_seeking_loop(logs: List[Any]) -> Optional[DetectedLoop]:
        """
        Detects dependency on external validation combined with low self-respect.
        Triggers when negative social influence is logged with low self-respect.
        """
        combined_days = 0
        for l in logs:
            has_neg_social = (
                isinstance(l.social_influence, dict)
                and len(l.social_influence.get("negative", [])) > 0
            )
            low_respect = l.self_respect in ("no", "partial")
            if has_neg_social and low_respect:
                combined_days += 1

        if combined_days < LOOP_THRESHOLDS["validation_seeking_loop"]:
            return None

        return DetectedLoop(
            type="validation_seeking_loop",
            label="External Validation Loop",
            message=f"On {combined_days} days, negative social influence coincided with low self-respect. External validation may be substituting for internal standards.",
            confidence=round(min(0.60 + combined_days * 0.08, 0.88), 3),
            evidence=[f"Negative social influence + low self-respect co-occurring on {combined_days} days."],
            days_active=combined_days,
        )

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_themes(thoughts: List[str]) -> List[str]:
        """Extract common words from a list of thoughts to identify themes."""
        STOP_WORDS = {"i", "am", "a", "the", "is", "it", "to", "and", "my",
                      "that", "just", "not", "so", "of", "in", "was", "me"}
        word_freq: Dict[str, int] = {}
        for thought in thoughts:
            for word in thought.lower().split():
                word = word.strip(".,!?")
                if word not in STOP_WORDS and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
        return [w for w, _ in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]]
