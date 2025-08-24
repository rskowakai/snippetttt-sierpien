import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, User
from app.db.session import get_db, engine
from app.services.security_service import get_password_hash, create_access_token

# Test configuration
@pytest.fixture(scope="session")
def test_db_engine():
    # The engine is already configured in app.db.session to read from .env
    # which points to the docker-compose postgres instance.
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Creates a new database session for a test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Fixture to override the get_db dependency to use the test session."""
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    del app.dependency_overrides[get_db]


@pytest.fixture(scope="function")
async def test_client(override_get_db):
    """Fixture for a test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def test_user(db_session):
    """Fixture to create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Fixture for authentication headers."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
