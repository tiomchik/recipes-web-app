import pytest

from fastapi.testclient import TestClient
from starlette.status import (
    HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)

from conftest import client, app, create_and_authenticate


pytestmark = pytest.mark.asyncio

async def test_delete_recipe(authenticated_client: TestClient) -> None:
    """`delete_recipe` endpoint standard test."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "test recipes api thats need to delete",
        "text": "lorem ipsum dolor!"
    })
    id = recipe.json().pop("id")

    r = authenticated_client.delete("/api/recipes/", params={"id": id})

    assert r.status_code == HTTP_200_OK


async def test_unauth_delete_recipe(
    authenticated_client: TestClient
) -> None:
    """`delete_recipe` endpoint test without authentication."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "test recipes api thats need to delete",
        "text": "lorem ipsum dolor!"
    })
    id = recipe.json().pop("id")

    r = client.delete("/api/recipes/", params={"id": id})

    assert r.json()["detail"]
    assert r.status_code == HTTP_401_UNAUTHORIZED


async def test_delete_nonexistent_recipe(
    authenticated_client: TestClient
) -> None:
    """`delete_recipe` endpoint test with non-existent recipe."""
    r = authenticated_client.delete("/api/recipes/", params={"id": 9999999})

    assert r.json()["detail"]
    assert r.status_code == HTTP_404_NOT_FOUND


async def test_delete_nonuser_recipe(
    authenticated_client: TestClient
) -> None:
    """`delete_recipe` endpoint test with non-user recipe."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "test recipes api thats need to delete",
        "text": "lorem ipsum dolor!"
    })
    id = recipe.json().pop("id")

    other_client = TestClient(app)
    await create_and_authenticate(
        other_client,
        username="other_test_user_delete",
        email="other_delete_test@example.com"
    )

    r = other_client.delete("/api/recipes/", params={"id": id})

    assert r.json()["detail"]
    assert r.status_code == HTTP_403_FORBIDDEN
