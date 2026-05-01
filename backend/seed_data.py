from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.analytics import AnalyticsEvent
from app.core.security import hash_password
from datetime import datetime, timedelta, date, timezone
import uuid

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Create Test User
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash=hash_password("password"),
            xp=150,
            level=2,
            coins=250,
            streak_freeze=2,
            is_premium=True,
            is_admin=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user: {test_user.email}")
    else:
        print("Test user already exists.")

    # 2. Create Habits
    habits_data = [
        {"name": "Morning Meditation", "time": "Morning", "difficulty": "easy"},
        {"name": "Read 10 Pages", "time": "Afternoon", "difficulty": "medium"},
        {"name": "Evening Workout", "time": "Night", "difficulty": "hard"},
    ]
    
    habits = []
    for h_data in habits_data:
        existing = db.query(Habit).filter(Habit.user_id == test_user.id, Habit.name == h_data["name"]).first()
        if not existing:
            h = Habit(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                name=h_data["name"],
                time=h_data["time"],
                difficulty=h_data["difficulty"]
            )
            db.add(h)
            habits.append(h)
            print(f"Created habit: {h.name}")
        else:
            habits.append(existing)

    db.commit()

    # 3. Create Logs for the last 7 days
    today = date.today()
    for i in range(7):
        log_date = today - timedelta(days=i)
        for h in habits:
            # Randomly skip some logs to make it look real
            if (i + len(h.name)) % 3 != 0:
                existing_log = db.query(HabitLog).filter(HabitLog.habit_id == h.id, HabitLog.date == log_date).first()
                if not existing_log:
                    log = HabitLog(
                        id=str(uuid.uuid4()),
                        habit_id=h.id,
                        date=log_date,
                        completed_at=datetime.combine(log_date, datetime.now().time()),
                        completed=True
                    )
                    db.add(log)
    
    db.commit()
    print("Seeded habit logs for the last 7 days.")

    # 4. Create Analytics Events
    event_types = ["app_open", "habit_completed", "streak_milestone"]
    for i in range(30):
        event_date = datetime.now(timezone.utc) - timedelta(days=i % 10)
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            event_type=event_types[i % 3],
            metadata_json={"os": "web", "version": "1.0.0"},
            created_at=event_date
        )
        db.add(event)
    
    db.commit()
    print("Seeded analytics events.")
    
    db.close()
    print("All seeding complete.")

if __name__ == "__main__":
    seed_data()
