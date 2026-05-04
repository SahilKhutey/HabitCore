"""
Intelligence API — Production-grade Behavioral Intelligence Endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.api.deps import get_db, auth_required
from app.services.intelligence_pipeline import IntelligencePipeline
from app.core.intelligence_primitives import EventType, EventCategory
from pydantic import BaseModel

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────────────

class DailyLogInput(BaseModel):
    date: Optional[date] = None
    mood: int
    energy: int
    stress: Optional[int] = None
    dominant_emotion: str
    key_thought: Optional[str] = None
    avoidance_flag: bool = False
    self_integrity_score: float
    wins: List[str] = []
    failures: List[str] = []

class EventInput(BaseModel):
    event_type: EventType
    category: EventCategory
    value: float = 1.0
    metadata: dict = {}

# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/log", summary="Ingest daily behavioral log and trigger pipeline")
def ingest_log(
    log_data: DailyLogInput,
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    pipeline = IntelligencePipeline(db)
    log = pipeline.ingest_daily_log(str(user.id), log_data.dict())
    
    # Trigger full pipeline processing asynchronously via Kafka
    from app.services.core.kafka_service import KafkaService
    KafkaService.send_behavioral_event(
        user_id=str(user.id),
        event_type="daily_log_ingested",
        value=log_data.self_integrity_score,
        metadata={
            "log_id": str(log.id),
            "date": log.date.isoformat(),
            "mood": log_data.mood,
            "energy": log_data.energy,
            "text": f"{log_data.key_thought or ''} {' '.join(log_data.wins)} {' '.join(log_data.failures)}"
        }
    )
    
    return {"status": "success", "log_id": log.id, "date": log.date}

@router.post("/event", summary="Ingest time-series behavioral event")
def ingest_event(
    event_data: EventInput,
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    pipeline = IntelligencePipeline(db)
    event = pipeline.ingest_event(
        str(user.id), 
        event_data.event_type, 
        event_data.category, 
        event_data.value, 
        event_data.metadata
    )
    return {"status": "success", "event_id": event.id}

@router.get("/insights", summary="Fetch high-priority behavioral insights")
def get_insights(
    user=Depends(auth_required),
    db: Session = Depends(get_db),
    limit: int = Query(2, le=5)
):
    from app.models.intelligence_models import Insight
    insights = db.query(Insight).filter(
        Insight.user_id == str(user.id),
        Insight.seen == False
    ).order_by(Insight.priority.desc()).limit(limit).all()
    
    return insights

@router.get("/signals/today", summary="Get computed signals and scores for today")
def get_today_signals(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    from app.models.intelligence_models import Score, DerivedSignal
    today = date.today()
    
    score = db.query(Score).filter(Score.user_id == str(user.id), Score.date == today).first()
    signal = db.query(DerivedSignal).filter(DerivedSignal.user_id == str(user.id), DerivedSignal.date == today).first()
    
    return {
        "date": today,
        "score": score,
        "signals": signal
    }

@router.get("/loops", summary="Fetch active psychological loops and interventions")
def get_active_loops(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    from app.models.intelligence_models import LoopDetection
    loops = db.query(LoopDetection).filter(
        LoopDetection.user_id == str(user.id),
        LoopDetection.active == True
    ).all()
    
    return loops
