import pytest
from unittest.mock import MagicMock, patch
from app.services.core.kafka_service import KafkaService

def test_kafka_service_singleton():
    """Verify that KafkaService returns the same producer instance."""
    with patch('app.services.core.kafka_service.KafkaProducer') as mock_producer:
        p1 = KafkaService.get_producer()
        p2 = KafkaService.get_producer()
        assert p1 == p2
        assert mock_producer.call_count == 1

def test_kafka_service_graceful_failure():
    """Verify that KafkaService doesn't raise exceptions if Kafka is down."""
    with patch('app.services.core.kafka_service.KafkaProducer', side_effect=Exception("Connection refused")):
        # Should not raise exception
        KafkaService._producer = None # Reset singleton
        producer = KafkaService.get_producer()
        assert producer is None
        
        # Should log and continue
        KafkaService.send_event("test_topic", {"data": "test"})

def test_kafka_message_format():
    """Verify that behavioral events are formatted correctly."""
    with patch('app.services.core.kafka_service.KafkaProducer') as mock_producer:
        KafkaService._producer = MagicMock()
        KafkaService.send_behavioral_event(
            user_id="user_123",
            event_type="habit_completed",
            value=1.5,
            metadata={"test": True}
        )
        
        KafkaService._producer.send.assert_called_once()
        args, _ = KafkaService._producer.send.call_args
        assert args[0] == "behavioral_events"
        assert args[1]["user_id"] == "user_123"
        assert args[1]["event_type"] == "habit_completed"
        assert args[1]["event_value"] == 1.5
        assert args[1]["metadata"]["test"] is True
