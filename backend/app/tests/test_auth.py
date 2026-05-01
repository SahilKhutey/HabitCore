import pytest
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.db.base import Base
from app.models.user import User
from app.services.identity_orchestrator import IdentityOrchestrator

@pytest.fixture
def db():
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    yield session
    session.close()

def test_authenticate_social_existing_user(db, mocker):
    # RED: This method doesn't exist yet
    
    # 1. Setup existing user
    user = User(email="test@apple.com", social_id="apple_123", provider="apple")
    db.add(user)
    db.commit()
    
    # 2. Mock token verification and analytics
    mocker.patch("app.services.identity_orchestrator.IdentityOrchestrator._verify_apple_token", 
                 return_value={"email": "test@apple.com", "sub": "apple_123"})
    mocker.patch("app.services.identity_orchestrator.AnalyticsService.log_event")
    
    # 3. Act
    session = IdentityOrchestrator.authenticate_social(db, "apple", "mock_token")
    
    # 4. Assert
    assert session is not None
    assert session.user_id == str(user.id)

def test_authenticate_social_new_user(db, mocker):
    # 1. Setup - no user exists
    
    # 2. Mock token verification and analytics
    mocker.patch("app.services.identity_orchestrator.IdentityOrchestrator._verify_apple_token", 
                 return_value={"email": "new@apple.com", "sub": "apple_new_456"})
    mocker.patch("app.services.identity_orchestrator.AnalyticsService.log_event")
    
    # 3. Act
    session = IdentityOrchestrator.authenticate_social(db, "apple", "mock_token")
    
    # 4. Assert
    assert session is not None
    user = db.query(User).filter(User.social_id == "apple_new_456").first()
    assert user is not None
    assert user.email == "new@apple.com"
    assert session.user_id == str(user.id)

def test_authenticate_social_invalid_token(db, mocker):
    # 1. Mock token verification to return None
    mocker.patch("app.services.identity_orchestrator.IdentityOrchestrator._verify_apple_token", 
                 return_value=None)
    
    # 2. Act
    session = IdentityOrchestrator.authenticate_social(db, "apple", "invalid_token")
    
    # 3. Assert
    assert session is None


