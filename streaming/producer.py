from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers='localhost:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=1000 # Short timeout for fail-fast
            )
        except Exception as e:
            logger.error(f"Kafka connection failed: {e}")
            return None
    return _producer

def send_user_text_event(user_id: str, text: str):
    """
    Asynchronously sends user reflection text to Kafka for processing.
    """
    prod = get_producer()
    if not prod:
        logger.warning("Kafka producer unavailable. Skipping event.")
        return

    try:
        prod.send("user_text_events", {
            "user_id": user_id,
            "text": text
        })
        # Note: In production, avoid flush() here for better throughput
        # prod.flush() 
        logger.info(f"Sent user_text_event for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send Kafka event: {e}")
