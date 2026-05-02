"""
InterventionEngine — Breaks psychological loops with specific CBT/ACT techniques.

CORE PRINCIPLE: Insight alone does not produce change.
The system must prescribe a specific, immediately actionable micro-intervention
that interrupts the detected loop before it reinforces further.

Technique library (CBT + ACT):
  Cognitive Defusion      — "I am having the thought that..."
  Behavioral Activation   — 2-minute version of avoided task
  Grounding               — 5-4-3-2-1 sensory anchor
  Energy Recovery         — structured rest prescription
  Identity Reconnection   — values clarification prompt
  Decatastrophizing       — realistic scenario exercise
  Thought Defusion Timer  — timed thought observation without engagement
  Social Boundary Setting — reduce negative social input deliberately

Intervention design rules:
  ✅ Max 2 sentences of explanation
  ✅ One specific, concrete action
  ✅ Optional timer for timed techniques
  ✅ Follow-up question after action (reinforces the neural pathway change)
  ❌ No therapy language ("Let's explore...", "How does that make you feel?")
  ❌ No moralizing ("You should...")
  ❌ No vague encouragement ("Just try your best")
"""
from typing import List, Optional, Dict, Any
from app.services.cognitive_training_system.schemas import Intervention, DetectedLoop


# ── Intervention Library ──────────────────────────────────────────────────────

_INTERVENTIONS: Dict[str, Dict[str, Any]] = {

    "negative_thought_loop": {
        "technique":    "Cognitive Defusion (ACT)",
        "action":       "thought_defusion",
        "prompt":       "Say out loud or write: 'I notice I am having the thought that [your thought].' "
                        "This creates distance between you and the narrative.",
        "duration_sec": None,
        "has_timer":    False,
        "follow_up":    "Did the thought feel less urgent after naming it this way?",
    },

    "avoidance_loop": {
        "technique":    "Behavioral Activation (CBT)",
        "action":       "micro_action",
        "prompt":       "Do exactly 2 minutes of the avoided task — not to finish it, but to break the avoidance response. Start now.",
        "duration_sec": 120,
        "has_timer":    True,
        "follow_up":    "What happened to your resistance level once you started?",
    },

    "energy_depletion_loop": {
        "technique":    "Structured Recovery Protocol",
        "action":       "energy_recovery",
        "prompt":       "Schedule one deliberate rest block today: 20 minutes with no input "
                        "(no phone, no media). Depletion does not resolve without deliberate recovery.",
        "duration_sec": 1200,
        "has_timer":    True,
        "follow_up":    "Rate your energy after the rest block (1–10).",
    },

    "identity_erosion_loop": {
        "technique":    "Values Reconnection (ACT)",
        "action":       "identity_reconnect",
        "prompt":       "Identify one small action — 5 minutes or less — that the person you intend to be would do right now. Execute it before doing anything else.",
        "duration_sec": None,
        "has_timer":    False,
        "follow_up":    "Did completing that action shift your self-respect rating even slightly?",
    },

    "rumination_loop": {
        "technique":    "Timed Thought Observation",
        "action":       "thought_timer",
        "prompt":       "Set a 5-minute timer. Allow the thought to exist without trying to fix or suppress it. When the timer ends, redirect to one concrete task.",
        "duration_sec": 300,
        "has_timer":    True,
        "follow_up":    "Did the thought intensity change during or after the 5 minutes?",
    },

    "catastrophizing_loop": {
        "technique":    "Decatastrophizing (CBT)",
        "action":       "realistic_scenario",
        "prompt":       "Write the realistic outcome (not the worst case): "
                        "What would most likely happen if things went moderately badly? "
                        "Then write one action you could take in that scenario.",
        "duration_sec": None,
        "has_timer":    False,
        "follow_up":    "On a scale of 0–100, how catastrophic does the situation feel now?",
    },

    "validation_seeking_loop": {
        "technique":    "Internal Standards Audit",
        "action":       "validation_audit",
        "prompt":       "Write one standard you hold for yourself that does not require anyone else's opinion to validate. "
                        "Did you meet it today?",
        "duration_sec": None,
        "has_timer":    False,
        "follow_up":    "What would it mean for your day if external reactions had not occurred?",
    },
}

# Fallback intervention for unknown loop types
_FALLBACK_INTERVENTION = {
    "technique":    "Pattern Interruption",
    "action":       "pattern_break",
    "prompt":       "Identify the specific moment this pattern activates. "
                    "What is the smallest action you can take to disrupt it at that point?",
    "duration_sec": None,
    "has_timer":    False,
    "follow_up":    "What triggered the pattern today?",
}


class InterventionEngine:
    """
    Stateless intervention prescriber.
    Maps detected loops to CBT/ACT-grounded micro-interventions.
    """

    @staticmethod
    def prescribe(loops: List[DetectedLoop]) -> List[Intervention]:
        """
        Generate one intervention per detected loop.
        Max 3 interventions returned — cognitive load protection.
        """
        interventions: List[Intervention] = []

        for loop in loops[:3]:   # max 3 at once
            config = _INTERVENTIONS.get(loop.type, _FALLBACK_INTERVENTION)

            interventions.append(Intervention(
                loop_type=loop.type,
                technique=config["technique"],
                action=config["action"],
                prompt=config["prompt"],
                duration_sec=config.get("duration_sec"),
                has_timer=config.get("has_timer", False),
                follow_up=config.get("follow_up"),
            ))

        return interventions

    @staticmethod
    def get_for_loop(loop_type: str) -> Optional[Intervention]:
        """
        Get a single intervention for a specific loop type.
        Used for real-time intervention trigger (immediate display after loop detection).
        """
        config = _INTERVENTIONS.get(loop_type)
        if not config:
            return None

        return Intervention(
            loop_type=loop_type,
            technique=config["technique"],
            action=config["action"],
            prompt=config["prompt"],
            duration_sec=config.get("duration_sec"),
            has_timer=config.get("has_timer", False),
            follow_up=config.get("follow_up"),
        )

    @staticmethod
    def get_available_techniques() -> List[Dict[str, str]]:
        """Returns all available intervention techniques for the technique library view."""
        return [
            {"loop_type": loop_type, "technique": config["technique"], "action": config["action"]}
            for loop_type, config in _INTERVENTIONS.items()
        ]
