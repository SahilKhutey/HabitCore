import pytest
from app.models.shop import ShopItem, UserInventory
from app.models.user import User
from app.core.security import hash_password

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        coins=100,
        level=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_inventory_activation_status(client, db_session, test_user):
    # Setup: Create a shop item and add it to user inventory
    item = ShopItem(name="Neon Glow", category="theme", cost=10, description="Vibrant neon theme")
    db_session.add(item)
    db_session.commit()
    
    # Login to get token
    login_res = client.post("/auth/login", json={"email": test_user.email, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buy item
    client.post(f"/shop/buy/{item.id}", headers=headers)
    
    # Check inventory
    res = client.get("/users/inventory", headers=headers)
    assert res.status_code == 200
    inventory = res.json()
    assert len(inventory) == 1
    assert inventory[0]["name"] == "Neon Glow"
    assert inventory[0]["is_active"] == False
    
    inventory_id = inventory[0]["inventory_id"]
    
    # Equip item
    res = client.post(f"/shop/equip/{inventory_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["is_active"] == True
    
    # Verify inventory status
    res = client.get("/users/inventory", headers=headers)
    assert res.json()[0]["is_active"] == True
    
    # Toggle off
    client.post(f"/shop/equip/{inventory_id}", headers=headers)
    res = client.get("/users/inventory", headers=headers)
    assert res.json()[0]["is_active"] == False

def test_theme_exclusivity(client, db_session, test_user):
    # Setup: Create two themes
    item1 = ShopItem(name="Theme 1", category="theme", cost=5)
    item2 = ShopItem(name="Theme 2", category="theme", cost=5)
    db_session.add(item1)
    db_session.add(item2)
    db_session.commit()
    
    login_res = client.post("/auth/login", json={"email": test_user.email, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buy both
    client.post(f"/shop/buy/{item1.id}", headers=headers)
    client.post(f"/shop/buy/{item2.id}", headers=headers)
    
    inventory = client.get("/users/inventory", headers=headers).json()
    inv1_id = next(i["inventory_id"] for i in inventory if i["name"] == "Theme 1")
    inv2_id = next(i["inventory_id"] for i in inventory if i["name"] == "Theme 2")
    
    # Equip Theme 1
    client.post(f"/shop/equip/{inv1_id}", headers=headers)
    
    # Equip Theme 2
    client.post(f"/shop/equip/{inv2_id}", headers=headers)
    
    # Verify only Theme 2 is active
    inventory = client.get("/users/inventory", headers=headers).json()
    for i in inventory:
        if i["name"] == "Theme 2":
            assert i["is_active"] == True
        if i["name"] == "Theme 1":
            assert i["is_active"] == False
