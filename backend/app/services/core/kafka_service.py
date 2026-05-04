import json
import logging
from kafka import KafkaProducer
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

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
                logger.error(f"Kafka connection failed: {e}")
                return None
        return cls._producer

    @classmethod
    def send_event(cls, topic: str, data: Dict[str, Any]):
        """Asynchronously sends an event to a Kafka topic."""
        producer = cls.get_producer()
        if not producer:
            logger.warning(f"Kafka producer unavailable. Skipping event for topic: {topic}")
            return

        try:
            producer.send(topic, data)
            # In high-throughput systems, we don't call flush() here.
            # The producer handles batching and background delivery.
            logger.info(f"Event sent to topic {topic}")
        except Exception as e:
            logger.error(f"Failed to send Kafka event: {e}")

    @classmethod
    def send_user_text_event(cls, user_id: str, text: str):
        """Sends user reflection text for NLP processing."""
        cls.send_event("user_text_events", {
            "user_id": user_id,
            "text": text
        })

    @classmethod
    def send_behavioral_event(cls, user_id: str, event_type: str, value: float = 1.0, metadata: Dict[str, Any] = None):
        """Sends behavioral events for real-time pattern detection (Flink/Nudge Engine)."""
        cls.send_event("behavioral_events", {
            "user_id": user_id,
            "event_type": event_type,
            "event_value": value,
            "metadata": metadata or {}
        })
