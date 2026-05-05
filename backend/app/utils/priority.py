import redis
import json
import time
import random
from typing import Dict, Any, Optional, List

class PriorityQueue:
    """
    Redis-based Priority Queue using ZSETs.
    Supports High, Medium, and Low buckets with weighted selection.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", prefix: str = "pq"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = prefix
        self.buckets = ["high", "med", "low"]
        
    def _get_key(self, queue_name: str, bucket: str) -> str:
        return f"{self.prefix}:{queue_name}:{bucket}"

    def push(self, queue_name: str, data: Dict[str, Any], priority_score: float):
        """
        Push data into the appropriate bucket based on priority_score (0.0 to 1.0).
        High: 0.8 - 1.0
        Med:  0.4 - 0.79
        Low:  0.0 - 0.39
        """
        if priority_score >= 0.8:
            bucket = "high"
        elif priority_score >= 0.4:
            bucket = "med"
        else:
            bucket = "low"
            
        key = self._get_key(queue_name, bucket)
        
        # Use timestamp as score for ZSET to maintain FIFO within buckets
        # but store the calculated priority in the payload for reference
        payload = {
            "data": data,
            "priority": priority_score,
            "enqueued_at": time.time()
        }
        
        self.redis.zadd(key, {json.dumps(payload): time.time()})

    def pop(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Pop the next item using weighted fair scheduling (60/30/10).
        """
        r = random.random()
        
        if r < 0.6:
            order = ["high", "med", "low"]
        elif r < 0.9:
            order = ["med", "high", "low"]
        else:
            order = ["low", "high", "med"]
            
        for bucket in order:
            key = self._get_key(queue_name, bucket)
            
            # Weighted selection using ZPOPMIN with a manual fallback for Redis < 5.0
            try:
                item = self.redis.zpopmin(key)
            except Exception as e:
                # Manual ZPOPMIN implementation (Fetch + Remove)
                # Note: This is not atomic without a Lua script, but acceptable for this demo
                res = self.redis.zrange(key, 0, 0, withscores=True)
                if res:
                    self.redis.zrem(key, res[0][0])
                    item = res
                else:
                    item = None
            
            if item:
                return json.loads(item[0][0])
                
        return None

    def get_stats(self, queue_name: str) -> Dict[str, int]:
        stats = {}
        for bucket in self.buckets:
            key = self._get_key(queue_name, bucket)
            stats[bucket] = self.redis.zcard(key)
        return stats

def calculate_priority(event: Dict[str, Any], user_context: Dict[str, Any]) -> float:
    """
    Calculate priority score (0.0 - 1.0)
    priority_score = w1*user_tier + w2*urgency + w3*lag
    """
    # Weights
    W_TIER = 0.4
    W_URGENCY = 0.4
    W_LAG = 0.2
    
    # 1. User Tier (Premium = 1.0, Free = 0.5)
    is_premium = user_context.get("is_premium", False)
    tier_score = 1.0 if is_premium else 0.5
    
    # 2. Urgency Signal
    event_type = event.get("event_type", "")
    urgency_map = {
        "avoidance": 1.0,
        "distraction": 0.8,
        "burnout_spike": 0.9,
        "habit_completed": 0.3,
        "checkin": 0.2
    }
    urgency_score = urgency_map.get(event_type, 0.2)
    
    # 3. Lag Penalty (capped at 1.0)
    # If event is older than 5 mins, max lag penalty
    event_ts = event.get("timestamp", time.time())
    lag_seconds = time.time() - event_ts
    lag_score = min(1.0, lag_seconds / 300.0)
    
    total_score = (W_TIER * tier_score) + (W_URGENCY * urgency_score) + (W_LAG * lag_score)
    return min(1.0, total_score)
