from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer(
    "cognitive_signals",
    bootstrap_servers="localhost:9092",
    group_id="signal-processor-group",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Signal Processor Consumer starting...")
for msg in consumer:
    signals = msg.value
    print(f"Extracting events for user {signals['user_id']}...")
    
    events = signals.get("events", [])
    
    for event in events:
        producer.send("behavioral_events", {
            "user_id": signals["user_id"],
            **event
        })
    
    producer.flush()
