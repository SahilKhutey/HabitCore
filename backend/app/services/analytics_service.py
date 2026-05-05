from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsEvent
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.core.kafka_service import KafkaService
from app.services.context_store.manager import ContextManager
import asyncio
import os
from datetime import datetime, timedelta, timezone
from app.core.constants import IDENTITY_WEIGHTS
from app.services.websocket_service import manager

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
        
        # 1. Broadcast via WebSockets (async)
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "metadata": metadata,
            "created_at": str(event.created_at)
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast(event_data))
        except RuntimeError:
            pass

        # 2. Publish Nudge to Redis SSE Stream (New for v2 Interactivity)
        if event_type == "nudge_generated" or event_type == "achievement_unlocked":
            try:
                ctx = ContextManager(host=os.environ.get("REDIS_HOST", "localhost"))
                message = metadata.get("message", "New behavioral signal detected.")
                nudge_type = "reminder" if event_type == "nudge_generated" else "success"
                ctx.publish_nudge(user_id, message, nudge_type)
            except Exception as e:
                print(f"[Analytics] Redis Publish Error: {e}")

        # 3. Push to Kafka for real-time streaming pipeline
        KafkaService.send_behavioral_event(
            user_id=user_id,
            event_type=event_type,
            value=metadata.get("value", 1.0),
            metadata=metadata
        )

    @staticmethod
    def get_identity_pulse(db: Session, user_id: str):
        """
        Calculates how aligned a user's recent actions are with their stated identity goal.
        Deep analysis of habit domains vs. identity mapping.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        # 1. Fetch completions from last 30 days
        pulse_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        thirty_days_ago = pulse_cutoff.replace(tzinfo=None) 
        
        completions = db.query(HabitLog.id, Habit.name, Habit.domain).join(Habit, HabitLog.habit_id == Habit.id).filter(
            Habit.user_id == user_id,
            HabitLog.completed_at >= thirty_days_ago
        ).all()

        # 2. Score based on identity goal mapping
        # Maps identity to preferred domains
        IDENTITY_DOMAIN_MAP = {
            "monk": ["mental", "sleep", "physical"],
            "warrior": ["physical", "work"],
            "architect": ["work", "mental"],
            "polymath": ["work", "mental", "social"],
            "healer": ["social", "mental"]
        }
        
        target_domains = IDENTITY_DOMAIN_MAP.get((user.archetype or user.identity_goal or "monk").lower(), ["mental"])
        target_keywords = IDENTITY_WEIGHTS.get(user.identity_goal, [])

        score = 0
        total = len(completions)
        
        if total == 0:
            return {"score": 0, "status": "Inactive", "total_completions": 0}

        for log_id, habit_name, habit_domain in completions:
            # Match by domain OR keyword
            if habit_domain in target_domains or any(cat.lower() in habit_name.lower() for cat in target_keywords):
                score += 1

        pulse_percentage = (score / total) * 100
        
        return {
            "score": int(pulse_percentage),
            "goal": user.identity_goal or user.archetype,
            "total_completions": total,
            "status": "Aligned" if pulse_percentage > 70 else "Wandering"
        }

