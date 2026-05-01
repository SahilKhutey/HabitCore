from sqlalchemy import Column, String, Integer, JSON, Date, ForeignKey
from app.db.base import Base
import uuid
from datetime import date

class DailyCheckin(Base):
    __tablename__ = "daily_checkins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    date = Column(Date, default=date.today)
    mood = Column(String) # happy, neutral, sad, angry, tired
    energy_morning = Column(String) # high, medium, low
    energy_evening = Column(String) # high, medium, low
    sleep_quality = Column(Integer) # 1-5
    tags = Column(JSON, default=[])
    reflection = Column(String, nullable=True)
