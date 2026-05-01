from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.api.deps import get_db, auth_required
from app.models.user import User
from app.models.analytics import AnalyticsEvent
from datetime import datetime, timedelta, timezone

router = APIRouter()

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
    # Simple heuristic: inactive for 3+ days
    threshold = datetime.now(timezone.utc) - timedelta(days=3)

    users = db.query(User).filter(User.last_active_hour < threshold.hour).all() # This is a placeholder logic
    return {"at_risk_count": len(users)}

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
