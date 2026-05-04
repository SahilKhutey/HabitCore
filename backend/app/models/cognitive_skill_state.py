"""
CognitiveSkillState — Tracks 14 mental skill scores per user.

This is the progression backbone of the CBTS.
Skills grow from daily cognitive log data — not from completing tasks.

Each skill: 0.0 (untrained) → 1.0 (mastered)
Progression level: 1 (Awareness) → 5 (Self-Mastery)

Skill taxonomy is CBT + ACT aligned:
  awareness, emotional_labeling, distortion_detection — foundational
  reframing, control_focus, action_despite_emotion     — executive
  avoidance_awareness, self_integrity, identity_alignment — identity
  progress_recognition, discomfort_tolerance           — resilience
  attention_control, validation_independence            — autonomy
  self_talk_quality                                     — metacognition
"""
from sqlalchemy import Column, String, Float, Integer, DateTime
from app.db.declarative import Base
from datetime import datetime, timezone
import uuid


class CognitiveSkillState(Base):
    __tablename__ = "cognitive_skill_state"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, unique=True, index=True, nullable=False)

    # ── Foundational Skills (Level 1 targets) ────────────────────────────
    awareness              = Column(Float, default=0.0)   # noticing thoughts without reacting
    emotional_labeling     = Column(Float, default=0.0)   # naming emotions precisely
    distortion_detection   = Column(Float, default=0.0)   # identifying cognitive distortions

    # ── Executive Skills (Level 2–3 targets) ─────────────────────────────
    reframing              = Column(Float, default=0.0)   # actively restructuring thoughts
    control_focus          = Column(Float, default=0.0)   # separating controllable vs not
    action_despite_emotion = Column(Float, default=0.0)   # acting against avoidance impulse

    # ── Identity Skills (Level 3–4 targets) ──────────────────────────────
    avoidance_awareness    = Column(Float, default=0.0)   # noticing avoidance patterns
    self_integrity         = Column(Float, default=0.0)   # actions aligned to stated values
    identity_alignment     = Column(Float, default=0.0)   # overall self-concept coherence

    # ── Resilience Skills (Level 4 targets) ──────────────────────────────
    progress_recognition   = Column(Float, default=0.0)   # recognizing non-linear growth
    discomfort_tolerance   = Column(Float, default=0.0)   # sitting with discomfort productively

    # ── Autonomy Skills (Level 5 targets) ────────────────────────────────
    attention_control      = Column(Float, default=0.0)   # directing focus deliberately
    validation_independence = Column(Float, default=0.0)  # internal vs external motivation
    self_talk_quality      = Column(Float, default=0.0)   # quality of internal voice

    # ── Computed ─────────────────────────────────────────────────────────
    cognitive_level        = Column(Integer, default=1)   # 1–5 (ProgressionEngine output)
    overall_score          = Column(Float, default=0.0)   # mean of all skills

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def skill_dict(self) -> dict:
        """Return all 14 skills as a flat dict for computation."""
        return {
            "awareness":               self.awareness or 0.0,
            "emotional_labeling":      self.emotional_labeling or 0.0,
            "distortion_detection":    self.distortion_detection or 0.0,
            "reframing":               self.reframing or 0.0,
            "control_focus":           self.control_focus or 0.0,
            "action_despite_emotion":  self.action_despite_emotion or 0.0,
            "avoidance_awareness":     self.avoidance_awareness or 0.0,
            "self_integrity":          self.self_integrity or 0.0,
            "identity_alignment":      self.identity_alignment or 0.0,
            "progress_recognition":    self.progress_recognition or 0.0,
            "discomfort_tolerance":    self.discomfort_tolerance or 0.0,
            "attention_control":       self.attention_control or 0.0,
            "validation_independence": self.validation_independence or 0.0,
            "self_talk_quality":       self.self_talk_quality or 0.0,
        }
