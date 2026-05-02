"""
Ingestion Layer — Redis-based event queue.
"""
from redis import Redis
import json
import logging

logger = logging.getLogger(__name__)

try:
    # Default to localhost Redis
    redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available for ingestion queue: {e}")
    redis_client = None

def push_event(event: dict):
    """Pushes a raw event to the queue."""
    if redis_client:
        try:
            redis_client.lpush("event_queue", json.dumps(event))
        except Exception as e:
            logger.error(f"Failed to push event to Redis: {e}")
    else:
        # Fallback to direct processing or memory queue if needed
        pass

def pop_event() -> dict:
    """Pops an event from the queue."""
    if redis_client:
        try:
            data = redis_client.rpop("event_queue")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to pop event from Redis: {e}")
    return None
