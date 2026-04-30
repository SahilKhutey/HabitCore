from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from app.db.declarative import Base
import uuid

class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    category = Column(String) # theme, powerup, booster
    cost = Column(Integer)
    description = Column(String)

class UserInventory(Base):
    __tablename__ = "user_inventory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    item_id = Column(String, ForeignKey("shop_items.id"))
    is_active = Column(Boolean, default=False)
