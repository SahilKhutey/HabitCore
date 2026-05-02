from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_user_text_event(user_id: str, text: str):
    """
    Asynchronously sends user reflection text to Kafka for processing.
    """
    try:
        producer.send("user_text_events", {
            "user_id": user_id,
            "text": text
        })
        producer.flush()
        logger.info(f"Sent user_text_event for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send Kafka event: {e}")
