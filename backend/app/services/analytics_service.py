from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsEvent
from app.services.websocket_service import manager
import asyncio

class AnalyticsService:
    @staticmethod
    def log_event(db: Session, user_id: str, event_type: str, metadata: dict = {}):
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            metadata_json=metadata
        )
        db.add(event)
        db.commit()
        
        # Broadcast via WebSockets (async)
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "metadata": metadata,
            "created_at": str(event.created_at)
        }
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(event_data))

        return event
