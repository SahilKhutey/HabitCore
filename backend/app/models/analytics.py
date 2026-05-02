from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.declarative import Base
import uuid

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    event_type = Column(String, index=True) # e.g., "habit_completed", "item_purchased"
    metadata_json = Column(JSON) # Additional data (streak, coins spent, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
