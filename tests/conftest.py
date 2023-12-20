import asyncio
import pytest_asyncio

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from src.database import get_async_session, Base
from src.main import app

# Database
DATABASE_URL_TEST = "sqlite+aiosqlite:///./database.db"
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine_test, expire_on_commit=False
)
Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


async def prepare_database() -> None:
    """Creates tables in database."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(prepare_database())

# Setup
client = TestClient(app)


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


async def create_and_authenticate(
    client: TestClient, username: str, email: str
) -> None:
    """Authenticates a passed test client.

    Password: test1234."""
    client.post("/auth/register", json={
        "username": username, "email": email,
        "password": "test1234"
    })
    r = client.post("/auth/jwt/login", data={
        "username": email, "password": "test1234"
    })
    client.cookies = r.cookies
    client.headers["Cookie"] = r.headers.get("Set-Cookie")


@pytest_asyncio.fixture(scope="function")
async def authenticated_client() -> None:
    """User fixture that authenticates a test client."""
    authenticated_client = TestClient(app)

    await create_and_authenticate(
        authenticated_client,
        username="test_user", email="test@example.com"
    )

    yield authenticated_client

    authenticated_client.cookies = None


async def create_recipe_for_update(client: TestClient) -> dict:
    recipe = client.post("/api/recipes/", json={
        "headling": "test recipes api not updated",
        "text": "lorem ipsum dolor!"
    })

    return recipe.json()
