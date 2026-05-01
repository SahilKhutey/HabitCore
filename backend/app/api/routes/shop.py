from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.models.shop import ShopItem, UserInventory
from app.models.user import User

from app.services.shop_service import ShopService

router = APIRouter()

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    return ShopService.get_items(db)

@router.post("/buy/{item_id}")
def buy_item(item_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    result = ShopService.buy_item(db, user, item_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result

@router.get("/inventory")
def get_inventory(user=Depends(auth_required), db: Session = Depends(get_db)):
    return db.query(UserInventory, ShopItem).join(ShopItem).filter(UserInventory.user_id == user.id).all()

@router.post("/equip/{inventory_id}")
def equip_item(inventory_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    inventory_item = db.query(UserInventory).filter(
        UserInventory.id == inventory_id,
        UserInventory.user_id == user.id
    ).first()
    
    if not inventory_item:
        raise HTTPException(404, "Item not found in inventory")
        
    shop_item = db.query(ShopItem).filter(ShopItem.id == inventory_item.item_id).first()
    
    if shop_item.category == "theme":
        # Deactivate other themes
        other_themes = db.query(UserInventory).join(ShopItem).filter(
            UserInventory.user_id == user.id,
            ShopItem.category == "theme",
            UserInventory.id != inventory_id
        ).all()
        for t in other_themes:
            t.is_active = False
            
    inventory_item.is_active = not inventory_item.is_active
    db.commit()
    
    return {"status": "success", "is_active": inventory_item.is_active}

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
