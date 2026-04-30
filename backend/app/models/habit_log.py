from sqlalchemy import Column, String, Date, Boolean, DateTime
from app.db.base import Base
import uuid
from datetime import date, datetime

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String)
    date = Column(Date, default=date.today)
    completed_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=True)
