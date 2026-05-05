"""
Nudge Decision Engine — Context-aware scoring and cooldown management.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

def score_nudge(pattern: Dict[str, Any], context: Dict[str, Any]) -> float:
    """
    Calculates a relevance score (0.0 - 1.0) for a potential nudge.
    """
    score = 0.0
    p_type = pattern.get("pattern_type") or pattern.get("event_type")
    
    # 1. Pattern Confidence (40% weight)
    confidence = pattern.get("confidence") or pattern.get("metadata", {}).get("confidence", 0.0)
    score += confidence * 0.4
    
    # 2. User State Adaptation (20% weight)
    if context.get("energy", 5) < 4:
        score += 0.2 # Higher priority when struggling
        
    # 3. Repetition Bias (20% weight)
    if context.get("pattern_recurring", False):
        score += 0.2
        
    # 4. Activity Context (20% weight)
    if context.get("active_session"):
        score += 0.2
        
    # 5. Journey Phase Boost (30% weight - Overrides for critical days)
    journey_day = context.get("journey_day", 0)
    p_type = pattern.get("pattern_type") or pattern.get("event_type")
    
    # 5. Event Type Boost
    if p_type == "habit_completed":
        score += 0.2
    elif p_type == "burnout_risk":
        score += 0.4

    return min(max(score, 0.0), 1.0)

def should_skip_nudge(user_id: str, last_nudge_at: Optional[datetime]) -> bool:
    """
    Enforces a 30-minute cooldown to prevent notification fatigue.
    """
    if not last_nudge_at:
        return False
        
    now = datetime.now(timezone.utc)
    if last_nudge_at.tzinfo is None:
        last_nudge_at = last_nudge_at.replace(tzinfo=timezone.utc)
        
    cooldown = timedelta(minutes=30)
    return (now - last_nudge_at) < cooldown
