import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.gamification import Badge, UserBadge
from app.services.gamification_service import HeroService

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Seed a premium badge
    badge = Badge(name="The Immortal", description="30 day streak", icon_name="crown", is_premium_exclusive=True)
    db_badge = db_session = session
    db_session.add(badge)
    db_session.commit()
    
    yield session
    session.close()

def test_grant_premium_badge_to_premium_user(db):
    # Setup
    user = User(email="hero@example.com", is_premium=True)
    db.add(user)
    db.commit()
    
    # Act
    # We want HeroService to check if a user qualifies for any badges
    HeroService.check_milestones(db, user, current_streak=30)
    
    # Assert
    earned = db.query(UserBadge).filter(UserBadge.user_id == user.id).first()
    assert earned is not None
    badge = db.query(Badge).filter(Badge.id == earned.badge_id).first()
    assert badge.name == "The Immortal"

def test_do_not_grant_premium_badge_to_standard_user(db):
    # Setup
    user = User(email="pleb@example.com", is_premium=False)
    db.add(user)
    db.commit()
    
    # Act
    HeroService.check_milestones(db, user, current_streak=30)
    
    # Assert
    earned = db.query(UserBadge).filter(UserBadge.user_id == user.id).first()
    assert earned is None
