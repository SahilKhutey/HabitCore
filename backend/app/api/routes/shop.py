from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.models.shop import ShopItem, UserInventory
from app.models.user import User

router = APIRouter()

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(ShopItem).all()

@router.post("/buy/{item_id}")
def buy_item(item_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item: raise HTTPException(404, "Item not found")
    
    if user.coins < item.cost:
        raise HTTPException(400, "Insufficient coins")
        
    user.coins -= item.cost
    
    # Apply Item Effects
    if item.category == "powerup" and "Streak Freeze" in item.name:
        user.streak_freezes += 1
    elif item.category == "booster":
        user.xp += 50 # Instant boost
        
    inventory_item = UserInventory(user_id=user.id, item_id=item.id)
    db.add(inventory_item)
    db.commit()
    
    return {
        "message": "Purchase successful", 
        "remaining_coins": user.coins,
        "xp": user.xp,
        "streak_freezes": user.streak_freezes
    }

@router.get("/inventory")
def get_inventory(user=Depends(auth_required), db: Session = Depends(get_db)):
    # Join with ShopItem to get names and categories
    return db.query(UserInventory, ShopItem).join(ShopItem).filter(UserInventory.user_id == user.id).all()

@router.post("/use/{inventory_id}")
def use_item(inventory_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    item_record = db.query(UserInventory).filter(
        UserInventory.id == inventory_id, 
        UserInventory.user_id == user.id
    ).first()
    
    if not item_record:
        raise HTTPException(404, "Item not found in inventory")
        
    # Logic based on item type
    # For now, just delete from inventory
    db.delete(item_record)
    db.commit()
    
    return {"message": "Item used successfully"}
