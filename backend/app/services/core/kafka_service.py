import json
import logging
import time
from kafka import KafkaProducer
from typing import Dict, Any, Optional

from app.core.config import settings
from app.utils.priority import PriorityQueue, calculate_priority

logger = logging.getLogger(__name__)

# Initialize PriorityQueue for nudge engine bridge
try:
    pq = PriorityQueue(redis_url=settings.REDIS_URL if hasattr(settings, "REDIS_URL") else "redis://localhost:6379")
except Exception as e:
    logger.error(f"Failed to initialize PriorityQueue: {e}")
    pq = None

class KafkaService:
    _producer: Optional[KafkaProducer] = None

    @classmethod
    def get_producer(cls) -> Optional[KafkaProducer]:
        """Singleton pattern for Kafka producer."""
        if cls._producer is None:
            try:
                # In a real environment, we'd use settings.KAFKA_BOOTSTRAP_SERVERS
                cls._producer = KafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    request_timeout_ms=1000  # Fail fast to avoid blocking the main thread
                )
                logger.info("Kafka producer initialized successfully.")
            except Exception as e:
                # Silent failure for producer, we will use the Redis bridge
                cls._producer = False # Mark as failed
                return None
        return cls._producer if cls._producer is not False else None

    @classmethod
    def send_event(cls, topic: str, data: Dict[str, Any]):
        """Asynchronously sends an event to a Kafka topic and bridges to Redis PQ if needed."""
        # 1. Try Kafka
        producer = cls.get_producer()
        if producer:
            try:
                producer.send(topic, data)
                logger.info(f"Event sent to Kafka topic {topic}")
            except Exception as e:
                logger.error(f"Failed to send Kafka event: {e}")
        
        # 2. Bridge to Redis PriorityQueue for Nudge Engine
        if pq and topic == "behavioral_events":
            try:
                # Calculate priority using the utility
                priority = calculate_priority(data, data.get("context", {}))
                pq.push("nudge", data, priority)
                logger.info(f"Event bridged to Redis PriorityQueue for {data.get('user_id')}")
            except Exception as e:
                logger.error(f"Failed to bridge event to Redis: {e}")

    @classmethod
    def send_user_text_event(cls, user_id: str, text: str):
        """Sends user reflection text for NLP processing."""
        cls.send_event("user_text_events", {
            "user_id": user_id,
            "text": text,
            "timestamp": time.time()
        })

    @classmethod
    def send_behavioral_event(cls, user_id: str, event_type: str, value: float = 1.0, metadata: Dict[str, Any] = None):
        """Sends behavioral events for real-time pattern detection."""
        cls.send_event("behavioral_events", {
            "user_id": user_id,
            "event_type": event_type,
            "event_value": value,
            "metadata": metadata or {},
            "timestamp": time.time()
        })
