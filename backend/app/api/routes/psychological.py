from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from app.api.deps import get_db, auth_required
from app.services.psychological_service import psychological_service
from app.services.reward_service import reward_service
from app.services.behavior_memory_service import BehaviorMemoryService
from app.services.ai_service import AIService, get_ai_service
from app.core.security import security_engine
from app.models.psychological import DailyCheckin

router = APIRouter()

# Global cached AI service instance
behavior_service_mock = None # Will be initialized per request or use a factory
cached_ai_service = None

def get_cached_ai_service(db: Session):
    global cached_ai_service
    if not cached_ai_service:
        behavior_service = BehaviorMemoryService(db)
        cached_ai_service = AIService(behavior_service)
    return cached_ai_service

# Behavior routes
@router.post("/behavior/log")
def log_behavior(event_type: str, event_data: Dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    # Security check
    if not security_engine.validate_event(user.id, event_type, event_data):
        raise HTTPException(status_code=429, detail="Too many requests or invalid data")
        
    service = BehaviorMemoryService(db)
    service.log_behavior(user.id, event_type, event_data)
    return {"success": True}

@router.get("/behavior/patterns")
def get_patterns(user=Depends(auth_required), db: Session = Depends(get_db)):
    service = BehaviorMemoryService(db)
    # Trigger analysis
    service.analyze_time_patterns(user.id)
    service.analyze_day_patterns(user.id)
    
    patterns = service.get_user_patterns(user.id)
    burnout_score = service.calculate_burnout_score(user.id)
    
    return {
        "success": True, 
        "patterns": patterns,
        "burnout_score": burnout_score
    }

@router.post("/ai-coach/advice")
def get_ai_advice(context: Dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    # Security check
    if not security_engine.validate_event(user.id, "ai_coach", context):
        raise HTTPException(status_code=429, detail="Too many requests")
        
    service = get_cached_ai_service(db)
    advice = service.get_personalized_advice(user.id, context)
    return {"success": True, "advice": advice}

class CheckinRequest(BaseModel):
    mood: str
    energy_morning: str
    energy_evening: str
    sleep_quality: int
    tags: Optional[List[str]] = []
    reflection: Optional[str] = None

class HabitCompletionRequest(BaseModel):
    habit_id: str
    completed: bool
    difficulty: str

@router.post("/checkin")
def daily_checkin(request: CheckinRequest, user=Depends(auth_required), db: Session = Depends(get_db)):
    try:
        # Store checkin data
        checkin = DailyCheckin(
            user_id=user.id,
            mood=request.mood,
            energy_morning=request.energy_morning,
            energy_evening=request.energy_evening,
            sleep_quality=request.sleep_quality,
            tags=request.tags,
            reflection=request.reflection
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        
        # 1. Push reflection to Kafka for NLP analysis (asynchronous)
        if request.reflection:
            from app.services.core.kafka_service import KafkaService
            KafkaService.send_user_text_event(str(user.id), request.reflection)

        # 2. Generate insights
        checkin_dict = {
            "mood": checkin.mood,
            "energy_morning": checkin.energy_morning,
            "energy_evening": checkin.energy_evening,
            "sleep_quality": checkin.sleep_quality
        }
        
        insights = psychological_service.calculate_daily_insights(
            checkin_dict, 
            {}  # Would include habit data in real implementation
        )
        
        return {
            "success": True,
            "checkin": {
                "id": checkin.id,
                "date": checkin.date.isoformat(),
                "mood": checkin.mood
            },
            "insights": insights,
            "message": psychological_service.generate_encouragement_message(True, {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkin error: {str(e)}")

# Redundant /habits/complete moved to habits.py

@router.get("/daily-challenge")
def get_daily_challenge():
    try:
        challenge = reward_service.generate_daily_challenge()
        return {
            "success": True,
            "challenge": challenge
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge generation error: {str(e)}")

@router.get("/user-progress")
def get_user_progress(user=Depends(auth_required)):
    try:
        return {
            "success": True,
            "progress": {
                "xp": user.xp,
                "level": user.level,
                "coins": user.coins,
                "identity_level": user.identity_level,
                "archetype": user.archetype,
                # "badges" and "unlocked_features" would fetch from separate tables/logic
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress fetch error: {str(e)}")


# ─── LIFE DOMAINS ─────────────────────────────────────────────────────────────

# Auto-tag habits to life domains by name keywords
DOMAIN_KEYWORDS = {
    "physical": ["run", "workout", "gym", "exercise", "yoga", "stretch", "walk", "fitness", "steps", "pushup", "push-up", "plank", "swim", "bike", "sport"],
    "mental":   ["meditat", "mindful", "journal", "read", "learn", "study", "focus", "breath", "gratitude", "reflect", "think", "cognitive"],
    "work":     ["deep work", "cod", "writ", "plan", "review", "project", "email", "meeting", "productiv", "task", "build", "design", "research"],
    "social":   ["call", "connect", "friend", "family", "communit", "volunteer", "network", "social", "talk", "meet"],
    "sleep":    ["sleep", "rest", "nap", "bedtime", "wind down", "night"],
}

def classify_habit_domain(name: str) -> str:
    name_lower = name.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return domain
    return "mental"  # Default uncategorised → mental

@router.get("/life-domains")
def get_life_domains(user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Computes life domain scores (0-100) from habit completions + checkin data.
    Domains: physical, mental, work, social, sleep
    """
    from app.models.habit import Habit
    from app.models.habit_log import HabitLog
    from sqlalchemy import func
    from datetime import date, timedelta

    # Last 7 days
    today = date.today()
    week_ago = today - timedelta(days=7)

    # Get all user habits with completion counts this week
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    logs_this_week = db.query(
        HabitLog.habit_id,
        func.count(HabitLog.id).label("count")
    ).join(Habit, Habit.id == HabitLog.habit_id).filter(
        Habit.user_id == user.id,
        HabitLog.date >= week_ago,
    ).group_by(HabitLog.habit_id).all()

    log_map = {row.habit_id: row.count for row in logs_this_week}
    
    # Score per domain: completions/7 * 100 (max 100)
    domain_totals = {d: {"completed": 0, "total_possible": 0, "habits": []} for d in DOMAIN_KEYWORDS}
    
    for habit in habits:
        domain = classify_habit_domain(habit.name)
        if domain in domain_totals:
            completions = log_map.get(habit.id, 0)
            domain_totals[domain]["completed"] += completions
            domain_totals[domain]["total_possible"] += 7
            domain_totals[domain]["habits"].append(habit.name)

    # Get latest checkin for sleep and mood boost
    latest = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
    ).order_by(DailyCheckin.date.desc()).first()

    domains = []
    domain_meta = {
        "physical": {"label": "Physical", "emoji": "💪", "color": "#33ffd6"},
        "mental":   {"label": "Mental",   "emoji": "🧠", "color": "#a78bfa"},
        "work":     {"label": "Work",     "emoji": "💼", "color": "#38bdf8"},
        "social":   {"label": "Social",   "emoji": "💞", "color": "#f472b6"},
        "sleep":    {"label": "Sleep",    "emoji": "😴", "color": "#fbbf24"},
    }

    for domain, meta in domain_meta.items():
        data = domain_totals[domain]
        if data["total_possible"] > 0:
            score = round((data["completed"] / data["total_possible"]) * 100)
        elif domain == "sleep" and latest:
            score = round((latest.sleep_quality / 5) * 100)
        else:
            score = 0

        # Sleep domain boost from checkin
        if domain == "sleep" and latest and latest.sleep_quality:
            score = max(score, round((latest.sleep_quality / 5) * 100))

        domains.append({
            "domain": domain,
            **meta,
            "score": min(100, score),
            "habits": data["habits"],
            "completions_this_week": data["completed"],
        })

    # Overall life score
    overall = round(sum(d["score"] for d in domains) / len(domains))

    return {
        "success": True,
        "domains": domains,
        "overall_score": overall,
        "checkin_mood": latest.mood if latest else None,
        "checkin_date": latest.date.isoformat() if latest else None,
    }


@router.get("/checkin/history")
def get_checkin_history(days: int = 7, user=Depends(auth_required), db: Session = Depends(get_db)):
    """Returns last N days of mood check-ins for trend charts."""
    from datetime import date, timedelta

    today = date.today()
    since = today - timedelta(days=days)

    checkins = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date >= since
    ).order_by(DailyCheckin.date.asc()).all()

    # Map mood to numeric score for charting
    mood_scores = {"happy": 5, "excited": 5, "neutral": 3, "tired": 2, "sad": 1, "angry": 1}

    result = []
    for c in checkins:
        result.append({
            "date": c.date.isoformat(),
            "mood": c.mood,
            "mood_score": mood_scores.get(c.mood, 3),
            "energy_morning": c.energy_morning,
            "energy_evening": c.energy_evening,
            "sleep_quality": c.sleep_quality,
            "reflection": c.reflection,
        })

    return {"success": True, "checkins": result, "total": len(result)}


@router.get("/today-checkin")
def get_today_checkin(user=Depends(auth_required), db: Session = Depends(get_db)):
    """Returns today's check-in if it exists, else None."""
    from datetime import date
    today = date.today()
    checkin = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user.id,
        DailyCheckin.date == today
    ).first()

    if not checkin:
        return {"done": False, "checkin": None}

    return {
        "done": True,
        "checkin": {
            "mood": checkin.mood,
            "energy_morning": checkin.energy_morning,
            "sleep_quality": checkin.sleep_quality,
        }
    }
