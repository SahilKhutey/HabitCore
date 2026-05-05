import sqlite3
import os

db_path = "backend/habithero.db"

def fix_schema():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")

    # Add missing columns
    missing = {
        "current_streak": "INTEGER DEFAULT 0",
        "followers": "INTEGER DEFAULT 0",
        "streak_freeze": "INTEGER DEFAULT 1",
        "referral_code": "TEXT UNIQUE",
        "last_active_hour": "INTEGER DEFAULT 9",
        "paywall_variant": "TEXT DEFAULT 'A'",
        "is_admin": "BOOLEAN DEFAULT 0",
        "is_active": "BOOLEAN DEFAULT 1",
        "social_id": "TEXT",
        "provider": "TEXT DEFAULT 'email'",
        "mode": "TEXT DEFAULT 'Consistency'",
        "progress_style": "TEXT DEFAULT 'bar'",
        "engagement_level": "TEXT DEFAULT 'Balanced'",
        "reward_type": "TEXT DEFAULT 'visual'",
        "identity_goal": "TEXT DEFAULT 'Productive'",
        "identity_level": "TEXT DEFAULT 'beginner'",
        "daily_habit_goal": "INTEGER DEFAULT 3",
        "timezone": "TEXT DEFAULT 'UTC'",
        "onboarding_state": "JSON",
        "identity_profile": "JSON",
        "cognitive_level": "INTEGER DEFAULT 1",
        "archetype": "TEXT"
    }

    for col, spec in missing.items():
        if col not in columns:
            print(f"Adding column: {col}")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {spec}")
            except Exception as e:
                print(f"Failed to add {col}: {e}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='habits'")
    if cursor.fetchone():
        # Frequency
        try: cursor.execute("ALTER TABLE habits ADD COLUMN frequency INTEGER DEFAULT 7")
        except: pass
        
        # Condition
        try: cursor.execute("ALTER TABLE habits ADD COLUMN condition TEXT")
        except: pass

        # Streak Target
        try: cursor.execute("ALTER TABLE habits ADD COLUMN streak_target INTEGER DEFAULT 30")
        except: pass

        # Current Streak
        try: cursor.execute("ALTER TABLE habits ADD COLUMN current_streak INTEGER DEFAULT 0")
        except: pass

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    fix_schema()
