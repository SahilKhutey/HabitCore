from sqlalchemy.orm import Session
from app.models.user import User
from app.models.analytics import AnalyticsEvent
from datetime import datetime, timedelta

class ChurnService:
    @staticmethod
    def calculate_churn_risk(db: Session, user: User):
        score = 0
        
        # 1. Recency (Days since last app_open)
        last_open = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user.id,
            AnalyticsEvent.event_type == "app_open"
        ).order_by(AnalyticsEvent.created_at.desc()).first()
        
        if not last_open:
            score += 50 # New user who never logged in?
        else:
            days_inactive = (datetime.utcnow() - last_open.created_at).days
            if days_inactive >= 3:
                score += 40
            elif days_inactive >= 1:
                score += 10
                
        # 2. Engagement (Habits completed last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        habits_completed = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user.id,
            AnalyticsEvent.event_type == "habit_completed",
            AnalyticsEvent.created_at >= seven_days_ago
        ).count()
        
        if habits_completed == 0:
            score += 30
        elif habits_completed < 3:
            score += 15
            
        # 3. Streak Strength
        if user.streak < 2:
            score += 20
            
        return score

    @staticmethod
    def get_at_risk_users(db: Session, threshold: int = 70):
        users = db.query(User).all()
        at_risk = []
        for user in users:
            score = ChurnService.calculate_churn_risk(db, user)
            if score >= threshold:
                at_risk.append({"user": user, "score": score})
        return at_risk
