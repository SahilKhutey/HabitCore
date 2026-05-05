import sys
import os
from datetime import datetime, timedelta, date, timezone
import uuid

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.behavioral import UserBehaviorLog
from app.core.security import hash_password

def seed_demo_experience():
    db = SessionLocal()
    try:
        # 1. Ensure Demo User exists
        email = "sim_v2_0@simulator.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"Creating demo user: {email}")
            user = User(
                email=email,
                password_hash=hash_password("sim_password_123"),
                xp=1450,
                level=12,
                coins=450,
                is_premium=True,
                archetype="monk",
                identity_goal="Calm",
                identity_level="disciplined",
                daily_habit_goal=4
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"Updating demo user: {email}")
            user.xp = 1450
            user.level = 12
            user.coins = 450
            user.archetype = "monk"
            user.identity_goal = "Calm"
            user.is_premium = True
            db.commit()

        # 2. Add Habits
        print("Seeding habits...")
        # Clear existing habits to start fresh
        db.query(Habit).filter(Habit.user_id == user.id).delete()
        
        demo_habits = [
            {"name": "Morning Sunlight", "time": "07:30", "difficulty": "easy"},
            {"name": "Deep Work Session", "time": "10:00", "difficulty": "hard"},
            {"name": "Hydration (3L)", "time": "14:00", "difficulty": "medium"},
            {"name": "Evening Gratitude", "time": "22:00", "difficulty": "easy"},
            {"name": "Post-Workout Protein", "time": "18:00", "difficulty": "medium"}
        ]
        
        habit_objs = []
        for h in demo_habits:
            obj = Habit(user_id=user.id, name=h["name"], time=h["time"], difficulty=h["difficulty"])
            db.add(obj)
            habit_objs.append(obj)
        
        db.commit()
        for h in habit_objs: db.refresh(h)

        # 3. Add History (Last 30 Days)
        print("Seeding history (30 days)...")
        # Clear existing logs
        db.query(HabitLog).filter(HabitLog.user_id == user.id).delete()
        
        today = date.today()
        for i in range(30):
            current_date = today - timedelta(days=i)
            # Higher completion rate on weekdays
            is_weekend = current_date.weekday() >= 5
            completion_chance = 0.5 if is_weekend else 0.85
            
            for habit in habit_objs:
                import random
                if random.random() < completion_chance:
                    # Randomize completion time slightly around the goal time
                    h_hour, h_min = map(int, habit.time.split(':'))
                    comp_time = datetime.combine(
                        current_date, 
                        datetime.min.time()
                    ).replace(hour=h_hour, minute=h_min) + timedelta(minutes=random.randint(-15, 45))
                    
                    log = HabitLog(
                        user_id=user.id,
                        habit_id=habit.id,
                        date=current_date,
                        completed_at=comp_time.replace(tzinfo=timezone.utc)
                    )
                    db.add(log)
        
        db.commit()

        # 4. Add Behavioral Signals
        print("Seeding behavioral signals...")
        db.query(UserBehaviorLog).filter(UserBehaviorLog.user_id == user.id).delete()
        
        signals = [
            {"type": "app_open", "data": {"device": "iPhone 15"}},
            {"type": "high_focus_detected", "data": {"session_length": 120}},
            {"type": "evening_slump", "data": {"mood": "tired"}},
            {"type": "streak_milestone", "data": {"streak": 14}},
            {"type": "shop_view", "data": {"category": "themes"}}
        ]
        
        for s in signals:
            blog = UserBehaviorLog(
                user_id=user.id,
                event_type=s["type"],
                event_data=s["data"],
                context={"timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))).isoformat()}
            )
            db.add(blog)
            
        db.commit()
        print("Demo Experience Seeded Successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import random
    seed_demo_experience()
