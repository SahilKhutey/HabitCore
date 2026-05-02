"""
HabitCore Flink Job — Real-time Pattern Detection (Docker Edition).
Uses internal 'kafka:9092' address.
"""
import json
import os
from pyflink.datastream import StreamExecutionEnvironment, KeyedProcessFunction, RuntimeContext
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time
from pyflink.common.state import ValueStateDescriptor

def setup_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    kafka_broker = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    print(f"Connecting to Kafka at {kafka_broker}...")
    
    # 1. Kafka Source
    kafka_props = {'bootstrap.servers': kafka_broker, 'group.id': 'flink-patterns-group'}
    consumer = FlinkKafkaConsumer(
        topics='behavioral_events',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    stream = env.add_source(consumer)
    
    # 2. Processing logic
    def parse_event(value):
        try:
            return json.loads(value)
        except:
            return None
            
    parsed_stream = stream.map(parse_event).filter(lambda x: x is not None)
    keyed_stream = parsed_stream.key_by(lambda x: x["user_id"])
    
    # --- Pattern: High Distraction ---
    def aggregate_distraction(events):
        return sum(e.get("event_value", 0) for e in events if "distraction" in e["event_type"])

    windowed_distraction = keyed_stream \
        .window(TumblingProcessingTimeWindows.of(Time.minutes(10))) \
        .apply(lambda key, window, events: {
            "user_id": key,
            "distraction_score": aggregate_distraction(events)
        })

    def detect_high_distraction(data):
        if data["distraction_score"] > 2.0:
            return {
                "user_id": data["user_id"],
                "pattern_type": "high_distraction_spike",
                "confidence": 0.8
            }
        return None
        
    pattern_spikes = windowed_distraction.map(detect_high_distraction).filter(lambda x: x is not None)

    # --- Pattern: Avoidance Cycle (Stateful) ---
    class AvoidanceCycleDetector(KeyedProcessFunction):
        def open(self, runtime_context: RuntimeContext):
            self.avoidance_count = runtime_context.get_state(
                ValueStateDescriptor("avoidance_count", int)
            )

        def process_element(self, value, ctx):
            count = self.avoidance_count.value() or 0
            if "avoidance" in value["event_type"]:
                count += 1
            elif "deep_work" in value["event_type"]:
                count = 0
            self.avoidance_count.update(count)
            if count >= 3:
                yield {
                    "user_id": value["user_id"],
                    "pattern_type": "active_avoidance_cycle",
                    "confidence": 0.9
                }

    avoidance_patterns = keyed_stream.process(AvoidanceCycleDetector())
    combined_patterns = pattern_spikes.union(avoidance_patterns)
    
    # 3. Sink back to Kafka
    producer = FlinkKafkaProducer(
        topic='patterns_stream',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': kafka_broker}
    )
    
    combined_patterns.map(lambda x: json.dumps(x)).add_sink(producer)
    
    env.execute("HabitCore Real-time Pattern Engine")

if __name__ == "__main__":
    setup_flink_job()
