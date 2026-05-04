"""
Reflection Engine V2 API — Serves adaptive questions and updates the learning layer.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.services.reflection_engine.selector import select_adaptive_questions_v2
from app.models.intelligence_models import DailyLog, QuestionUsageLog, QuestionStats, Question
from datetime import date, datetime, timezone
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ResponseSchema(BaseModel):
    question_id: str
    response: str
    response_time: int
    skipped: bool = False

@router.get("/questions", summary="Get V2 adaptive reflection questions")
def get_reflection_questions_v2(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    # 1. Standardized Signals
    log = db.query(DailyLog).filter(
        DailyLog.user_id == str(user.id)
    ).order_by(DailyLog.date.desc()).first()
    
    signals = {
        "avoidance_high": False,
        "low_energy": False,
        "negative_thought": False,
        "burnout_risk": False,
        "high_performance": False
    }
    
    if log:
        signals["avoidance_high"] = log.avoidance_flag == 1
        signals["low_energy"] = (log.self_integrity_score or 5) < 4
        # signals["negative_thought"] = log.thought_label == "negative"
        # signals["burnout_risk"] = log.state == "burnout"
        signals["high_performance"] = (log.execution_score or 0) > 0.8
    
    # 2. Adaptive Selection
    questions = select_adaptive_questions_v2(db, str(user.id), signals)
    
    return [
        {
            "id": q.id,
            "text": q.text,
            "category": q.category,
            "subcategory": q.subcategory,
            "depth_level": q.depth_level,
            "intent": q.intent
        } for q in questions
    ]

from app.services.reflection_engine.answer_intelligence import AnswerIntelligence
from app.models.intelligence_models import DailyLog, QuestionUsageLog, QuestionStats, Question, CognitiveSignal, Event

from streaming.producer import send_user_text_event
from app.services.ai_service import get_ai_service

@router.post("/respond", summary="Log V2 response and stream intelligence")
def log_reflection_response_v2(
    resp: ResponseSchema,
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    # 1. Log Usage
    usage = QuestionUsageLog(
        user_id=str(user.id),
        question_id=resp.question_id,
        date=date.today(),
        response=resp.response,
        response_time_seconds=resp.response_time,
        skipped=resp.skipped
    )
    db.add(usage)
    
    # 2. Asynchronous Intelligence Pipeline (Kafka)
    if not resp.skipped and resp.response:
        # Push to Kafka topic for non-blocking NLP analysis
        send_user_text_event(str(user.id), resp.response)
    
    # 3. Update Global Stats (Learning Layer)
    stats = db.query(QuestionStats).filter(QuestionStats.question_id == resp.question_id).first()
    if not stats:
        stats = QuestionStats(question_id=resp.question_id)
        db.add(stats)
    
    if not resp.skipped:
        stats.times_answered += 1
        if stats.avg_response_time == 0:
            stats.avg_response_time = float(resp.response_time)
        else:
            stats.avg_response_time = (stats.avg_response_time * 0.9) + (resp.response_time * 0.1)
        stats.effectiveness_score = min(stats.times_answered / (stats.times_shown + 1), 1.0)
    else:
        stats.times_skipped += 1
        stats.effectiveness_score *= 0.9
        
    stats.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # 4. Phase 1 Hook: Generate Instant Insight for Day 0
    instant_insight = None
    if user.onboarding_state and not user.onboarding_state.get("instant_insight"):
        # Check if this is truly the first successful reflection
        successful_count = db.query(QuestionUsageLog).filter(
            QuestionUsageLog.user_id == str(user.id),
            QuestionUsageLog.skipped == False
        ).count()
        
        if successful_count == 1: # This current one is the first
            ai = get_ai_service()
            instant_insight = ai.generate_instant_insight(
                str(user.id), 
                user.onboarding_state, 
                resp.response
            )
            # Persist insight to avoid re-generating
            user.onboarding_state["instant_insight"] = instant_insight
            # Mark that we've delivered the Day 0 hook
            user.onboarding_state["hook_delivered_at"] = datetime.now(timezone.utc).isoformat()
            db.commit()

    return {
        "status": "synced", 
        "effectiveness": stats.effectiveness_score,
        "instant_insight": instant_insight
    }
