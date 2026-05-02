from apscheduler.schedulers.background import BackgroundScheduler
from app.services.notification import notification_service
from app.db.session import SessionLocal
from app.models.habit import Habit
from app.models.habit_log import HabitLog

from app.models.user import User
from datetime import date, timedelta, datetime

scheduler = BackgroundScheduler()

def smart_reengagement_system():
    db = SessionLocal()
    current_hour = datetime.utcnow().hour
    
    # Fetch users whose optimal active hour is NOW
    users_to_notify = db.query(User).filter(User.last_active_hour == current_hour).all()
    
    for user in users_to_notify:
        # 1. Check for Streak Risk
        at_risk_habit = db.query(Habit).filter(
            Habit.user_id == user.id,
            ~Habit.id.in_(db.query(HabitLog.habit_id).filter(HabitLog.date == date.today()))
        ).first()
        
        if at_risk_habit:
            print(f"🚀 SMART NOTIFY: User {user.id} at hour {current_hour}")
            # send_push(user.fcm_token, "🔥 Save your streak!", f"Don't lose progress on {at_risk_habit.title}")
            continue

        # 2. Reward Tease (if no streak risk)
        if user.coins < 100:
             print(f"🎁 REWARD TEASE: User {user.id}")
             # send_push(user.fcm_token, "🎁 Unclaimed Rewards", "Complete 1 habit to earn bonus Coins!")

    db.close()

# Run EVERY HOUR to catch users at their optimal time
scheduler.add_job(smart_reengagement_system, "cron", minute=0)
