"""
BFE Routes — Behavioral Feedback Engine API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, auth_required
from app.services.behavioral_feedback_engine.service import BehavioralFeedbackService
from app.services.behavioral_feedback_engine.schemas import (
    BFESessionOut, DailyInput, UserSystemState, BFEInsight
)

router = APIRouter()

@router.post("/process", response_model=BFESessionOut, summary="Process daily behavioral input and get system feedback")
def process_behavioral_input(
    input_data: DailyInput,
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    """
    Main entry point for the Behavioral Feedback Engine.
    Processes the user's daily input (mood, energy, behavior, etc.) 
    and returns adaptive directives, insights, and state analysis.
    """
    svc = BehavioralFeedbackService(db)
    return svc.process_daily_input(str(user.id), input_data)

@router.get("/state", summary="Get current user behavioral state and directives")
def get_behavioral_state(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    """
    Returns the user's current behavioral state (stable, struggling, etc.)
    and the corresponding system directives (reduce inputs, disable streaks, etc.)
    """
    svc = BehavioralFeedbackService(db)
    state = svc.get_user_state(str(user.id))
    if not state:
        return {
            "current_state": "stable",
            "directives": {
                "state": "stable",
                "reduce_inputs": False,
                "max_input_fields": 8,
                "focus_mode": "action"
            }
        }
    return {
        "current_state": state.current_state,
        "directives": state.directives,
        "last_score": state.last_score,
        "updated_at": state.updated_at
    }

@router.get("/weekly-meta", summary="Get weekly behavioral meta analysis")
def get_weekly_meta(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    """
    Returns the weekly meta-analysis including trends, peak days, 
    and identity consistency ratio.
    """
    svc = BehavioralFeedbackService(db)
    state = svc.get_user_state(str(user.id))
    if not state or not state.weekly_meta:
        raise HTTPException(status_code=404, detail="Weekly meta not found. Process a daily input first.")
    return state.weekly_meta
