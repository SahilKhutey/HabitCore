"""
Cognitive Engine Routes — FastAPI endpoints.

UX-aligned API design:
  POST /cognitive/morning        — 30-second morning check-in
  POST /cognitive/evening        — ≤2-minute evening check-in (all steps)
  GET  /cognitive/today          — Today's log (for pre-filling forms)
  GET  /cognitive/insights       — Generated cognitive insights
  GET  /cognitive/summary        — DailyCognitiveSummary (AI context)
  GET  /cognitive/history        — Past logs (last N days)
  GET  /cognitive/burnout        — Current burnout assessment
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, auth_required
from app.services.cognitive_engine.service import CognitiveEngineService
from app.services.cognitive_engine.schemas import (
    MorningCheckinRequest,
    EveningCheckinRequest,
    CognitiveDayLogOut,
    CognitiveInsightOut,
    DailyCognitiveSummary,
)
from app.services.cognitive_engine.burnout_detector import BurnoutDetector
from app.services.cognitive_engine.feature_builder import FeatureBuilder

router = APIRouter()


@router.post("/morning", summary="30-second morning cognitive check-in")
def morning_checkin(
    req: MorningCheckinRequest,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Fast morning entry: mood + energy + optional intent.
    Returns immediate state feedback.
    UX: shown as 3 quick-tap cards, not a form.
    """
    svc = CognitiveEngineService(db)
    return svc.submit_morning(str(user.id), req)


@router.post("/evening", summary="Evening cognitive check-in (5 steps, all optional)")
def evening_checkin(
    req: EveningCheckinRequest,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Evening deep entry. All 5 steps are optional.
    Returns top 3 cognitive insights and burnout assessment.
    UX: each step = separate screen, max 2 minutes total.
    """
    svc = CognitiveEngineService(db)
    return svc.submit_evening(str(user.id), req)


@router.get("/today", summary="Get today's cognitive log for pre-filling forms")
def get_today_log(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    svc = CognitiveEngineService(db)
    log = svc.get_today_log(str(user.id))
    if not log:
        return {"status": "no_log", "morning_completed": False, "evening_completed": False}

    return {
        "id":                   log.id,
        "log_date":             str(log.log_date),
        "morning_completed":    log.morning_completed or False,
        "evening_completed":    log.evening_completed or False,
        "mood":                 log.mood,
        "energy":               log.energy,
        "morning_intent":       log.morning_intent,
        "tomorrow_priority":    log.tomorrow_priority,
        "cognitive_load_score": log.cognitive_load_score,
        "identity_alignment_score": log.identity_alignment_score,
    }


@router.get("/insights", summary="Get cognitive insight feed for current user")
def get_cognitive_insights(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """Returns generated cognitive insights from last N days of data."""
    svc = CognitiveEngineService(db)
    insights = svc.get_insights(str(user.id), days=min(days, 30))
    return {"insights": insights, "count": len(insights)}


@router.get("/summary", summary="Get cognitive summary for AI context enrichment")
def get_cognitive_summary(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns DailyCognitiveSummary — used by AICoachService for context injection.
    Also useful for frontend analytics displays.
    """
    svc = CognitiveEngineService(db)
    summary = svc.get_cognitive_summary(str(user.id), days=min(days, 30))
    return summary


@router.get("/burnout", summary="Get current burnout assessment")
def get_burnout_assessment(
    days: int = 7,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Full burnout assessment combining behavioral + cognitive signals.
    Returns severity, confidence, signals list, and recommended action.
    """
    svc = CognitiveEngineService(db)

    # Get cognitive features
    logs = svc._get_recent_logs(str(user.id), days=days)
    features = FeatureBuilder.build(logs) if logs else FeatureBuilder.build([])

    # Get behavioral burnout
    try:
        from app.services.core.psychological_engine import PsychologicalEngine
        behavioral = PsychologicalEngine(db).calculate_burnout_score(str(user.id))
    except Exception:
        behavioral = 0.0

    assessment = BurnoutDetector.assess(features, behavioral)
    return assessment.to_dict()


@router.get("/history", summary="Get past cognitive logs")
def get_history(
    days: int = 14,
    user=Depends(auth_required),
    db: Session = Depends(get_db),
):
    """Returns last N days of cognitive logs with completion status."""
    svc = CognitiveEngineService(db)
    logs = svc._get_recent_logs(str(user.id), days=min(days, 90))

    return {
        "logs": [
            {
                "id":                       l.id,
                "log_date":                 str(l.log_date),
                "morning_completed":        l.morning_completed or False,
                "evening_completed":        l.evening_completed or False,
                "mood":                     l.mood,
                "energy":                   l.energy,
                "thought_type":             l.thought_type,
                "cognitive_distortion":     l.cognitive_distortion,
                "self_respect":             l.self_respect,
                "moved_forward":            l.moved_forward,
                "identity_alignment_score": l.identity_alignment_score,
                "cognitive_load_score":     l.cognitive_load_score,
            }
            for l in logs
        ],
        "total": len(logs),
    }
