from sqlalchemy.orm import Session
from app.models.user import User

SHOP_ITEMS = {
    "streak_freeze": {"price": 100, "name": "Streak Freeze"},
    "premium_theme": {"price": 500, "name": "Premium Theme"}
}

class ShopService:
    @staticmethod
    def buy_item(db: Session, user_id: str, item_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
            
        item = SHOP_ITEMS.get(item_id)
        if not item:
            return {"error": "Item not found"}
            
        if user.coins < item["price"]:
            return {"error": "Not enough coins"}
            
        user.coins -= item["price"]
        
        if item_id == "streak_freeze":
            user.streak_freezes += 1
        elif item_id == "premium_theme":
            # Logic for unlocking themes (e.g., adding to a many-to-many table)
            pass
            
        db.commit()
        return {"message": f"Successfully purchased {item['name']}", "coins": user.coins}
