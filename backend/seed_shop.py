from app.db.session import SessionLocal
from app.models.shop import ShopItem

def seed_shop():
    db = SessionLocal()
    
    items = [
        {
            "name": "Streak Freeze",
            "category": "powerup",
            "cost": 50,
            "description": "Protects your streak for one day if you miss a habit."
        },
        {
            "name": "XP Booster (2h)",
            "category": "booster",
            "cost": 30,
            "description": "Gain double XP for all habit completions for the next 2 hours."
        },
        {
            "name": "Theme: Cyber Neon",
            "category": "theme",
            "cost": 200,
            "description": "A vibrant neon theme for your entire dashboard."
        },
        {
            "name": "Daily Chest",
            "category": "mystery",
            "cost": 40,
            "description": "Contains a random amount of XP or a small chance for a powerup."
        },
        {
            "name": "Premium Pass (1mo)",
            "category": "subscription",
            "cost": 500,
            "description": "Unlock all premium features for 30 days."
        }
    ]

    for item_data in items:
        existing = db.query(ShopItem).filter(ShopItem.name == item_data["name"]).first()
        if not existing:
            item = ShopItem(**item_data)
            db.add(item)
            print(f"Adding shop item: {item.name}")
        else:
            print(f"Shop item already exists: {item_data['name']}")
    
    db.commit()
    db.close()
    print("Shop seeding complete.")

if __name__ == "__main__":
    seed_shop()
