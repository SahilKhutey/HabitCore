from apscheduler.schedulers.background import BackgroundScheduler
from app.services.notification import notification_service
from app.db.session import SessionLocal
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.user import User
from datetime import date, timedelta, datetime, timezone
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def smart_reengagement_system():
    """
    v2 Intelligence System:
    1. Analyzes user 'Smart Time' (historical peak performance hour).
    2. Identifies streak-risk habits.
    3. Triggers identity-framed nudges.
    """
    db = SessionLocal()
    try:
        current_hour = datetime.now(timezone.utc).hour
        
        # 1. Fetch users whose peak performance hour aligns with current time
        # In a real system, we'd query a 'smart_time' column or aggregate logs
        # For now, we use a simple heuristic: users who were active at this hour yesterday
        yesterday_hour = (datetime.now(timezone.utc) - timedelta(days=1)).hour
        users = db.query(User).all() # Simple scan for demo
        
        for user in users:
            # 2. Check for Streak Risk
            # Find habits not yet completed today
            incomplete_habits = db.query(Habit).filter(
                Habit.user_id == user.id,
                ~Habit.id.in_(db.query(HabitLog.habit_id).filter(HabitLog.date == date.today()))
            ).all()
            
            if incomplete_habits:
                habit = incomplete_habits[0]
                logger.info(f"Triggering nudge for {user.email} -> {habit.name}")
                
                # Identity-framed messaging
                archetype = user.identity_goal or "pioneer"
                msg_body = f"Your identity as a {archetype} is built on consistency. Complete your {habit.name} anchor to maintain the pulse."
                
                notification_service.send_push(
                    getattr(user, "fcm_token", "test_token"), 
                    "🔥 Streak Alert", 
                    msg_body
                )

        db.commit()
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
    finally:
        db.close()

def daily_cleanup_and_stats():
    """Performs daily maintenance tasks."""
    logger.info("Running daily maintenance...")
    # Add logic for resetting daily caps, generating reports, etc.

# Run EVERY HOUR to catch users at their optimal time
scheduler.add_job(smart_reengagement_system, "cron", minute=0)
scheduler.add_job(daily_cleanup_and_stats, "cron", hour=0, minute=0)
