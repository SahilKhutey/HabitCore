import redis
import json
import time
import random
from typing import Dict, Any, Optional

class PriorityQueue:
    """
    Redis-based Priority Queue using ZSETs.
    Identical to backend/app/utils/priority.py for service portability.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", prefix: str = "pq"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = prefix
        self.buckets = ["high", "med", "low"]
        
    def _get_key(self, queue_name: str, bucket: str) -> str:
        return f"{self.prefix}:{queue_name}:{bucket}"

    def push(self, queue_name: str, data: Dict[str, Any], priority_score: float):
        if priority_score >= 0.8:
            bucket = "high"
        elif priority_score >= 0.4:
            bucket = "med"
        else:
            bucket = "low"
            
        key = self._get_key(queue_name, bucket)
        payload = {
            "data": data,
            "priority": priority_score,
            "enqueued_at": time.time()
        }
        self.redis.zadd(key, {json.dumps(payload): time.time()})

    def pop(self, queue_name: str) -> Optional[Dict[str, Any]]:
        r = random.random()
        if r < 0.6:
            order = ["high", "med", "low"]
        elif r < 0.9:
            order = ["med", "high", "low"]
        else:
            order = ["low", "high", "med"]
            
        for bucket in order:
            key = self._get_key(queue_name, bucket)
            item = self.redis.zpopmin(key)
            if item:
                return json.loads(item[0][0])
        return None
