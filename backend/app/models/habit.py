from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.db.declarative import Base
import uuid
from datetime import datetime

class Habit(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String)
    name = Column(String)
    time = Column(String) # Morning, Afternoon, Night
    difficulty = Column(String, default="medium") # easy, medium, hard
    target_per_day = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)     # False = archived
    last_adjusted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
