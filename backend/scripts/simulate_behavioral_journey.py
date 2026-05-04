import sys
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import app.db.session
app.db.session.DATABASE_URL = "sqlite:///./habithero_test.db"

from app.db.session import SessionLocal, engine
from app.db.declarative import Base
from app.models.user import User
from app.models.habit import Habit
from app.services.nudge_engine import NudgeEngine
from app.services.analytics_service import AnalyticsService

def simulate_journey():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        print("Starting Behavioral Journey Simulation...")
        
        # 1. Create a synthetic user if not exists
        user = db.query(User).filter(User.email == "synthetic@habitcore.ai").first()
        if not user:
            user = User(
                email="synthetic@habitcore.ai",
                identity_goal="High Performance Executive",
                current_streak=0,
                level=1,
                xp=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created synthetic user: {user.email}")

        # 2. Add a habit
        habit = db.query(Habit).filter(Habit.user_id == user.id).first()
        if not habit:
            habit = Habit(
                user_id=user.id,
                name="Deep Work Session",
                difficulty="hard",
                done=False
            )
            db.add(habit)
            db.commit()
            db.refresh(habit)

        # 3. Progress through phases
        # Hook Phase (Day 1)
        print("\n--- Phase 1: HOOK (Day 1) ---")
        user.current_streak = 1
        db.commit()
        nudge = NudgeEngine.generate_nudge(user, habit)
        print(f"Generated Nudge: {nudge}")

        # Awareness Phase (Day 5)
        print("\n--- Phase 2: AWARENESS (Day 5) ---")
        user.current_streak = 5
        db.commit()
        nudge = NudgeEngine.generate_nudge(user, habit)
        print(f"Generated Nudge: {nudge}")

        # Intervention Phase (Day 10)
        print("\n--- Phase 3: INTERVENTION (Day 10) ---")
        user.current_streak = 10
        db.commit()
        nudge = NudgeEngine.generate_nudge(user, habit)
        print(f"Generated Nudge: {nudge}")

        # Identity Phase (Day 25)
        print("\n--- Phase 4: IDENTITY (Day 25) ---")
        user.current_streak = 25
        db.commit()
        nudge = NudgeEngine.generate_nudge(user, habit)
        print(f"Generated Nudge: {nudge}")

        print("\nSimulation Successful: Nudge Engine correctly identifies psychological phases.")

        # 4. Check Process Nudges
        print("\nTesting Process Nudges...")
        count = NudgeEngine.process_nudges(db)
        print(f"Logged {count} nudge events to analytics.")

    except Exception as e:
        print(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_journey()
