import pytest

from fastapi.testclient import TestClient
from starlette.status import HTTP_404_NOT_FOUND

from conftest import (
    client, app, create_and_authenticate, create_recipe_for_update
)

pytestmark = pytest.mark.asyncio

updated_recipe_dict = {
    "headling": "test recipes api updated",
    "text": "lorem ipsum dolor now updated!!"
}


async def test_update_recipe(authenticated_client: TestClient) -> None:
    """`update_recipe` endpoint standard test."""
    recipe = await create_recipe_for_update(authenticated_client)

    authenticated_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json=updated_recipe_dict
    )

    r = authenticated_client.get(
        "/api/recipes/", params={"id": recipe["id"]}
    )

    assert recipe["id"] == r.json()["id"]
    assert "test recipes api updated" == r.json()["headling"]
    assert "lorem ipsum dolor now updated!!" == r.json()["text"]


async def test_update_recipe_short_headling(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test with too short headling."""
    recipe = await create_recipe_for_update(authenticated_client)

    r = authenticated_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json={
            "headling": "updated",
            "text": "lorem ipsum dolor now updated!!"
        }
    )

    assert r.json()["detail"]


async def test_update_recipe_long_headling(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test with too long headling."""
    recipe = await create_recipe_for_update(authenticated_client)

    updated_recipe_dict = {
        "headling": "updateddddddddddddddddddddddddddddddddddddddddddddd",
        "text": "lorem ipsum dolor now updated!!"
    }

    r = authenticated_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json=updated_recipe_dict
    )

    assert r.json()["detail"]


async def test_update_recipe_without_headling(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test without headling."""
    recipe = await create_recipe_for_update(authenticated_client)

    r = authenticated_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json={
            "text": "lorem ipsum dolor now updated!!"
        }
    )

    assert r.json()["detail"]


async def test_update_recipe_short_text(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test with too short text."""
    recipe = await create_recipe_for_update(authenticated_client)

    r = authenticated_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json={
            "headling": "test recipes api updated",
        }
    )

    assert r.json()["detail"]


async def test_update_nonexistent_recipe(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test with non-existent id."""
    r = authenticated_client.put(
        "/api/recipes/", params={"id": 99},
        json=updated_recipe_dict
    )

    assert r.json()["detail"]
    assert r.status_code == HTTP_404_NOT_FOUND


async def test_update_nonuser_recipe(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test with non-user recipe."""
    recipe = await create_recipe_for_update(authenticated_client)

    other_client = TestClient(app)
    await create_and_authenticate(
        other_client,
        username="other_test_user", email="other_test@example.com"
    )

    r = other_client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json=updated_recipe_dict
    )

    assert r.json()["detail"]


async def test_unauth_update_recipe(
    authenticated_client: TestClient
) -> None:
    """`update_recipe` endpoint test without authentication."""
    recipe = await create_recipe_for_update(authenticated_client)

    r = client.put(
        "/api/recipes/", params={"id": recipe["id"]},
        json=updated_recipe_dict
    )

    assert r.json()["detail"]
