"""
SkillTracker + ProgressionEngine — Cognitive skill growth system.

NOT gamified levels. Skill maturity levels.

Levels:
  1 — Awareness      (overall < 0.30)
  2 — Understanding  (0.30–0.50)
  3 — Control        (0.50–0.70)
  4 — Discipline     (0.70–0.85)
  5 — Self-Mastery   (0.85+)

Skill update rules:
  Each skill grows based on EVIDENCE from today's cognitive log.
  Growth is small and incremental (max +0.05/day per skill).
  Skills decay very slowly if not exercised (−0.005/day).
  Decay is capped to prevent regression below 0.05.

14 skills, their growth signals:
  awareness              ← thought logged
  emotional_labeling     ← dominant_emotion named
  distortion_detection   ← cognitive_distortion identified
  reframing              ← reframe logged + belief_strength decreased
  control_focus          ← in_control + out_of_control both logged
  action_despite_emotion ← habits_completed despite low mood/energy
  avoidance_awareness    ← avoided_task logged
  self_integrity         ← self_respect = "yes" + acted_as_intended
  identity_alignment     ← identity_alignment_score from cognitive log
  progress_recognition   ← win logged + moved_forward = True
  discomfort_tolerance   ← low energy/mood + habit completed
  attention_control      ← deep_work_ratio > 0.60
  validation_independence← social_influence positive > negative
  self_talk_quality      ← thought_type="helpful" or belief_shift > 30%
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.cognitive_skill_state import CognitiveSkillState
from app.services.cognitive_training_system.schemas import (
    LevelUpEvent, CognitiveSkillOut
)
from app.services.cognitive_training_system.protocol_engine import ProtocolEngine, LEVEL_PROTOCOLS


# ── Growth/Decay Constants ─────────────────────────────────────────────────────
MAX_GROWTH  = 0.05    # max skill gain per day per skill
DECAY_RATE  = 0.005   # daily decay when skill not exercised
DECAY_FLOOR = 0.05    # minimum skill floor (cannot decay below this)


# ── Level Definitions ─────────────────────────────────────────────────────────
LEVELS = {
    1: {"label": "Awareness",    "min": 0.00, "description": "You are beginning to notice thought and behavioral patterns."},
    2: {"label": "Understanding","min": 0.30, "description": "You understand the structure of your psychological patterns."},
    3: {"label": "Control",      "min": 0.50, "description": "You can separate what is in your control from what is not."},
    4: {"label": "Discipline",   "min": 0.70, "description": "Your actions consistently reflect your stated values."},
    5: {"label": "Self-Mastery", "min": 0.85, "description": "You operate with deliberate, evidence-based self-direction."},
}


class SkillTracker:
    """Updates CognitiveSkillState based on today's CognitiveDayLog."""

    @staticmethod
    def update(
        skill_state: CognitiveSkillState,
        log: Any,
    ) -> Dict[str, float]:
        """
        Compute skill deltas and apply them to the skill_state object.
        Returns dict of {skill_name: delta} for reporting to user.
        """
        deltas: Dict[str, float] = {}

        # ── Compute raw growth signals from log ───────────────────────────
        signals = SkillTracker._extract_signals(log)

        # ── Apply each skill update ───────────────────────────────────────
        all_skills = skill_state.skill_dict()
        for skill_name in all_skills.keys():
            growth    = signals.get(skill_name, 0.0)
            current   = getattr(skill_state, skill_name, 0.0) or 0.0

            # Diminishing returns: harder to grow near 1.0
            effective_growth = growth * (1.0 - current * 0.7)
            new_val = min(current + effective_growth, 1.0)

            # Apply decay if not exercised today
            if growth == 0.0 and current > DECAY_FLOOR:
                new_val = max(current - DECAY_RATE, DECAY_FLOOR)
                delta   = new_val - current
            else:
                delta   = new_val - current

            setattr(skill_state, skill_name, round(new_val, 4))

            if abs(delta) > 0.001:
                deltas[skill_name] = round(delta, 4)

        # ── Update overall score ──────────────────────────────────────────
        updated_skills = skill_state.skill_dict()
        skill_state.overall_score = round(sum(updated_skills.values()) / len(updated_skills), 4)
        skill_state.updated_at    = datetime.utcnow()

        return deltas

    @staticmethod
    def _extract_signals(log: Any) -> Dict[str, float]:
        """
        Map log fields to skill growth signals.
        Each signal = 0.0–MAX_GROWTH float.
        """
        s: Dict[str, float] = {}
        G = MAX_GROWTH  # shorthand

        # awareness — thought logged
        s["awareness"] = G if log.thought else 0.0

        # emotional_labeling — dominant emotion named
        s["emotional_labeling"] = G if log.dominant_emotion else 0.0

        # distortion_detection — distortion identified
        s["distortion_detection"] = G if log.cognitive_distortion else 0.0

        # reframing — reframe logged AND belief shifted down
        reframe_success = False
        if log.reframe and log.belief_strength_before and log.belief_strength_after:
            reframe_success = log.belief_strength_after < log.belief_strength_before
        s["reframing"] = G if reframe_success else (G * 0.4 if log.reframe else 0.0)

        # control_focus — both in/out of control lists logged
        has_in  = isinstance(log.in_control,       list) and len(log.in_control) > 0
        has_out = isinstance(log.out_of_control,   list) and len(log.out_of_control) > 0
        s["control_focus"] = G if (has_in and has_out) else (G * 0.5 if (has_in or has_out) else 0.0)

        # action_despite_emotion — habits completed despite low mood or energy
        low_state   = (log.mood and log.mood <= 4) or (log.energy == "low")
        did_habits  = (log.habits_completed or 0) > 0
        s["action_despite_emotion"] = G if (low_state and did_habits) else 0.0

        # avoidance_awareness — avoided task named
        s["avoidance_awareness"] = G if log.avoided_task else 0.0

        # self_integrity — self_respect=yes AND acted_as_intended
        full_integrity = log.self_respect == "yes" and log.acted_as_intended is True
        part_integrity = log.self_respect in ("yes", "partial")
        s["self_integrity"] = G if full_integrity else (G * 0.4 if part_integrity else 0.0)

        # identity_alignment — from computed score
        ias = log.identity_alignment_score or 0.0
        s["identity_alignment"] = round(G * ias, 5)

        # progress_recognition — win logged + moved_forward
        s["progress_recognition"] = G if (log.win and log.moved_forward) else (G * 0.3 if log.win else 0.0)

        # discomfort_tolerance — low energy/mood but completed habits
        s["discomfort_tolerance"] = G if (low_state and did_habits) else 0.0

        # attention_control — deep work ratio > 60%
        deep  = log.deep_work_minutes   or 0
        dist  = log.distraction_minutes or 0
        total = deep + dist
        focus_ratio = (deep / total) if total > 0 else 0.0
        s["attention_control"] = G if focus_ratio >= 0.60 else (G * focus_ratio if total > 0 else 0.0)

        # validation_independence — more positive than negative social
        if isinstance(log.social_influence, dict):
            pos = len(log.social_influence.get("positive", []))
            neg = len(log.social_influence.get("negative", []))
            s["validation_independence"] = G if pos > neg else 0.0
        else:
            s["validation_independence"] = 0.0

        # self_talk_quality — helpful thought OR strong belief shift
        helpful_thought = log.thought_type == "helpful"
        strong_shift = False
        if log.belief_strength_before and log.belief_strength_after and log.belief_strength_before > 0:
            strong_shift = (log.belief_strength_before - log.belief_strength_after) / log.belief_strength_before > 0.30
        s["self_talk_quality"] = G if (helpful_thought or strong_shift) else 0.0

        return s


