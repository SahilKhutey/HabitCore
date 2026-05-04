import json
import logging
import time
import os
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.utils.priority import PriorityQueue, calculate_priority

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("priority_scheduler")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize PQ
pq = PriorityQueue(redis_url=REDIS_URL)

def get_user_context(user_id: str) -> dict:
    """Fetch minimal user context for priority calculation."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "is_premium": user.is_premium,
                "tier": user.level  # Using level as a proxy for tier for now
            }
        return {}
    finally:
        db.close()

def main():
    consumer = KafkaConsumer(
        "patterns_stream",
        "user_text_events",
        "behavioral_events",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id="priority_scheduler_group",
        auto_offset_reset="latest"
    )

    logger.info(f"Priority Scheduler started. Listening on {KAFKA_BOOTSTRAP_SERVERS}...")

    for message in consumer:
        try:
            event = message.value
            topic = message.topic
            user_id = event.get("user_id")
            
            if not user_id:
                logger.warning(f"Event missing user_id: {event}")
                continue

            # 1. Enrich with User Context
            user_context = get_user_context(user_id)
            
            # 2. Calculate Priority
            priority = calculate_priority(event, user_context)
            
            # 3. Route to Priority Queue
            if topic == "user_text_events":
                pq.push("nlp", event, priority)
                logger.info(f"Enqueued to NLP PQ: user={user_id}, priority={priority:.2f}")
            elif topic == "patterns_stream":
                pq.push("nudge", event, priority)
                logger.info(f"Enqueued to Nudge PQ: user={user_id}, priority={priority:.2f}")
            elif topic == "behavioral_events":
                # Route specific behavioral events that need NLP/Processing
                if event.get("event_type") == "daily_log_ingested":
                    pq.push("nlp", event, priority)
                    logger.info(f"Enqueued Log for Analysis: user={user_id}, priority={priority:.2f}")
                else:
                    # General behavioral events might just go to nudge or patterns
                    pq.push("nudge", event, priority)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

if __name__ == "__main__":
    main()
