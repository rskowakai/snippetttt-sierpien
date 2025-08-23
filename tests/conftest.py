import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.main import app
from app.models import Base, User
from app.db.session import get_db
from app.services.security_service import get_password_hash, create_access_token

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis

@pytest.fixture(scope="function")
def test_db(postgres_container):
    database_url = postgres_container.get_connection_url()
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def test_user(test_db):
    db = test_db()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
