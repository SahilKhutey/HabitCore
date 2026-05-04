import unittest
from priority_scheduler.app.utils.priority import calculate_priority

class TestPriorityScheduler(unittest.TestCase):
    def test_calculate_priority_premium_user(self):
        event = {"event_type": "checkin", "timestamp": 1625000000}
        user_context = {"is_premium": True}
        priority = calculate_priority(event, user_context)
        # Premium weight (0.4 * 1.0) + Urgency checkin (0.4 * 0.2) + Lag (0.2 * 1.0)
        # 0.4 + 0.08 + 0.2 = 0.68
        self.assertGreaterEqual(priority, 0.4)

    def test_calculate_priority_urgent_event(self):
        event = {"event_type": "avoidance", "timestamp": 1625000000}
        user_context = {"is_premium": False}
        priority = calculate_priority(event, user_context)
        # Non-premium (0.4 * 0.5) + Urgency avoidance (0.4 * 1.0) + Lag (0.2 * 1.0)
        # 0.2 + 0.4 + 0.2 = 0.8
        self.assertEqual(priority, 0.8)

    def test_calculate_priority_low_urgency(self):
        event = {"event_type": "habit_completed", "timestamp": 1625000000}
        user_context = {"is_premium": False}
        priority = calculate_priority(event, user_context)
        # Non-premium (0.4 * 0.5) + Urgency habit (0.4 * 0.3) + Lag (0.2 * 1.0)
        # 0.2 + 0.12 + 0.2 = 0.52
        self.assertLess(priority, 0.8)

if __name__ == '__main__':
    unittest.main()