class ProgressionEngine:
    """
    Maps overall_score to cognitive level.
    Detects level-up events and returns the LevelUpEvent payload.
    """

    @staticmethod
    def compute_level(overall_score: float) -> int:
        """Map overall score (mean of all 14 skills) to a level 1–5."""
        if overall_score >= 0.85: return 5
        if overall_score >= 0.70: return 4
        if overall_score >= 0.50: return 3
        if overall_score >= 0.30: return 2
        return 1

    @staticmethod
    def update_level(
        skill_state: CognitiveSkillState,
    ) -> Optional[LevelUpEvent]:
        """
        Recompute the user's cognitive level.
        If it increased, return a LevelUpEvent. Otherwise return None.
        """
        previous_level = skill_state.cognitive_level or 1
        new_level      = ProgressionEngine.compute_level(skill_state.overall_score)

        skill_state.cognitive_level = new_level

        if new_level > previous_level:
            level_info  = LEVELS.get(new_level, LEVELS[1])
            unlocked    = ProtocolEngine.get_unlocked_steps(new_level)

            return LevelUpEvent(
                previous_level=previous_level,
                new_level=new_level,
                level_label=level_info["label"],
                message=level_info["description"],
                unlocked_steps=unlocked,
            )

        return None

    @staticmethod
    def get_or_create(user_id: str, db: Session) -> CognitiveSkillState:
        """Fetch skill state or create blank record for new user."""
        state = db.query(CognitiveSkillState).filter(
            CognitiveSkillState.user_id == str(user_id)
        ).first()
        if not state:
            state = CognitiveSkillState(user_id=str(user_id))
            db.add(state)
            db.flush()
        return state
