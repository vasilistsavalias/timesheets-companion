import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.manager import Base
from src.database.models import User
from src.services.auth_service import AuthService

# Use in-memory SQLite for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_creation_and_auth(db_session):
    # Create user
    AuthService.create_user(db_session, "testuser", "password123", "Test User", is_admin=False)
    
    # Authenticate success
    user = AuthService.authenticate(db_session, "testuser", "password123")
    assert user is not None
    assert user.username == "testuser"
    assert AuthService.verify_password("password123", user.password_hash)
    
    # Authenticate failure (wrong password)
    assert AuthService.authenticate(db_session, "testuser", "wrong") is None
    
    # Authenticate failure (wrong user)
    assert AuthService.authenticate(db_session, "missing", "password123") is None

def test_admin_flag(db_session):
    admin = AuthService.create_user(db_session, "admin", "adminpass", is_admin=True)
    assert admin.is_admin is True
    
    regular = AuthService.create_user(db_session, "user", "userpass", is_admin=False)
    assert regular.is_admin is False
