"""
One-time shop seeding utility. Called on startup if shop is empty.
"""
from sqlalchemy.orm import Session
from app.models.shop import ShopItem
import uuid


DEFAULT_SHOP_ITEMS = [
    # Themes
    {"name": "Neon Matrix", "category": "theme", "cost": 150, "unlock_level": 1,
     "description": "Activate a vibrant neon-green matrix overlay on your dashboard."},
    {"name": "Void Protocol", "category": "theme", "cost": 250, "unlock_level": 3,
     "description": "Deep space dark mode with violet constellation accents."},
    {"name": "Solar Flare", "category": "theme", "cost": 350, "unlock_level": 5,
     "description": "Amber and gold energy burst theme for high-performers."},

    # Powerups
    {"name": "Streak Freeze", "category": "powerup", "cost": 100, "unlock_level": 1,
     "description": "Protect your streak from a single missed day."},
    {"name": "XP Multiplier", "category": "powerup", "cost": 200, "unlock_level": 2,
     "description": "Double all XP earned for the next 24 hours."},
    {"name": "Focus Shield", "category": "powerup", "cost": 175, "unlock_level": 3,
     "description": "Reduce burnout score accumulation by 50% for 3 days."},

    # Boosters
    {"name": "Morning Boost", "category": "booster", "cost": 80, "unlock_level": 1,
     "description": "Instantly complete 1 habit with full XP rewards."},
    {"name": "Identity Reset", "category": "booster", "cost": 300, "unlock_level": 4,
     "description": "Reset your identity goal alignment to a fresh archetype."},
    {"name": "Coin Magnet", "category": "booster", "cost": 120, "unlock_level": 2,
     "description": "Earn 2x coins from all habits for 48 hours."},
]


def seed_shop_items(db: Session):
    """Seed default shop items if shop is empty."""
    count = db.query(ShopItem).count()
    if count == 0:
        for item_data in DEFAULT_SHOP_ITEMS:
            item = ShopItem(
                id=str(uuid.uuid4()),
                **item_data
            )
            db.add(item)
        db.commit()
        print(f"[ShopSeed] Seeded {len(DEFAULT_SHOP_ITEMS)} shop items.")
    else:
        print(f"[ShopSeed] Shop already has {count} items — skipping seed.")
