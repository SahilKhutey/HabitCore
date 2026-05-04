import json
import logging
import time
import os
from kafka import KafkaProducer
from app.pipeline import process_text
from app.utils.priority import PriorityQueue

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nlp_worker")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize PQ and Producer
pq = PriorityQueue(redis_url=REDIS_URL)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def run_worker():
    logger.info("NLP Priority Worker started. Listening on Redis PQ...")
    
    while True:
        try:
            item = pq.pop("nlp")
            if item:
                data = item["data"]
                user_id = data.get("user_id")
                text_content = data.get("text") or data.get("metadata", {}).get("text")
                priority = item.get("priority", 0.0)
                
                if not user_id or not text_content:
                    logger.warning(f"Invalid item data or missing text: {data}")
                    continue

                logger.info(f"Processing NLP task for user {user_id} (priority={priority:.2f})")
                
                # 1. Process Text
                analysis_result = process_text(user_id, text_content)
                
                # 2. Emit behavioral events to Kafka
                for event in analysis_result.get("events", []):
                    payload = {
                        "user_id": user_id,
                        "event_type": event["event_type"],
                        "event_value": event.get("event_value", 1),
                        "timestamp": time.time(),
                        "metadata": {
                            "source": "nlp_worker",
                            "original_priority": priority,
                            "emotion": analysis_result.get("emotion")
                        }
                    }
                    producer.send("behavioral_events", payload)
                
                producer.flush()
                logger.info(f"Successfully processed NLP and emitted {len(analysis_result.get('events', []))} events")

            else:
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in NLP Worker loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    run_worker()
