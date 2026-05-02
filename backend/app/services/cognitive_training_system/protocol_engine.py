"""
ProtocolEngine — Adaptive UX Brain.

Decides WHAT the user sees, HOW MUCH, and WHEN complexity evolves.

Core principle: Cognitive load management.
A beginner seeing a 9-step reflection form will quit.
An expert seeing only mood + thought will feel under-challenged.

Protocol evolution is skill-gated, not time-gated.
The user earns access to deeper reflection by demonstrating skill growth.

Level → Step set:
  1 (Awareness)    — 4 steps: mood, thought, win, tomorrow
  2 (Understanding)— 6 steps: + distortion, reframe
  3 (Control)      — 8 steps: + avoidance, control_filter
  4 (Discipline)   — 9 steps: + identity_alignment, attention_tracking
  5 (Self-Mastery) — full 11-step protocol

All step keys correspond to EveningCheckinRequest fields.
"""
from typing import List, Dict, Any
from app.services.cognitive_training_system.schemas import DailyProtocol


# ── Step definitions ──────────────────────────────────────────────────────────

ALL_STEPS = [
    "mood",               # mood rating 1–10
    "thought",            # one thought observed today
    "win",                # one thing that went well
    "tomorrow_priority",  # single focus for tomorrow
    "distortion",         # detected or self-identified distortion
    "reframe",            # reframe attempt
    "avoidance",          # what was avoided + why
    "control_filter",     # in_control vs out_of_control split
    "identity_alignment", # acted-as-intended + self-respect
    "attention_tracking", # deep work vs distraction minutes
    "self_integrity",     # anxiety dump + improvement
    "energy_drivers",     # drainers + givers
    "social_influence",   # positive / negative social patterns
]

LEVEL_PROTOCOLS: Dict[int, Dict[str, Any]] = {
    1: {
        "label":       "Awareness",
        "steps":       ["mood", "thought", "win", "tomorrow_priority"],
        "description": "Begin by noticing. Four inputs — no pressure.",
    },
    2: {
        "label":       "Understanding",
        "steps":       ["mood", "thought", "distortion", "reframe", "win", "tomorrow_priority"],
        "description": "You are learning to observe and question thoughts.",
    },
    3: {
        "label":       "Control",
        "steps":       ["mood", "thought", "distortion", "reframe",
                        "avoidance", "control_filter", "win", "tomorrow_priority"],
        "description": "Now you separate what is in your control from what is not.",
    },
    4: {
        "label":       "Discipline",
        "steps":       ["mood", "thought", "distortion", "reframe",
                        "avoidance", "control_filter", "identity_alignment",
                        "attention_tracking", "win", "tomorrow_priority"],
        "description": "You are aligning actions with identity and tracking focus quality.",
    },
    5: {
        "label":       "Self-Mastery",
        "steps":       ALL_STEPS,
        "description": "Full cognitive protocol. You operate with deliberate awareness.",
    },
}

# Steps that unlock when leveling up (for LevelUpEvent.unlocked_steps)
UNLOCKED_AT_LEVEL = {
    2: ["distortion", "reframe"],
    3: ["avoidance", "control_filter"],
    4: ["identity_alignment", "attention_tracking"],
    5: ["self_integrity", "energy_drivers", "social_influence"],
}


class ProtocolEngine:
    """
    Stateless protocol adapter. Returns DailyProtocol based on user's cognitive level.
    Also applied to morning check-in to determine how many inputs to request.
    """

    @staticmethod
    def get_daily_protocol(cognitive_level: int) -> DailyProtocol:
        """
        Returns tonight's check-in protocol for the given cognitive level.
        Level is clamped to 1–5.
        """
        level  = max(1, min(cognitive_level, 5))
        config = LEVEL_PROTOCOLS[level]

        return DailyProtocol(
            level=level,
            level_label=config["label"],
            steps=config["steps"],
            max_steps=len(ALL_STEPS),
            description=config["description"],
        )

    @staticmethod
    def get_morning_fields(cognitive_level: int) -> List[str]:
        """
        Returns which morning fields to request based on level.
        Level 1–2: mood + energy only (2 fields)
        Level 3+:  mood + energy + dominant_emotion + intent (4 fields)
        """
        if cognitive_level <= 2:
            return ["mood", "energy"]
        return ["mood", "energy", "dominant_emotion", "morning_intent"]

    @staticmethod
    def should_show_step(step: str, cognitive_level: int) -> bool:
        """Check if a given step is available at the user's current level."""
        protocol = ProtocolEngine.get_daily_protocol(cognitive_level)
        return step in protocol.steps

    @staticmethod
    def get_unlocked_steps(new_level: int) -> List[str]:
        """Returns steps newly unlocked when reaching new_level."""
        return UNLOCKED_AT_LEVEL.get(new_level, [])
