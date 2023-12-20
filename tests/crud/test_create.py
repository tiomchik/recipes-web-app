import pytest

from fastapi.testclient import TestClient
from starlette.status import (
    HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED
)

from conftest import client

pytestmark = pytest.mark.asyncio


async def test_create_recipe(authenticated_client: TestClient) -> None:
    """`create_recipe` endpoint standard test."""
    r = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api test",
        "text": "lorem ipsum dolor!"
    })

    assert r.status_code == HTTP_201_CREATED


async def test_create_recipe_short_headling(
    authenticated_client: TestClient
) -> None:
    """`create_recipe` endpoint test with too short headling."""
    r = authenticated_client.post("/api/recipes/", json={
        "headling": "123", "text": "lorem ipsum dolor!"
    })

    assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_recipe_long_headling(
    authenticated_client: TestClient
) -> None:
    """`create_recipe` endpoint test with too long headling."""
    r = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api test with toooooooooooooooo long headling",
        "text": "lorem ipsum dolor!"
    })

    assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_recipe_without_headling(
    authenticated_client: TestClient
) -> None:
    """`create_recipe` endpoint test without headling."""
    r = authenticated_client.post("/api/recipes/", json={
        "text": "lorem ipsum dolor!"
    })

    assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_recipe_short_text(
    authenticated_client: TestClient
) -> None:
    """`create_recipe` endpoint test with too short text."""
    r = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api test", "text": "hi"
    })

    assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_recipe_without_text(
    authenticated_client: TestClient
) -> None:
    """`create_recipe` endpoint test without text."""
    r = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api test"
    })

    assert r.status_code == HTTP_422_UNPROCESSABLE_ENTITY


async def test_unauth_create_recipe() -> None:
    """`create_recipe` endpoint test without authentication."""
    r = client.post("/api/recipes/", json={
        "headling": "recipes api test",
        "text": "lorem ipsum dolor!"
    })

    assert r.status_code == HTTP_401_UNAUTHORIZED