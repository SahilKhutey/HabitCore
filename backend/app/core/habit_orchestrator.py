from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import hashlib
from sqlalchemy.orm import Session

from ..services.psychological_service import psychological_service
from ..services.advanced_reward_service import AdvancedRewardService
from ..services.recovery_service import recovery_service
from ..services.cached_ai_service import CachedAICoachService
from ..services.behavior_memory_service import BehaviorMemoryService
from ..services.advanced_gamification import gamification_service
from ..services.avatar_service import AvatarService
from ..core.state_engine import user_state_engine, UserMode
from ..core.security import security_engine
from ..utils.logging import structured_logger

class HabitOrchestrator:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.behavior_service = BehaviorMemoryService(db_session)
        self.ai_service = CachedAICoachService(self.behavior_service)
        self.reward_service = AdvancedRewardService()
        self.avatar_service = AvatarService(db_session)
        self.logger = structured_logger
        
    async def process_habit_completion(self, user_id: str, habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MASTER PIPELINE - Orchestrates the entire habit completion flow
        """
        try:
            # 1. 🔐 Security Validation
            if not security_engine.validate_event(user_id, "habit_completed", habit_data):
                self.logger.warning("Security validation failed", user_id=user_id)
                return {"success": False, "error": "Invalid event or rate limit exceeded"}
            
            # 2. 📊 Parallel Processing: Start async tasks
            reward_task = asyncio.create_task(self._calculate_rewards(user_id, habit_data))
            behavior_task = asyncio.create_task(self._log_behavior(user_id, habit_data))
            state_task = asyncio.create_task(self._update_user_state(user_id))
            
            # 3. 🎯 Wait for core computations
            rewards, behavior_log, user_state = await asyncio.gather(
                reward_task, behavior_task, state_task
            )

            # 4. 🧬 Avatar Progression
            avatar_update = await self._update_avatar(user_id, rewards["total_xp"], habit_data)
            
            # 4. 🧠 AI Coaching (cached)
            ai_advice = await self._get_ai_advice(user_id, user_state)
            
            # 5. 🧯 Recovery Check
            recovery_plan = await self._check_recovery_needed(user_id, user_state)
            
            # 6. 🎁 Gamification Elements
            gamification = await self._get_gamification_elements(user_id, habit_data, rewards)
            
            # 7. 📈 Update User Progress (In production, this would hit the DB)
            self.logger.info("Habit completion processed", user_id=user_id, xp_earned=rewards["total_xp"])
            
            return {
                "success": True,
                "rewards": rewards,
                "user_state": user_state,
                "ai_advice": ai_advice,
                "recovery_plan": recovery_plan,
                "gamification": gamification,
                "avatar_update": avatar_update,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error("Orchestration failed", error=str(e), user_id=user_id)
            return {"success": False, "error": f"Processing failed: {str(e)}"}
    
    async def _calculate_rewards(self, user_id: str, habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all rewards for habit completion"""
        # Get base XP from psychological service
        base_xp = psychological_service.calculate_xp_reward(
            habit_data.get("difficulty", "medium"),
            habit_data.get("current_streak", 0)
        )
        
        # Get consistency and calculate multiplier
        consistency = 0.8 # Mocked for now
        total_xp = self.reward_service.calculate_xp_with_consistency(
            base_xp, 
            habit_data.get("current_streak", 0),
            habit_data.get("difficulty", "medium"),
            consistency
        )
        
        variable_bonus = self.reward_service.get_variable_reward("small")
        
        return {
            "base_xp": base_xp,
            "variable_bonus": variable_bonus,
            "total_xp": total_xp + variable_bonus,
            "coins": (total_xp + variable_bonus) // 2
        }
    
    async def _log_behavior(self, user_id: str, habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log behavior and return context"""
        context = {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().strftime("%A"),
            "device": "mobile"
        }
        
        self.behavior_service.log_behavior(
            user_id,
            "habit_completed",
            habit_data,
            context
        )
        
        return {"logged": True, "context": context}
    
    async def _update_user_state(self, user_id: str) -> Dict[str, Any]:
        """Update and return current user state"""
        burnout_score = self.behavior_service.calculate_burnout_score(user_id)
        
        # Summary data for state engine
        user_data = {
            "current_streak": 7,
            "completion_rate": 0.85,
            "session_frequency": 5,
            "recent_activity": 8,
            "burnout_score": burnout_score
        }
        
        user_mode = user_state_engine.determine_user_mode(user_data)
        state_actions = user_state_engine.get_state_based_actions(user_mode)
        
        return {
            "mode": user_mode,
            "actions": state_actions,
            "burnout_score": burnout_score,
            "engagement_score": user_state_engine.calculate_engagement_score(user_data)
        }
    
    async def _get_ai_advice(self, user_id: str, user_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI advice with caching"""
        context = {
            "current_streak": 7, # Would come from state
            "recent_failures": 1
        }
        advice = self.ai_service.get_advice(user_id, context)
        
        return {
            "message": advice,
            "freshness": "cached"
        }
    
    async def _check_recovery_needed(self, user_id: str, user_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if recovery plan is needed"""
        if user_state["burnout_score"] > 0.7:
            return recovery_service.generate_recovery_plan(
                "burnout",
                user_state["burnout_score"]
            )
        return None
    
    async def _get_gamification_elements(self, user_id: str, habit_data: Dict[str, Any], rewards: Dict[str, Any]) -> Dict[str, Any]:
        """Get gamification elements"""
        streak = habit_data.get("current_streak", 0)
        
        mystery_reward = None
        if streak > 0 and streak % 5 == 0:
            mystery_reward = gamification_service.generate_mystery_reward()
        
        # Anticipation for next milestone
        user_progress = {"xp": 350} # Mocked
        anticipation = gamification_service.create_anticipation_loop(user_progress)
        
        return {
            "mystery_reward": mystery_reward,
            "anticipation_loop": anticipation,
            "current_streak": streak
        }

    async def _update_avatar(self, user_id: str, xp_earned: int, habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update avatar and return delta for UI celebrations"""
        try:
            # Prepare context for archetype and evolution check
            # In a real app, we'd fetch actual category distribution from DB
            habit_data['category_distribution'] = {habit_data.get('category', 'general'): 1.0}
            habit_data['consistency_score'] = 0.8
            
            avatar = self.avatar_service.update_avatar_progress(user_id, xp_earned, habit_data)
            
            return {
                "level": avatar.level,
                "evolution_stage": avatar.evolution_stage,
                "archetype": avatar.archetype
            }
        except Exception as e:
            self.logger.error("Avatar update failed", error=str(e), user_id=user_id)
            return {}

# Factory function for dependency injection
def get_habit_orchestrator(db_session: Session):
    return HabitOrchestrator(db_session)
