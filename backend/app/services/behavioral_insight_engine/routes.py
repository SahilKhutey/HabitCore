"""
Insights Router — FastAPI endpoints for the Behavioral Insight Engine.

Endpoints:
  POST /insights/run          Trigger insight generation for current user
  GET  /insights/behavioral   Fetch ranked insight feed
  POST /insights/mark-read    Mark an insight as read
  POST /insights/dismiss      Dismiss an insight permanently
  GET  /insights/growth-report  Weekly growth narrative report
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, auth_required
from app.services.behavioral_insight_engine.service import BehavioralInsightService
from app.services.behavioral_insight_engine.schemas import InsightOut, GrowthReportOut
from app.models.habit import Habit


router = APIRouter()


# ── Request bodies ────────────────────────────────────────────────────────────

class MarkReadRequest(BaseModel):
    insight_id: str

class DismissRequest(BaseModel):
    insight_id: str

class RunInsightsRequest(BaseModel):
    force: bool = False   # ignore dedup window and regenerate


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/run", summary="Trigger behavioral insight generation for the current user")
def run_insights(
    req: RunInsightsRequest = RunInsightsRequest(),
    user = Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Runs the full BehavioralInsightEngine pipeline for the authenticated user.
    Returns newly generated insights (not previously stored ones).

    Typically called server-side after habit completion or check-in.
    Can be called from client with force=True to refresh.
    """
    habit_count = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True,
    ).count()

    archetype = getattr(user, "archetype", None) or getattr(user, "identity_goal", "pioneer") or "pioneer"

    svc = BehavioralInsightService(db)
    new_insights = svc.run_for_user(
        user_id=str(user.id),
        habit_count=habit_count,
        archetype=archetype,
    )

    return {
        "generated": len(new_insights),
        "insights": [
            {
                "type": i.type,
                "category": i.category,
                "message": i.message,
                "action_hint": i.action_hint,
                "confidence": i.confidence,
            }
            for i in new_insights
        ]
    }


@router.get(
    "/behavioral",
    response_model=List[InsightOut],
    summary="Get ranked behavioral insight feed for current user"
)
def get_behavioral_insights(
    limit: int = 10,
    include_read: bool = False,
    user = Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Returns the user's behavioral insight feed, ordered by rank_score (confidence × impact),
    with time decay applied to older insights.

    Params:
      limit:        max number of insights to return (default 10)
      include_read: include already-read insights (default False)
    """
    svc = BehavioralInsightService(db)
    return svc.get_feed(
        user_id=str(user.id),
        limit=min(limit, 25),
        include_read=include_read,
    )


@router.post("/mark-read", summary="Mark a behavioral insight as read")
def mark_insight_read(
    req: MarkReadRequest,
    user = Depends(auth_required),
    db: Session = Depends(get_db),
):
    svc = BehavioralInsightService(db)
    found = svc.mark_read(str(user.id), req.insight_id)
    if not found:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"status": "marked_read", "insight_id": req.insight_id}


@router.post("/dismiss", summary="Permanently dismiss an insight from the feed")
def dismiss_insight(
    req: DismissRequest,
    user = Depends(auth_required),
    db: Session = Depends(get_db),
):
    svc = BehavioralInsightService(db)
    found = svc.mark_dismissed(str(user.id), req.insight_id)
    if not found:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"status": "dismissed", "insight_id": req.insight_id}


@router.get(
    "/growth-report",
    response_model=GrowthReportOut,
    summary="Weekly behavioral growth narrative report"
)
def get_growth_report(
    days: int = 7,
    user = Depends(auth_required),
    db: Session = Depends(get_db),
):
    """
    Generates a narrative behavioral report for the last N days.
    Includes trend direction, completion rate, top pattern and warning,
    and a plain-language 2–3 sentence summary.
    """
    svc = BehavioralInsightService(db)
    return svc.get_growth_report(str(user.id), days=min(days, 30))
