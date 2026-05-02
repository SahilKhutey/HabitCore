"""
HabitCore Flink Job — Real-time Pattern Detection.
Processes Kafka 'events_raw' stream to detect behavioral loops.
"""
import json
from pyflink.datastream import StreamExecutionEnvironment, KeyedProcessFunction, RuntimeContext
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time
from pyflink.common.state import ValueStateDescriptor

def setup_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # 1. Kafka Source
    kafka_props = {'bootstrap.servers': 'localhost:9092', 'group.id': 'flink-patterns-group'}
    consumer = FlinkKafkaConsumer(
        topics='behavioral_events', # Consuming from our behavioral stream
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    stream = env.add_source(consumer)
    
    # 2. Parse & Key by User
    def parse_event(value):
        try:
            return json.loads(value)
        except:
            return None
            
    parsed_stream = stream.map(parse_event).filter(lambda x: x is not None)
    keyed_stream = parsed_stream.key_by(lambda x: x["user_id"])
    
    # --- PATTERN A: Rolling Distraction (Stateless Window) ---
    def aggregate_distraction(events):
        total = sum(e.get("event_value", 0) for e in events if "distraction" in e["event_type"])
        return total

    windowed_distraction = keyed_stream \
        .window(TumblingProcessingTimeWindows.of(Time.minutes(10))) \
        .apply(lambda key, window, events: {
            "user_id": key,
            "distraction_score": aggregate_distraction(events),
            "window_end": window.end
        })

    def detect_high_distraction(data):
        if data["distraction_score"] > 2.0: # Threshold for high activity
            return {
                "user_id": data["user_id"],
                "pattern_type": "high_distraction_spike",
                "confidence": 0.8,
                "metadata": {"score": data["distraction_score"]}
            }
        return None
        
    pattern_spikes = windowed_distraction.map(detect_high_distraction).filter(lambda x: x is not None)

    # --- PATTERN B: Avoidance Cycle (Stateful) ---
    class AvoidanceCycleDetector(KeyedProcessFunction):
        def open(self, runtime_context: RuntimeContext):
            # Track consecutive avoidance signals
            self.avoidance_count = runtime_context.get_state(
                ValueStateDescriptor("avoidance_count", int)
            )

        def process_element(self, value, ctx):
            count = self.avoidance_count.value() or 0
            
            if "avoidance" in value["event_type"]:
                count += 1
            else:
                # Reset on positive behavior
                if "deep_work" in value["event_type"]:
                    count = 0
            
            self.avoidance_count.update(count)
            
            if count >= 3: # 3 consecutive avoidance signals
                yield {
                    "user_id": value["user_id"],
                    "pattern_type": "active_avoidance_cycle",
                    "confidence": 0.9,
                    "metadata": {"consecutive_count": count}
                }

    avoidance_patterns = keyed_stream.process(AvoidanceCycleDetector())

    # --- PATTERN C: Burnout Warning ---
    # (Low energy + high distraction over 10m)
    # This would require joining streams or a more complex state, 
    # but we can combine them in the sink or a final map.

    # 3. Union & Sink to Kafka
    combined_patterns = pattern_spikes.union(avoidance_patterns)
    
    producer = FlinkKafkaProducer(
        topic='patterns_stream',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'localhost:9092'}
    )
    
    combined_patterns.map(lambda x: json.dumps(x)).add_sink(producer)
    
    env.execute("HabitCore Real-time Pattern Engine")

if __name__ == "__main__":
    setup_flink_job()
