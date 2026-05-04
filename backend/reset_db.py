from app.db.session import engine
from app.db.base import Base
import os
from seed_data import seed_data
from seed_shop import seed_shop

db_path = 'habithero.db'

def reset_db():
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database at {db_path}")
    
    Base.metadata.create_all(bind=engine)
    print("Created all tables from models.")
    
    seed_data()
    print("Seeded basic data.")
    
    # Check if seed_shop exists
    try:
        from seed_shop import seed_shop
        from app.db.session import SessionLocal
        db = SessionLocal()
        seed_shop(db)
        db.close()
        print("Seeded shop items.")
    except ImportError:
        print("seed_shop.py not found, skipping.")

if __name__ == "__main__":
    reset_db()
