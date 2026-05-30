"""Test fixtures: async client with isolated test database."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from blog_api.main import app
from blog_api.database import get_db
from blog_api.models.base import Base

TEST_DB = "sqlite+aiosqlite:///test.db"


@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine(TEST_DB, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def auth_client(async_client: AsyncClient):
    """Return a client pre-authenticated with a test user."""
    await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    })

    r = await async_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    token = r.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client
