from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.services.avatar_service import get_avatar_service
from app.api.deps import get_db, auth_required
from app.models.avatar_models import AvatarItem

router = APIRouter()

class AvatarUpdateRequest(BaseModel):
    xp_earned: int
    habit_data: Dict[str, Any]

class PurchaseRequest(BaseModel):
    item_id: str

class EquipRequest(BaseModel):
    item_type: str
    item_value: Optional[str] = None

@router.get("/")
async def get_avatar(db: Session = Depends(get_db), current_user = Depends(auth_required)):
    """Get user avatar data"""
    try:
        service = get_avatar_service(db)
        avatar = service.get_avatar(current_user.id)
        return {
            "success": True,
            "avatar": {
                "level": avatar.level,
                "xp": avatar.xp,
                "total_xp": avatar.total_xp,
                "archetype": avatar.archetype,
                "evolution_stage": avatar.evolution_stage,
                "evolution_progress": avatar.evolution_progress,
                "appearance": {
                    "skin": avatar.skin,
                    "outfit": avatar.outfit,
                    "aura": avatar.aura,
                    "accessory": avatar.accessory,
                    "emote": avatar.emote
                },
                "economy": {
                    "coins": avatar.coins,
                    "unlocked_items": avatar.unlocked_items,
                    "equipped_items": avatar.equipped_items
                },
                "stats": {
                    "streak_bonus": avatar.streak_bonus,
                    "consistency_score": avatar.consistency_score
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get avatar: {str(e)}")

@router.post("/update")
async def update_avatar(request: AvatarUpdateRequest, db: Session = Depends(get_db), current_user = Depends(auth_required)):
    """Update avatar progress"""
    try:
        service = get_avatar_service(db)
        previous_stage = service.get_avatar(current_user.id).evolution_stage
        previous_level = service.get_avatar(current_user.id).level
        
        avatar = service.update_avatar_progress(current_user.id, request.xp_earned, request.habit_data)
        
        return {
            "success": True,
            "avatar": {
                "level": avatar.level,
                "xp": avatar.xp,
                "evolution_stage": avatar.evolution_stage,
                "evolution_progress": avatar.evolution_progress,
                "coins": avatar.coins
            },
            "evolution_occurred": avatar.evolution_stage > previous_stage,
            "level_up": avatar.level > previous_level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update avatar: {str(e)}")

@router.post("/purchase")
async def purchase_item(request: PurchaseRequest, db: Session = Depends(get_db), current_user = Depends(auth_required)):
    """Purchase and equip avatar item"""
    try:
        service = get_avatar_service(db)
        success = service.purchase_item(current_user.id, request.item_id)
        
        return {
            "success": success,
            "message": "Item purchased and equipped successfully" if success else "Purchase failed. Check requirements and funds."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@router.post("/equip")
async def equip_item(request: EquipRequest, db: Session = Depends(get_db), current_user = Depends(auth_required)):
    """Equip or unequip an appearance item"""
    try:
        from app.models.avatar_models import UserAvatar
        avatar = db.query(UserAvatar).filter(UserAvatar.user_id == current_user.id).first()
        if not avatar: raise HTTPException(404, "Avatar not found")
        
        if request.item_type == "skin": avatar.skin = request.item_value
        elif request.item_type == "outfit": avatar.outfit = request.item_value
        elif request.item_type == "aura": avatar.aura = request.item_value
        elif request.item_type == "accessory": avatar.accessory = request.item_value
        
        db.commit()
        return {"success": True, "message": f"{request.item_type} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Equip failed: {str(e)}")

@router.get("/shop")
async def get_shop_items(db: Session = Depends(get_db), current_user = Depends(auth_required)):
    """Get available avatar items"""
    try:
        items = db.query(AvatarItem).order_by(AvatarItem.price).all()
        return {
            "success": True,
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "type": item.type,
                    "rarity": item.rarity,
                    "price": item.price,
                    "unlock_level": item.unlock_level,
                    "preview_url": item.preview_url,
                    "stats": {
                        "xp_boost": item.xp_boost,
                        "coin_boost": item.coin_boost,
                        "streak_protection": item.streak_protection
                    }
                }
                for item in items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shop items: {str(e)}")
