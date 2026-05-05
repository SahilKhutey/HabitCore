"""
Behavioral Context Manager — Real-time state management using Redis.
"""
import redis
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ContextManager:
    def __init__(self, host="localhost", port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl_context = 3600 # 1 hour
        self.ttl_cooldown = 1800 # 30 mins
        self.ttl_metrics = 3600

    def update_event_context(self, user_id: str, event_type: str, value: float = 1.0):
        """Updates the sliding-window metrics and general context in Redis."""
        try:
            # 1. Update Metrics (Hashes)
            metrics_key = f"user:{user_id}:metrics"
            if "distraction" in event_type:
                self.r.hincrby(metrics_key, "distraction_count", 1)
                self.r.hset(metrics_key, "last_distraction_at", str(json.dumps(True)))
            elif "deep_work" in event_type:
                self.r.hincrby(metrics_key, "deep_work_mins", int(value))
                
            self.r.expire(metrics_key, self.ttl_metrics)
            
            # 2. Update General State (JSON)
            state_key = f"user:{user_id}:state"
            state = {
                "last_event": event_type,
                "active_session": True
            }
            self.r.set(state_key, json.dumps(state), ex=self.ttl_context)
            
            # 3. Update Behavior Flags
            self.recompute_flags(user_id)
            
        except Exception as e:
            logger.error(f"Redis update failed for {user_id}: {e}")

    def recompute_flags(self, user_id: str):
        """Calculates fast boolean signals for the nudge engine."""
        metrics = self.r.hgetall(f"user:{user_id}:metrics")
        distractions = int(metrics.get("distraction_count", 0))
        
        flags = {
            "high_distraction": distractions > 3,
            "low_focus": distractions > 5
        }
        self.r.set(f"user:{user_id}:flags", json.dumps(flags), ex=600) # 10 min flags

    def get_full_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieves all real-time behavioral signals for a user."""
        try:
            state = self.r.get(f"user:{user_id}:state")
            metrics = self.r.hgetall(f"user:{user_id}:metrics")
            flags = self.r.get(f"user:{user_id}:flags")
            
            return {
                "state": json.loads(state) if state else {},
                "metrics": metrics,
                "flags": json.loads(flags) if flags else {},
                "is_on_cooldown": self.r.exists(f"user:{user_id}:nudge_cooldown")
            }
        except Exception as e:
            logger.error(f"Redis read failed for {user_id}: {e}")
            return {}

    def set_nudge_cooldown(self, user_id: str):
        """Enforces a cooldown period between nudges."""
        self.r.set(f"user:{user_id}:nudge_cooldown", "active", ex=self.ttl_cooldown)

    def is_active(self, user_id: str) -> bool:
        """Checks if the user has been active in the last 15 minutes."""
        return self.r.exists(f"user:{user_id}:state")

    def publish_nudge(self, user_id: str, message: str, nudge_type: str = "reminder"):
        """Publishes a nudge to the user's specific channel for SSE delivery."""
        try:
            channel = f"nudges:{user_id}"
            data = json.dumps({
                "message": message,
                "type": nudge_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.r.publish(channel, data)
            logger.info(f"Nudge published to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish nudge to {user_id}: {e}")
