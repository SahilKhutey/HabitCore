from functools import lru_cache
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .ai_coach_service import AICoachService

class CachedAICoachService:
    def __init__(self, behavior_service):
        self.ai_coach = AICoachService(behavior_service)
        # Simple in-memory cache for demo/MVP
        self._cache = {}
    
    def get_advice(self, user_id: str, context: Dict[str, Any]) -> str:
        """Get cached advice or generate new one"""
        # Create a simple hash of the context
        context_key = f"{context.get('current_streak', 0)}_{context.get('recent_failures', 0)}"
        cache_key = f"{user_id}_{context_key}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            # Check if fresh (6 hours)
            if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
                return cached_data['advice']
        
        # Generate new advice
        advice = self.ai_coach.generate_personalized_advice(user_id, context)
        
        # Save to cache
        self._cache[cache_key] = {
            'advice': advice,
            'timestamp': datetime.now()
        }
        
        return advice

    def invalidate_cache(self, user_id: str):
        """Invalidate cache for specific user"""
        keys_to_remove = [k for k in self._cache if k.startswith(f"{user_id}_")]
        for k in keys_to_remove:
            del self._cache[k]
