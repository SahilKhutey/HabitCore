from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.avatar_models import UserAvatar, AvatarItem, Archetype, EvolutionStage
# Assuming psychological_service is available
from .psychological_service import psychological_service

class AvatarService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def update_avatar_progress(self, user_id: str, xp_earned: int, habit_data: Dict[str, Any]) -> UserAvatar:
        """Update avatar progress after habit completion"""
        avatar = self.get_avatar(user_id)
        
        # Apply XP and level up if needed
        avatar.xp += xp_earned
        avatar.total_xp += xp_earned
        
        # Check for level up
        while avatar.xp >= self._get_xp_for_level(avatar.level):
            avatar.xp -= self._get_xp_for_level(avatar.level)
            avatar.level += 1
            self._handle_level_up(avatar)
        
        # Update archetype based on habit patterns
        self._update_archetype(avatar, habit_data)
        
        # Update evolution progress
        self._update_evolution(avatar)
        
        # Sync with mood if enabled
        if avatar.mood_sync:
            self._sync_with_mood(avatar, habit_data.get('mood'))
        
        avatar.updated_at = datetime.utcnow()
        self.db.commit()
        
        return avatar
    
    def _update_archetype(self, avatar: UserAvatar, habit_data: Dict[str, Any]):
        """Update archetype based on user behavior patterns"""
        category_distribution = habit_data.get('category_distribution', {})
        consistency = habit_data.get('consistency_score', 0)
        streak = habit_data.get('current_streak', 0)
        
        # Determine dominant category
        dominant_category = max(category_distribution.items(), key=lambda x: x[1], default=('general', 0))[0]
        
        archetype_map = {
            'fitness': Archetype.WARRIOR,
            'meditation': Archetype.MONK,
            'learning': Archetype.ACHIEVER,
            'creativity': Archetype.EXPLORER
        }
        
        new_archetype = archetype_map.get(dominant_category, Archetype.ACHIEVER)
        
        # Only change archetype if significant pattern emerges
        if (category_distribution.get(dominant_category, 0) > 0.6 and 
            consistency > 0.7 and 
            avatar.archetype != new_archetype):
            avatar.archetype = new_archetype
    
    def _update_evolution(self, avatar: UserAvatar):
        """Update evolution stage based on progress"""
        evolution_thresholds = {
            EvolutionStage.NOVICE: 0,
            EvolutionStage.APPRENTICE: 500,
            EvolutionStage.PRACTITIONER: 1500,
            EvolutionStage.EXPERT: 3000,
            EvolutionStage.MASTER: 6000
        }
        
        # Calculate evolution progress
        current_stage = avatar.evolution_stage
        current_threshold = evolution_thresholds.get(current_stage, 0)
        next_threshold = evolution_thresholds.get(current_stage + 1, float('inf'))
        
        if avatar.total_xp >= next_threshold:
            avatar.evolution_stage = current_stage + 1
            avatar.last_evolution = datetime.utcnow()
            avatar.evolution_progress = 0.0
        else:
            if next_threshold != float('inf'):
                progress = (avatar.total_xp - current_threshold) / (next_threshold - current_threshold)
                avatar.evolution_progress = max(0.0, min(1.0, progress))
    
    def _sync_with_mood(self, avatar: UserAvatar, mood: Optional[str]):
        """Sync avatar appearance with user mood"""
        mood_effects = {
            'happy': {'aura': 'golden_glow', 'emote': 'happy'},
            'sad': {'aura': 'none', 'emote': 'sad'},
            'energetic': {'aura': 'electric_blue', 'emote': 'energetic'},
            'tired': {'aura': 'none', 'emote': 'tired'},
            'focused': {'aura': 'concentration', 'emote': 'focused'}
        }
        
        if mood and mood in mood_effects:
            effects = mood_effects[mood]
            # Simple check if item is unlocked - in production this would be more robust
            if effects['aura'] in avatar.unlocked_items:
                avatar.aura = effects['aura']
            if effects['emote'] in avatar.unlocked_items:
                avatar.emote = effects['emote']
    
    def _handle_level_up(self, avatar: UserAvatar):
        """Handle rewards and unlocks on level up"""
        # Grant coins
        avatar.coins += avatar.level * 10
        
        # Unlock new items based on level
        unlockable_items = self.db.query(AvatarItem).filter(
            AvatarItem.unlock_level == avatar.level
        ).all()
        
        for item in unlockable_items:
            if item.id not in avatar.unlocked_items:
                # Need to handle JSON mutable list correctly for SQLAlchemy
                current_unlocked = list(avatar.unlocked_items)
                current_unlocked.append(item.id)
                avatar.unlocked_items = current_unlocked
    
    def purchase_item(self, user_id: str, item_id: str) -> bool:
        """Purchase and equip an avatar item"""
        avatar = self.get_avatar(user_id)
        item = self.db.query(AvatarItem).filter(AvatarItem.id == item_id).first()
        
        if not item:
            return False
            
        # Check if item is unlocked (level/archetype requirements)
        if avatar.level < item.unlock_level:
            return False
            
        if item.id not in avatar.unlocked_items:
            # Check for purchase if level requirement met
            if avatar.coins < item.price:
                return False
            avatar.coins -= item.price
            current_unlocked = list(avatar.unlocked_items)
            current_unlocked.append(item.id)
            avatar.unlocked_items = current_unlocked
        
        # Equip the item
        current_equipped = dict(avatar.equipped_items)
        current_equipped[item.type] = item.id
        avatar.equipped_items = current_equipped
        
        # Update visual fields directly for easy access
        if item.type == "skin": avatar.skin = item.id
        elif item.type == "outfit": avatar.outfit = item.id
        elif item.type == "aura": avatar.aura = item.id
        elif item.type == "accessory": avatar.accessory = item.id
        elif item.type == "emote": avatar.emote = item.id
        
        # Apply any stat boosts
        if item.xp_boost > 0:
            avatar.streak_bonus += int(item.xp_boost * 10) # Example scaling
        
        self.db.commit()
        return True
    
    def get_avatar(self, user_id: str) -> UserAvatar:
        """Get or create user avatar"""
        avatar = self.db.query(UserAvatar).filter(UserAvatar.user_id == user_id).first()
        if not avatar:
            avatar = UserAvatar(user_id=user_id, unlocked_items=[], equipped_items={})
            self.db.add(avatar)
            self.db.commit()
        return avatar
    
    def _get_xp_for_level(self, level: int) -> int:
        """Calculate XP required for level"""
        return level * 100 + (level - 1) * 50

# Factory for dependency injection
def get_avatar_service(db_session: Session) -> AvatarService:
    return AvatarService(db_session)
