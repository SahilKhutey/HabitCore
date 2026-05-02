"""
Reflection Intelligence Layer — Semantic tagging and duplication filtering for production-grade questions.
"""
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

TAG_RULES = {
    "avoidance": ["avoid", "delay", "escape", "postpone", "pushed"],
    "fear": ["fear", "afraid", "anxiety", "scared"],
    "self_doubt": ["doubt", "confidence", "uncertainty"],
    "distraction": ["distract", "focus", "attention", "interrupted"],
    "identity": ["person", "identity", "values", "standards", "integrity"],
    "emotion": ["feel", "emotion", "mood", "uncomfortable"],
    "productivity": ["work", "task", "finish", "complete", "progress"],
    "thought": ["think", "thought", "mind", "belief", "assumption"]
}

COGNITIVE_MAP = {
    "awareness": "awareness",
    "thoughts": "distortion",
    "avoidance": "behavioral_probe",
    "identity": "reflection",
    "behavior": "behavioral_probe"
}

def generate_semantic_tags(text: str) -> List[str]:
    """Auto-generates tags based on keyword matching."""
    q = text.lower()
    tags = []
    for tag, keywords in TAG_RULES.items():
        if any(k in q for k in keywords):
            tags.append(tag)
    return tags

def get_cognitive_type(category: str) -> str:
    """Maps system category to cognitive function type."""
    return COGNITIVE_MAP.get(category, "awareness")

def deduplicate_questions(questions_data: List[Dict[str, Any]], threshold: float = 0.8) -> List[Dict[str, Any]]:
    """
    Uses TF-IDF + Cosine Similarity to remove semantically redundant questions.
    """
    if not questions_data:
        return []
        
    texts = [q["question"] for q in questions_data]
    
    try:
        vec = TfidfVectorizer().fit_transform(texts)
        sim = cosine_similarity(vec)
        
        keep = []
        removed_indices = set()
        
        for i in range(len(texts)):
            if i in removed_indices:
                continue
            keep.append(questions_data[i])
            
            for j in range(i + 1, len(texts)):
                if sim[i][j] > threshold:
                    removed_indices.add(j)
                    logger.info(f"Duplicate detected: '{texts[j][:30]}' similar to '{texts[i][:30]}'")
                    
        return keep
    except Exception as e:
        logger.error(f"Deduplication failed: {e}")
        return questions_data
