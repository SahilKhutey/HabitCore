"""
Reflection Pool Seeder V3 (Intelligence) — Ingests with Semantic Tagging and Deduplication.
"""
import json
import os
import logging
from sqlalchemy.orm import Session
from app.models.intelligence_models import Question
from app.services.reflection_engine.intelligence import generate_semantic_tags, get_cognitive_type, deduplicate_questions

logger = logging.getLogger(__name__)

def validate_question_v3(q):
    assert 1 <= q.get("depth", 1) <= 3, f"Invalid depth for: {q.get('question')}"
    assert q.get("category") and (q.get("subcategory") or q.get("category")), "Category required."

def seed_questions_v3(db: Session):
    """
    Ingests questions with V3 intelligence:
    - Auto-tagging
    - Semantic deduplication
    - Intelligence field mapping
    """
    data_path = os.path.join(os.path.dirname(__file__), "data", "questions_v2.json")
    
    if not os.path.exists(data_path):
        logger.error(f"Questions dataset not found at {data_path}")
        return

    with open(data_path, "r") as f:
        raw_data = json.load(f)

    # 1. Deduplicate before ingestion
    clean_data = deduplicate_questions(raw_data, threshold=0.85)
    logger.info(f"Deduplication complete: {len(raw_data)} -> {len(clean_data)}")

    for q_data in clean_data:
        try:
            validate_question_v3(q_data)
            
            text = q_data["question"]
            category = q_data["category"]
            
            # 2. Intelligence Enrichment
            semantic_tags = generate_semantic_tags(text)
            cognitive_type = get_cognitive_type(category)
            
            db_data = {
                "category": category,
                "subcategory": q_data.get("subcategory", f"{category}_general"),
                "text": text,
                "depth_level": q_data.get("depth", 1),
                "emotional_intensity": q_data.get("intensity", 0.5),
                "trigger_types": q_data.get("trigger_types", []),
                "semantic_tags": semantic_tags,
                "cognitive_type": cognitive_type,
                "emotional_weight": int(q_data.get("intensity", 0.5) * 5),
                "novelty_score": 1.0,
                "cooldown_days": 3,
                "base_priority": q_data.get("priority", 0.5),
                "intent": q_data.get("intent", category.replace("_", " "))
            }
            
            # 3. Idempotent Sync
            exists = db.query(Question).filter(Question.text == db_data["text"]).first()
            if not exists:
                q = Question(**db_data)
                db.add(q)
            else:
                for key, value in db_data.items():
                    setattr(exists, key, value)
                    
        except Exception as e:
            logger.error(f"Seeding error: {e}")
            continue
    
    db.commit()
    logger.info("Successfully synced Reflection Pool V3.")
