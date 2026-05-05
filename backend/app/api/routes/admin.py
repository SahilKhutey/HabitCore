from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc
from app.api.deps import get_db, auth_required
from app.models.user import User
from app.models.analytics import AnalyticsEvent
from app.models.habit import Habit
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    premium_users = db.query(func.count(User.id)).filter(User.is_premium == True).scalar()
    total_coins = db.query(func.sum(User.coins)).scalar() or 0
    
    # Growth calculation (last 24h vs previous 24h)
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)
    
    new_users_last_24h = db.query(func.count(User.id)).filter(User.created_at >= day_ago).scalar()
    new_users_prev_24h = db.query(func.count(User.id)).filter(User.created_at >= two_days_ago, User.created_at < day_ago).scalar()
    
    growth = 0
    if new_users_prev_24h > 0:
        growth = ((new_users_last_24h - new_users_prev_24h) / new_users_prev_24h) * 100
    
    return {
        "total_users": total_users,
        "premium_rate": round((premium_users / total_users * 100), 1) if total_users > 0 else 0,
        "system_treasury": total_coins,
        "growth_velocity": f"{'+' if growth >= 0 else ''}{growth:.1f}%"
    }

@router.get("/analytics/archetype-distribution")
def get_archetype_distribution(db: Session = Depends(get_db)):
    results = db.query(
        User.archetype,
        func.count(User.id).label('count')
    ).group_by(User.archetype).all()
    
    return [{"archetype": r.archetype or "unknown", "count": r.count} for r in results]

@router.get("/analytics/top-habits")
def get_top_habits(db: Session = Depends(get_db)):
    results = db.query(
        Habit.name,
        func.count(Habit.id).label('popularity')
    ).group_by(Habit.name).order_by(desc('popularity')).limit(5).all()
    
    return [{"name": r.name, "count": r.popularity} for r in results]

@router.get("/analytics/dau")
def get_dau(db: Session = Depends(get_db)):
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)

    dau = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
        AnalyticsEvent.event_type == "app_open",
        AnalyticsEvent.created_at >= one_day_ago
    ).scalar()
    return {"dau": dau or 0}

@router.get("/analytics/user-growth")
def get_user_growth(db: Session = Depends(get_db)):
    # Group users by creation date (last 7 days)
    seven_days_ago = datetime.now(timezone.utc).date() - timedelta(days=7)

    
    # Simple query to get daily counts
    results = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('users')
    ).filter(User.created_at >= seven_days_ago).group_by('date').all()
    
    return [{"date": str(r.date), "users": r.users} for r in results]

@router.get("/analytics/events")
def get_recent_events(db: Session = Depends(get_db)):
    # Get last 50 events for the live feed
    events = db.query(AnalyticsEvent).order_by(AnalyticsEvent.created_at.desc()).limit(50).all()
    return [{
        "user_id": e.user_id,
        "event_type": e.event_type,
        "created_at": str(e.created_at)
    } for e in events]

@router.get("/analytics/retention")
def get_retention_cohorts(db: Session = Depends(get_db)):
    # SQL Adapted for compatibility
    query = text("""
    WITH first_seen AS (
        SELECT user_id, MIN(DATE(created_at)) AS signup_date
        FROM analytics_events
        WHERE event_type = 'app_open'
        GROUP BY user_id
    ),
    activity AS (
        SELECT e.user_id, DATE(e.created_at) AS activity_date, f.signup_date
        FROM analytics_events e
        JOIN first_seen f ON e.user_id = f.user_id
    )
    SELECT 
        signup_date,
        COUNT(DISTINCT CASE WHEN activity_date = signup_date THEN user_id END) AS d0,
        COUNT(DISTINCT CASE WHEN activity_date = date(signup_date, '+1 day') THEN user_id END) AS d1,
        COUNT(DISTINCT CASE WHEN activity_date = date(signup_date, '+7 day') THEN user_id END) AS d7
    FROM activity
    GROUP BY signup_date
    ORDER BY signup_date DESC;
    """)
    
    result = db.execute(query)
    return [dict(row._asdict()) for row in result]

@router.get("/churn-risk-users")
def get_churn_risk_users(db: Session = Depends(get_db)):
    # Identify users inactive for 3+ days based on latest analytics event
    threshold = datetime.now(timezone.utc) - timedelta(days=3)
    
    latest_events = db.query(
        AnalyticsEvent.user_id,
        func.max(AnalyticsEvent.created_at).label("latest_activity")
    ).group_by(AnalyticsEvent.user_id).subquery()
    
    at_risk_count = db.query(func.count(User.id)).outerjoin(
        latest_events, User.id == latest_events.c.user_id
    ).filter(
        (latest_events.c.latest_activity < threshold) | 
        ((latest_events.c.latest_activity == None) & (User.created_at < threshold))
    ).scalar()
    
    return {"at_risk_count": at_risk_count or 0}

@router.post("/ban/{user_id}")
def ban_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404)
    user.is_active = False
    db.commit()
    return {"message": "User banned"}

@router.post("/grant-premium/{user_id}")
def grant_premium(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404)
    user.is_premium = True
    db.commit()
    return {"message": "Premium granted"}
