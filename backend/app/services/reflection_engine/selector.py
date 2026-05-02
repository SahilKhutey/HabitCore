"""
Reflection Selection Engine V3 — Semantic Rotation and Psychological Balancing.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.intelligence_models import Question, QuestionStats, UserQuestionHistory
from datetime import datetime, timezone

def select_adaptive_questions_v2(db: Session, user_id: str, signals: Dict[str, Any]) -> List[Question]:
    """
    Selects 3 questions using V3 Intelligence Layer:
    1. Fetch candidates with Novelty Ranking
    2. Apply Trigger Overrides
    3. Smart Semantic Rotation (Anti-Repetition)
    4. Enforce Psychological Balance (Awareness, Behavior, Identity)
    """
    # 1. Fetch Candidates (Ranked by Novelty)
    pool = db.query(Question).filter(Question.active == True).order_by(Question.novelty_score.desc()).all()
    
    # 2. Fetch History
    history = db.query(UserQuestionHistory).filter(UserQuestionHistory.user_id == user_id).all()
    history_dict = {h.question_id: h for h in history}
    
    now = datetime.now(timezone.utc)
    
    # 3. Filtering & Trigger Application
    triggered_questions = []
    active_signals = [s for s, val in signals.items() if val]
    
    candidates = []
    for q in pool:
        # History Filter (Cooldown)
        h = history_dict.get(q.id)
        if h and h.last_shown_at:
            days_since = (now - h.last_shown_at.replace(tzinfo=timezone.utc)).days
            if days_since < q.cooldown_days:
                continue
        
        # Trigger Check
        if q.trigger_types:
            if set(q.trigger_types) & set(active_signals):
                triggered_questions.append(q)
                continue # Prioritize in special list
                
        candidates.append(q)

    # 4. Smart Rotation & Balancing
    selected = []
    used_semantic_tags = set()
    used_categories = set()
    
    # Mode balancing targets
    targets = ["awareness", "behavior", "identity"]
    if signals.get("avoidance_high"):
        targets = ["avoidance", "behavior", "thoughts"]
    elif signals.get("burnout_risk"):
        targets = ["awareness", "emotional_regulation"]

    # --- Phase A: Triggered Overrides (Max 1) ---
    if triggered_questions:
        # Sort by emotional intensity if burnout, or priority
        t_q = triggered_questions[0]
        selected.append(t_q)
        used_categories.add(t_q.category)
        if t_q.semantic_tags:
            used_semantic_tags.update(t_q.semantic_tags)

    # --- Phase B: Balanced Selection ---
    for target_cat in targets:
        if len(selected) >= 3: break
        if target_cat in used_categories: continue
        
        for q in candidates:
            if q.category != target_cat: continue
            
            # Semantic check
            q_tags = set(q.semantic_tags or [])
            if q_tags & used_semantic_tags: continue
            
            selected.append(q)
            used_categories.add(q.category)
            if q_tags:
                used_semantic_tags.update(q_tags)
            break

    # --- Phase C: Fallback Fill ---
    if len(selected) < 3:
        for q in candidates:
            if q in selected: continue
            selected.append(q)
            if len(selected) >= 3: break

    # 5. Update Usage & Decay Novelty
    for q in selected:
        h = history_dict.get(q.id)
        if not h:
            h = UserQuestionHistory(user_id=user_id, question_id=q.id)
            db.add(h)
        h.last_shown_at = now
        h.times_seen += 1
        
        # Decay Novelty Score
        q.novelty_score *= 0.95
        
    db.commit()
    return selected
