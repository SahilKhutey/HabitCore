from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from app.core.habit_orchestrator import get_habit_orchestrator
from app.api.deps import get_db, auth_required

router = APIRouter()

class HabitCompletionRequest(BaseModel):
    habit_id: str
    habit_name: str
    difficulty: str = "medium"
    completed: bool = True
    current_streak: int = 0
    metadata: Dict[str, Any] = {}

@router.post("/complete")
async def complete_habit(
    request: HabitCompletionRequest,
    user = Depends(auth_required),
    db: Session = Depends(get_db)
):
    """Complete a habit - main orchestration endpoint"""
    try:
        orchestrator = get_habit_orchestrator(db)
        result = await orchestrator.process_habit_completion(
            user.id,
            request.dict()
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        print(f"Route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state")
async def get_user_state(
    user = Depends(auth_required),
    db: Session = Depends(get_db)
):
    """Get current user state and recommendations"""
    try:
        orchestrator = get_habit_orchestrator(db)
        
        user_state = await orchestrator._update_user_state(user.id)
        ai_advice = await orchestrator._get_ai_advice(user.id, user_state)
        
        return {
            "user_state": user_state,
            "ai_advice": ai_advice,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
