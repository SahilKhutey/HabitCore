from app.db.session import SessionLocal
from app.models.avatar_models import AvatarItem
from sqlalchemy.orm import Session

# Default shop items for Studio
STUDIO_ITEMS = [
    {"id": "outfit_warrior", "name": "Warrior Cloak", "type": "outfit", "price": 50, "rarity": "rare", "archetype_requirement": "warrior"},
    {"id": "outfit_monk", "name": "Monk Robes", "type": "outfit", "price": 30, "rarity": "common", "archetype_requirement": "monk"},
    {"id": "outfit_achiever", "name": "Achiever Suit", "type": "outfit", "price": 80, "rarity": "epic", "archetype_requirement": "achiever"},
    {"id": "aura_fire", "name": "Fire Aura", "type": "aura", "price": 60, "rarity": "rare"},
    {"id": "aura_void", "name": "Void Aura", "type": "aura", "price": 100, "rarity": "legendary"},
    {"id": "aura_nature", "name": "Nature Aura", "type": "aura", "price": 40, "rarity": "common"},
    {"id": "accessory_crown", "name": "Focus Crown", "type": "accessory", "price": 120, "rarity": "legendary"},
    {"id": "accessory_shield", "name": "Guardian Shield", "type": "accessory", "price": 70, "rarity": "rare"},
]

def seed_shop(db: Session):
    print("Seeding shop items...")
    for item_data in STUDIO_ITEMS:
        existing = db.query(AvatarItem).filter(AvatarItem.id == item_data["id"]).first()
        if not existing:
            item = AvatarItem(**item_data)
            db.add(item)
            print(f"Added shop item: {item.name}")
    db.commit()
    print("Shop items seeded successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_shop(db)
    finally:
        db.close()
