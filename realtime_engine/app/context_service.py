from app.redis_client import redis_client
import time
import json

def update_user_context(user_id: str, event_type: str, value: float):
    key = f"user:{user_id}:realtime"
    window_key = f"user:{user_id}:history:1h"

    # 1. Update Counters (Rolling Aggregates)
    if event_type == "deep_work":
        redis_client.hincrbyfloat(key, "focus_score", value)
    elif event_type == "scrolling":
        redis_client.hincrby(key, "distraction_minutes", int(value))

    # 2. Add to Sliding Window (Sorted Set for time-based queries)
    now = time.time()
    event_data = json.dumps({"type": event_type, "val": value, "ts": now})
    redis_client.zadd(window_key, {event_data: now})
    
    # 3. Clean up old window data (> 1 hour)
    redis_client.zremrangebyscore(window_key, 0, now - 3600)

    # 4. Store last event & set behavior decay
    redis_client.hset(key, "last_event", event_type)
    redis_client.expire(key, 86400)  # Behavior memory lasts 24h
    redis_client.expire(window_key, 3600) # Window lasts 1h


def get_user_context(user_id: str):
    key = f"user:{user_id}:realtime"
    data = redis_client.hgetall(key)

    return {
        "user_id": user_id,
        "focus_score": float(data.get("focus_score", 0)),
        "distraction_minutes": int(data.get("distraction_minutes", 0)),
        "last_event": data.get("last_event", "")
    }

def get_window_metrics(user_id: str):
    """Calculates granular metrics from the 1h sliding window."""
    window_key = f"user:{user_id}:history:1h"
    now = time.time()
    events = redis_client.zrangebyscore(window_key, now - 3600, now)
    
    metrics = {"distraction_events": 0, "focus_events": 0}
    for e in events:
        data = json.loads(e)
        if data["type"] == "scrolling":
            metrics["distraction_events"] += 1
        elif data["type"] == "deep_work":
            metrics["focus_events"] += 1
            
    return metrics
