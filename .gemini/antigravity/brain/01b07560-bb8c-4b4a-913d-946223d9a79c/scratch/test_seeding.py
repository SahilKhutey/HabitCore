import sys
import os
sys.path.append(r"c:\Users\User\Documents\HabitCore\backend")

from app.db.session import SessionLocal
from app.services.reflection_engine.pool import seed_questions_v3
from app.models.intelligence_models import Question

def test_seeding():
    db = SessionLocal()
    try:
        print("Starting seeding process V3...")
        seed_questions_v3(db)
        
        count = db.query(Question).count()
        print(f"Seeding complete. Total questions in DB: {count}")
        
        # Verify a few samples
        samples = db.query(Question).limit(5).all()
        for q in samples:
            print(f"- [{q.category}] {q.text[:50]}... (Depth: {q.depth_level})")
            
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_seeding()
