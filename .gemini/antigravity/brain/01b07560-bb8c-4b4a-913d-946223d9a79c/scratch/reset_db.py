import sys
import os
sys.path.append(r"c:\Users\User\Documents\HabitCore\backend")

from app.db.session import engine
from sqlalchemy import text

def reset_questions_table():
    with engine.connect() as conn:
        print("Dropping questions table...")
        conn.execute(text("DROP TABLE IF EXISTS user_question_history"))
        conn.execute(text("DROP TABLE IF EXISTS question_usage_logs"))
        conn.execute(text("DROP TABLE IF EXISTS question_stats"))
        conn.execute(text("DROP TABLE IF EXISTS questions"))
        conn.commit()
    print("Tables dropped. Re-running init_db...")
    
    from app.db.declarative import Base
    import app.db.base
    print("Creating all tables in database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    reset_questions_table()
