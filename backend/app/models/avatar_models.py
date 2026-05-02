from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.declarative import Base

class Archetype(str, Enum):
    BEGINNER = "beginner"
    WARRIOR = "warrior"
    MONK = "monk"
    ACHIEVER = "achiever"
    EXPLORER = "explorer"

class EvolutionStage(int, Enum):
    NOVICE = 1
    APPRENTICE = 2
    PRACTITIONER = 3
    EXPERT = 4
    MASTER = 5

class UserAvatar(Base):
    __tablename__ = "user_avatars"

    user_id = Column(String, primary_key=True)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    
    # Identity and progression
    archetype = Column(String, default=Archetype.BEGINNER)
    evolution_stage = Column(Integer, default=EvolutionStage.NOVICE)
    evolution_progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Visual customization
    skin = Column(String, default="default")
    outfit = Column(String, default="basic")
    aura = Column(String, default="none")
    accessory = Column(String, default="none")
    emote = Column(String, default="default")
    
    # Stats and behavior
    streak_bonus = Column(Integer, default=0)
    consistency_score = Column(Float, default=0.0)
    mood_sync = Column(Boolean, default=True)
    
    # Economy
    coins = Column(Integer, default=0)
    unlocked_items = Column(JSON, default=list)
    equipped_items = Column(JSON, default=dict)
    
    # Timestamps
    last_evolution = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AvatarItem(Base):
    __tablename__ = "avatar_items"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # skin, outfit, aura, accessory, emote
    rarity = Column(String, default="common")  # common, rare, epic, legendary
    price = Column(Integer, default=0)
    unlock_level = Column(Integer, default=1)
    archetype_requirement = Column(String, nullable=True)
    evolution_requirement = Column(Integer, nullable=True)
    
    # Visual properties
    preview_url = Column(String)
    animation_url = Column(String, nullable=True)
    
    # Stats (for gameplay items)
    xp_boost = Column(Float, default=0.0)
    coin_boost = Column(Float, default=0.0)
    streak_protection = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
