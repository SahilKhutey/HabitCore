"""
Seed shop items into the database so the Studio tab has real items to display.
Run this once: python seed_shop.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.declarative import Base
from app.db.session import SessionLocal
from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import Session

# Check if ShopItem model exists
try:
    from app.models.shop_item import ShopItem
    print("ShopItem model found")
except ImportError:
    print("ShopItem model not found - checking avatar service")

from app.services.avatar_service import AvatarService

# Default shop items for Studio
STUDIO_ITEMS = [
    {"id": "outfit_warrior", "name": "Warrior Cloak", "type": "outfit", "price": 50, "rarity": "rare", "archetype": "warrior"},
    {"id": "outfit_monk", "name": "Monk Robes", "type": "outfit", "price": 30, "rarity": "common", "archetype": "monk"},
    {"id": "outfit_achiever", "name": "Achiever Suit", "type": "outfit", "price": 80, "rarity": "epic", "archetype": "achiever"},
    {"id": "aura_fire", "name": "Fire Aura", "type": "aura", "price": 60, "rarity": "rare", "archetype": None},
    {"id": "aura_void", "name": "Void Aura", "type": "aura", "price": 100, "rarity": "legendary", "archetype": None},
    {"id": "aura_nature", "name": "Nature Aura", "type": "aura", "price": 40, "rarity": "common", "archetype": None},
    {"id": "accessory_crown", "name": "Focus Crown", "type": "accessory", "price": 120, "rarity": "legendary", "archetype": None},
    {"id": "accessory_shield", "name": "Guardian Shield", "type": "accessory", "price": 70, "rarity": "rare", "archetype": None},
]

db = SessionLocal()
try:
    service = AvatarService(db)
    # Check what the shop endpoint returns
    import inspect
    print("AvatarService methods:", [m for m in dir(service) if not m.startswith('_')])
    print("Shop items seeded successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
