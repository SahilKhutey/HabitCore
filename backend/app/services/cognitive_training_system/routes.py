"""
CBTS Routes — Cognitive Training System API.

Endpoints:
  GET  /cognitive-training/context         — Morning context (home screen data)
  POST /cognitive-training/session         — Run full training pipeline after evening log
  GET  /cognitive-training/skills          — User's 14 cognitive skill scores
  GET  /cognitive-training/scores          — Weekly mental scores (clarity/control/integrity/focus)
  GET  /cognitive-training/loops           — Active detected loops
  GET  /cognitive-training/interventions   — Prescribe interventions for active loops
  GET  /cognitive-training/protocol        — Today's adaptive check-in protocol
  GET  /cognitive-training/techniques      — Library of all CBT/ACT techniques
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, auth_required
from app.services.cognitive_training_system.service import CognitiveTrainingService
from app.services.cognitive_training_system.intervention_engine import InterventionEngine
from app.services.cognitive_training_system.loop_detector import LoopDetector
from app.services.cognitive_training_system.scoring_engine import ScoringEngine
from app.services.cognitive_training_system.skill_tracker import ProgressionEngine
from app.services.cognitive_training_system.protocol_engine import ProtocolEngine
from app.services.cognitive_training_system.schemas import CognitiveSkillOut
from app.models.cognitive_day_log import CognitiveDayLog
from app.services.cognitive_engine.feature_builder import FeatureBuilder
from datetime import date, timedelta

router = APIRouter()


@router.get("/context", summary="Morning context: cognitive level, tonight's protocol, energy trend")
def get_morning_context(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Fast home screen data. No heavy analysis.
    Returns cognitive level, tonight's step list, morning fields to show.
    """
    svc = CognitiveTrainingService(db)
    return svc.get_morning_context(str(user.id))


@router.post("/session", summary="Run full CBTS pipeline after evening check-in")
def run_training_session(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Triggers the full 6-step cognitive training pipeline.
    Call this after submitting the evening check-in.
    Returns: scores, loops, interventions, skill_deltas, level_up, links, tomorrow_protocol.
    """
    svc = CognitiveTrainingService(db)
    return svc.run_training_session(str(user.id))


@router.get("/skills", summary="User's 14 cognitive skill scores + level")
def get_skills(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns all 14 cognitive skills with current scores (0.0–1.0)
    and the user's overall cognitive level (1–5).
    """
    svc   = CognitiveTrainingService(db)
    state = svc.get_skill_state(str(user.id))
    return CognitiveSkillOut.from_orm(state)


@router.get("/scores", summary="Weekly mental score aggregation")
def get_weekly_scores(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns Clarity, Control, Integrity, Focus averages + trend (improving/stable/declining)
    over the last N days.
    """
    svc = CognitiveTrainingService(db)
    return svc.get_weekly_scores(str(user.id))


@router.get("/loops", summary="Detected active psychological loops")
def get_loops(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns active harmful psychological loops with confidence, evidence, and days_active.
    Used to show the loop notification card: 'You are in an avoidance loop.'
    """
    cutoff = date.today() - timedelta(days=days)
    logs = db.query(CognitiveDayLog).filter(
        CognitiveDayLog.user_id == str(user.id),
        CognitiveDayLog.log_date >= cutoff,
    ).order_by(CognitiveDayLog.log_date).all()

    loops = LoopDetector.detect(logs, window_days=days)
    return {"loops": [l.dict() for l in loops], "count": len(loops)}


@router.get("/interventions", summary="Prescribe CBT/ACT interventions for active loops")
def get_interventions(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Detects active loops and returns prescribed CBT/ACT micro-interventions.
    Each includes: technique, prompt, timer (if applicable), and follow-up question.
    """
    cutoff = date.today() - timedelta(days=days)
    logs = db.query(CognitiveDayLog).filter(
        CognitiveDayLog.user_id == str(user.id),
        CognitiveDayLog.log_date >= cutoff,
    ).order_by(CognitiveDayLog.log_date).all()

    loops         = LoopDetector.detect(logs, window_days=days)
    interventions = InterventionEngine.prescribe(loops)

    return {
        "loops_detected":  len(loops),
        "interventions":   [i.dict() for i in interventions],
    }


@router.get("/protocol", summary="Today's adaptive cognitive check-in protocol")
def get_protocol(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns the step list for tonight's check-in based on the user's cognitive level.
    Used by frontend to render the correct check-in screens.
    """
    state    = ProgressionEngine.get_or_create(str(user.id), db)
    protocol = ProtocolEngine.get_daily_protocol(state.cognitive_level or 1)
    return protocol.dict()


@router.get("/techniques", summary="Library of all CBT/ACT intervention techniques")
def get_techniques():
    """Returns all available intervention techniques. No auth required (public reference)."""
    return {"techniques": InterventionEngine.get_available_techniques()}
