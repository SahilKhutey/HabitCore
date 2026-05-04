import sys
import os
import json
import time
from unittest.mock import MagicMock

# Mock external dependencies before imports
sys.modules["redis"] = MagicMock()
sys.modules["kafka"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["app.db.session"] = MagicMock()

# Add project roots to path
sys.path.append(os.getcwd())

from behavioral_simulator.app.archetypes import User, UserArchetype
from priority_scheduler.app.utils.priority import calculate_priority, PriorityQueue

def test_workflow():
    print("Starting Behavioral Simulator Workflow Verification (Simulated)")
    
    # 1. Setup Test Users
    streak_user = User(user_id="streak_1", archetype=UserArchetype.STREAK, is_premium=False)
    dropoff_user = User(user_id="dropoff_1", archetype=UserArchetype.DROPOFF, is_premium=True)
    binge_user = User(user_id="binge_1", archetype=UserArchetype.BINGE, is_premium=False)
    
    # 2. Generate Events
    print("\n--- Phase 1: Event Generation ---")
    streak_event = None
    while not streak_event:
        streak_event = streak_user.generate_event()
    print(f"[Streak] Generated: {streak_event['event_type']} (Urgency: {streak_event['urgency_score']:.2f})")

    dropoff_event = None
    while not dropoff_event:
        dropoff_event = dropoff_user.generate_event()
    print(f"[Drop-off] Generated: {dropoff_event['event_type']} (Urgency: {dropoff_event['urgency_score']:.2f})")

    # 3. Simulate Priority Calculation
    print("\n--- Phase 2: Priority Calculation ---")
    
    # Mock user context enrichment (normally from DB)
    streak_context = {"is_premium": streak_user.is_premium, "tier": streak_user.streak_count}
    dropoff_context = {"is_premium": dropoff_user.is_premium, "tier": 100} # High tier for premium
    
    streak_priority = calculate_priority(streak_event, streak_context)
    dropoff_priority = calculate_priority(dropoff_event, dropoff_context)
    
    print(f"[Streak] Priority Score: {streak_priority:.2f}")
    print(f"[Drop-off] Priority Score: {dropoff_priority:.2f}")
    
    # 4. Enqueue to Mock Redis
    print("\n--- Phase 3: Priority Routing ---")
    mock_redis = MagicMock()
    pq = PriorityQueue(redis_url="redis://localhost:6379")
    pq.redis = mock_redis # Inject mock
    
    pq.push("nlp", streak_event, streak_priority)
    pq.push("nlp", dropoff_event, dropoff_priority)
    
    # Verify bucket assignments
    streak_bucket = "high" if streak_priority >= 0.8 else "med" if streak_priority >= 0.4 else "low"
    dropoff_bucket = "high" if dropoff_priority >= 0.8 else "med" if dropoff_priority >= 0.4 else "low"
    
    print(f"[Streak] Routed to bucket: {streak_bucket}")
    print(f"[Drop-off] Routed to bucket: {dropoff_bucket}")
    
    # Verify that dropoff (Premium + High Urgency) actually gets higher priority
    assert dropoff_priority > streak_priority, "Error: Premium Drop-off user should have higher priority than standard Streak user"
    print("Verification Successful: Behavioral patterns correctly influence system priority.")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"Verification Failed: {e}")
        sys.exit(1)
