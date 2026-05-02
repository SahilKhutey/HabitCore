import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.models.avatar_models import AvatarItem

ITEMS = [
    {"id": "outfit_basic", "name": "Basic Armor", "type": "outfit", "rarity": "common", "price": 0, "unlock_level": 1, "xp_boost": 0.0, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "outfit_warrior", "name": "Warrior Cloak", "type": "outfit", "rarity": "rare", "price": 50, "unlock_level": 3, "xp_boost": 0.1, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": "warrior", "evolution_requirement": 0, "animation_url": None},
    {"id": "outfit_monk", "name": "Monk Robes", "type": "outfit", "rarity": "common", "price": 30, "unlock_level": 2, "xp_boost": 0.0, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "outfit_achiever", "name": "Achiever Suit", "type": "outfit", "rarity": "epic", "price": 80, "unlock_level": 5, "xp_boost": 0.15, "coin_boost": 0.1, "streak_protection": False, "preview_url": None, "archetype_requirement": "achiever", "evolution_requirement": 0, "animation_url": None},
    {"id": "outfit_explorer", "name": "Explorer Vest", "type": "outfit", "rarity": "rare", "price": 60, "unlock_level": 4, "xp_boost": 0.05, "coin_boost": 0.05, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "aura_focus", "name": "Focus Haze", "type": "aura", "rarity": "common", "price": 20, "unlock_level": 1, "xp_boost": 0.05, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "aura_fire", "name": "Fire Aura", "type": "aura", "rarity": "rare", "price": 60, "unlock_level": 3, "xp_boost": 0.1, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "aura_void", "name": "Void Aura", "type": "aura", "rarity": "legendary", "price": 150, "unlock_level": 7, "xp_boost": 0.2, "coin_boost": 0.15, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 2, "animation_url": None},
    {"id": "aura_nature", "name": "Nature Aura", "type": "aura", "rarity": "uncommon", "price": 35, "unlock_level": 2, "xp_boost": 0.0, "coin_boost": 0.1, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "acc_crown", "name": "Focus Crown", "type": "accessory", "rarity": "legendary", "price": 200, "unlock_level": 10, "xp_boost": 0.25, "coin_boost": 0.2, "streak_protection": True, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 3, "animation_url": None},
    {"id": "acc_shield", "name": "Guardian Shield", "type": "accessory", "rarity": "rare", "price": 70, "unlock_level": 4, "xp_boost": 0.0, "coin_boost": 0.0, "streak_protection": True, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "acc_book", "name": "Sage Tome", "type": "accessory", "rarity": "rare", "price": 55, "unlock_level": 3, "xp_boost": 0.15, "coin_boost": 0.0, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 0, "animation_url": None},
    {"id": "acc_crystal", "name": "Mind Crystal", "type": "accessory", "rarity": "epic", "price": 90, "unlock_level": 6, "xp_boost": 0.12, "coin_boost": 0.08, "streak_protection": False, "preview_url": None, "archetype_requirement": None, "evolution_requirement": 1, "animation_url": None},
]

db = SessionLocal()
try:
    added = 0
    for item_data in ITEMS:
        exists = db.query(AvatarItem).filter(AvatarItem.id == item_data["id"]).first()
        if not exists:
            item = AvatarItem(**item_data)
            db.add(item)
            added += 1
    db.commit()
    total = db.query(AvatarItem).count()
    print(f"Added {added} new items. Total shop items: {total}")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
    import traceback; traceback.print_exc()
finally:
    db.close()
