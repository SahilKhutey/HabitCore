import unittest
from unittest.mock import MagicMock, patch
import json
import time

# Mock dependencies
import sys
from types import ModuleType

# Create a mock Redis module
redis_mock = ModuleType('redis')
redis_mock.from_url = MagicMock()
sys.modules['redis'] = redis_mock

# Create a mock Kafka module
kafka_mock = ModuleType('kafka')
kafka_mock.KafkaConsumer = MagicMock()
sys.modules['kafka'] = kafka_mock

from priority_scheduler.app.utils.priority import PriorityQueue, calculate_priority
from priority_scheduler.main import get_user_context

class TestPriorityIntegrationSim(unittest.TestCase):
    @patch('priority_scheduler.app.utils.priority.redis.from_url')
    @patch('priority_scheduler.main.SessionLocal')
    def test_end_to_end_routing(self, mock_session, mock_redis_url):
        # 1. Setup Mock Redis
        mock_redis_client = MagicMock()
        mock_redis_url.return_value = mock_redis_client
        
        # 2. Setup Mock DB
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_user = MagicMock()
        mock_user.is_premium = True
        mock_user.level = 10
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # 3. Setup PQ
        pq = PriorityQueue(redis_url="redis://localhost:6379")
        
        # 4. Simulate Event
        event = {
            "user_id": "user_123",
            "event_type": "avoidance",
            "timestamp": time.time()
        }
        
        # 5. Get Context (Simulated main loop step)
        user_context = get_user_context("user_123")
        self.assertTrue(user_context["is_premium"])
        
        # 6. Calculate Priority
        priority = calculate_priority(event, user_context)
        # Premium(0.4*1.0) + Urgency Avoidance(0.4*1.0) + Lag(~0.2*0.0) = ~0.8
        self.assertGreaterEqual(priority, 0.8)
        
        # 7. Push to PQ
        pq.push("nlp", event, priority)
        
        # 8. Verify Redis Call
        # Should call zadd for the 'high' bucket
        self.assertTrue(mock_redis_client.zadd.called)
        args, kwargs = mock_redis_client.zadd.call_args
        key = args[0]
        self.assertIn("high", key)

if __name__ == '__main__':
    unittest.main()
