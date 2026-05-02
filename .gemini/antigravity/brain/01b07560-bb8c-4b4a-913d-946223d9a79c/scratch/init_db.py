import sys
import os
sys.path.append(r"c:\Users\User\Documents\HabitCore\backend")

from app.db.session import engine
from app.db.declarative import Base
import app.db.base # This imports all models to Base.metadata

def init_db():
    print("Creating all tables in database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
