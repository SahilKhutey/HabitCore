import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..services.behavior_memory_service import BehaviorMemoryService
from ..core.state_engine import user_state_engine

class PatternWorker:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.behavior_service = BehaviorMemoryService(db_session)
    
    async def process_user_patterns_async(self, user_id: str):
        """Async pattern processing for better performance"""
        loop = asyncio.get_event_loop()
        
        # Run CPU-intensive analysis in thread pool
        patterns = await loop.run_in_executor(
            self.executor, 
            self._compute_all_patterns, 
            user_id
        )
        
        # Determine state
        user_data = self._get_user_summary(user_id)
        user_state = user_state_engine.determine_user_mode(user_data)
        
        return patterns, user_state
    
    def _compute_all_patterns(self, user_id: str):
        """Wrapper for service calls"""
        self.behavior_service.analyze_time_patterns(user_id)
        self.behavior_service.analyze_day_patterns(user_id)
        return self.behavior_service.get_user_patterns(user_id)
    
    def _get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Collect metrics for state engine"""
        burnout = self.behavior_service.calculate_burnout_score(user_id)
        # Mocking some data that would come from a comprehensive analytics service
        return {
            'current_streak': 7,
            'completion_rate': 0.85,
            'session_frequency': 5,
            'recent_activity': 8,
            'burnout_score': burnout
        }
