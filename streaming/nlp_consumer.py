import json
import logging
from kafka import KafkaConsumer, KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nlp_consumer")

try:
    from app.pipeline import process_text
except ImportError:
    # Fallback for local development if not installed as module
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nlp_service')))
    from app.pipeline import process_text

def start_consumer():
    try:
        consumer = KafkaConsumer(
            "user_text_events",
            bootstrap_servers="localhost:9092",
            group_id="nlp-processor-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        logger.info("NLP Consumer starting...")
        for msg in consumer:
            try:
                data = msg.value
                logger.info(f"Processing text for user {data.get('user_id')}...")
                
                # Process using the NLP microservice pipeline
                result = process_text(data["user_id"], data["text"])
                
                # Send signals downstream
                producer.send("cognitive_signals", result)
                producer.flush()
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    except Exception as e:
        logger.error(f"Critical consumer error: {e}")

if __name__ == "__main__":
    start_consumer()
