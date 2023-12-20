import pytest

from fastapi.testclient import TestClient
from starlette.status import HTTP_404_NOT_FOUND

from conftest import client

pytestmark = pytest.mark.asyncio


async def test_get_recipes(authenticated_client: TestClient) -> None:
    """`get_recipes` endpoint standard test."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api get test",
        "text": "lorem ipsum dolor!"
    })

    headling = recipe.json().pop("headling")

    r = authenticated_client.get("/api/recipes/")

    assert headling in r.json()[0].values()


async def test_search_recipes(authenticated_client: TestClient) -> None:
    """`get_recipes` endpoint search test."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api search test",
        "text": "lorem ipsum dolor!"
    })

    headling = recipe.json().pop("headling")

    r = authenticated_client.get(
        "/api/recipes/", params={"search_query": "search"}
    )

    assert "search" in r.json()[0]["headling"]


async def test_search_nonexistent_recipes() -> None:
    """`get_recipes` endpoint test with non-existent recipes search query."""
    r = client.get("/api/recipes/", params={"search_query": "ello"})

    assert r.json()["detail"]
    assert r.status_code == HTTP_404_NOT_FOUND


async def test_get_recipe_by_id(authenticated_client: TestClient) -> None:
    """`get_recipes` endpoint test with id."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api get by id test",
        "text": "lorem ipsum dolor!"
    })

    id = recipe.json().pop("id")

    r = authenticated_client.get("/api/recipes/", params={"id": id})

    assert id == r.json()["id"]


async def test_get_recipe_by_nonexistent_id() -> None:
    """`get_recipes` endpoint test with non-existent id."""
    r = client.get("/api/recipes/", params={"id": 99999999})

    assert r.json()["detail"]
    assert r.status_code == HTTP_404_NOT_FOUND


async def test_get_random_recipe() -> None:
    """`get_recipes` endpoint test with random recipe."""
    r = client.get("/api/recipes/", params={"random": True})

    assert r.json()["headling"]


async def test_get_recipes_few_params(
    authenticated_client: TestClient
) -> None:
    """`get_recipes` endpoint test with few params."""
    recipe = authenticated_client.post("/api/recipes/", json={
        "headling": "recipes api get with few params test",
        "text": "lorem ipsum dolor!"
    })

    headling = recipe.json()["headling"]

    r = authenticated_client.get("/api/recipes/", params={
        "search_query": headling, "id": 99999999, "random": True
    })

    assert headling in r.json()[0]["headling"]
