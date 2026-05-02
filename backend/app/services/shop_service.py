from sqlalchemy.orm import Session
from app.models.user import User
from app.models.shop import ShopItem, UserInventory

class ShopService:
    @staticmethod
    def get_items(db: Session):
        return db.query(ShopItem).all()

    @staticmethod
    def buy_item(db: Session, user: User, item_id: str):
        item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
        if not item:
            return {"error": "Item not found"}
            
        if user.coins < item.cost:
            return {"error": "Not enough coins"}
            
        if user.level < item.unlock_level:
            return {"error": f"Requires Level {item.unlock_level}"}

        # Check if already owned
        existing = db.query(UserInventory).filter(
            UserInventory.user_id == user.id,
            UserInventory.item_id == item.id
        ).first()
        
        if existing:
            return {"error": "Already owned"}
            
        user.coins -= item.cost
        
        inventory_item = UserInventory(
            user_id=user.id,
            item_id=item.id
        )
        db.add(inventory_item)
        
        # Special logic for consumables
        if item.category == "booster" and item.name == "Streak Freeze":
            user.streak_freeze += 1
            
        db.commit()
        return {"message": f"Successfully purchased {item.name}", "coins": user.coins}
