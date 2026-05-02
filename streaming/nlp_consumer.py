import sys
import os
import json
from kafka import KafkaConsumer, KafkaProducer

# Ensure app imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nlp_service')))
from app.pipeline import process_text

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

print("NLP Consumer starting...")
for msg in consumer:
    data = msg.value
    print(f"Processing text for user {data['user_id']}...")
    
    # Process using the NLP microservice pipeline
    result = process_text(data["user_id"], data["text"])
    
    # Send signals downstream
    producer.send("cognitive_signals", result)
    producer.flush()
