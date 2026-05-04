from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.db.declarative import Base
import uuid
from datetime import datetime, timezone

class Habit(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String)
    name = Column(String)
    time = Column(String) # Morning, Afternoon, Night
    difficulty = Column(String, default="medium") # easy, medium, hard
    target_per_day = Column(Integer, default=1)
    done = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)     # False = archived
    last_adjusted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
