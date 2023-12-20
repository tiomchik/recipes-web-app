from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.status import (
    HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
)
from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from random import randint

from auth.auth_config import current_user
from database import get_async_session, Recipe, User
from config import limiter
from .schemas import RecipeCreate, RecipeResponse
from .utils import recipe_response, get_recipe_by_id

router = APIRouter(
    prefix="/api/recipes",
    tags=["API"],
)


async def _create_recipe(
    session: AsyncSession, headling: str, text: str, author_id: int
) -> Recipe:
    """Sub-function for `create_recipe`."""
    recipe = Recipe(
        headling=headling,
        text=text,
        author_id=author_id
    )

    session.add(recipe)
    await session.commit()

    return recipe


@router.post("/", status_code=HTTP_201_CREATED, response_model=RecipeResponse)
@limiter.limit("30/minute")
async def create_recipe(
    request: Request, new_recipe: RecipeCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
) -> RecipeResponse:
    """Creates a new recipe."""
    recipe = await _create_recipe(
        session, new_recipe.headling, new_recipe.text, user.id
    )

    return recipe_response(recipe)


async def _get_recipes(
    session: AsyncSession,
    search_query: str | None = None, id: int | None = None,
    random: bool = False,
    page: int = 1, size: int = 12
) -> HTTPException | RecipeResponse | list[dict[str, int] | RecipeResponse]:
    """Sub-function for `get_recipes`."""
    # Search
    if search_query:
        stmt = select(Recipe).filter(
            Recipe.headling.like(f"%{search_query}%")
        )
        result = await session.execute(stmt)
        recipes = result.scalars().all()

        if not recipes:
            raise HTTPException(
                HTTP_404_NOT_FOUND,
                f"Recipes for query '{search_query}' not found"
            )
    
    # Searching a recipe with passed id
    elif id:
        recipe = await get_recipe_by_id(session, id)

        return recipe_response(recipe, full_text=True)

    # Random recipe
    elif random:
        count = await session.scalar(select(func.count(Recipe.id)))

        while True:
            random_id = randint(1, count)
            stmt = select(Recipe).filter_by(id=random_id)
            result = await session.execute(stmt)
            try:
                recipe = result.scalar_one()
            except NoResultFound:
                continue

            if not recipe:
                continue

            return recipe_response(recipe)

    # Latest recipes
    else:
        stmt = select(Recipe).order_by(Recipe.pub_date.desc())
        result = await session.execute(stmt)
        recipes = result.scalars().all()

        if not recipes:
            raise HTTPException(HTTP_404_NOT_FOUND, "Recipes not found")

    # Formatting a result
    formatted_result = [
        recipe_response(recipe).model_dump(mode="json") for recipe in recipes
    ]

    # Pagination and slicing
    offset_min = (page - 1) * size
    offset_max = page * size

    response = formatted_result[offset_min:offset_max] + [
        {
            "page": page,
            "size": size,
            "total": ceil(len(recipes) / size),
        }
    ]

    return response


@router.get("/", response_model=None)
@limiter.limit("30/minute")
async def get_recipes(
    request: Request, search_query: str | None = None, id: int | None = None,
    random: bool = False,
    page: int = 1, size: int = Query(ge=1, le=30, default=12),
    session: AsyncSession = Depends(get_async_session)
) -> HTTPException | RecipeResponse | list[dict[str, int] | RecipeResponse]:
    """Returns a latest recipes if no params are passed.

    :param `search_query`:

    Returns results of search on this query.

    :param `id`:

    Returns a recipe with this id.

    :param `random`:

    Returns a random recipe, default value is `False`. Makes sense, right?

    Endpoint can accept only one of this arguments. 
    For example, if you pass `search_query` and `random=True`,
    you'll get only results of search.

    """
    response = await _get_recipes(
        session, search_query, id, random, page, size
    )

    return response


async def _update_recipe(
    session: AsyncSession, user: User,
    id: int, updated_recipe: RecipeCreate
) -> Recipe | None:
    """Sub-function for `update_recipe`.
    
    Returns an updated recipe."""
    recipe = await get_recipe_by_id(session, id)
    if not recipe:
        raise HTTPException(HTTP_404_NOT_FOUND, "Recipe not found")
    elif user.id != recipe.author_id:
        raise HTTPException(
            HTTP_403_FORBIDDEN, "You aren't an author of this recipe"
        )

    stmt = update(Recipe).where(Recipe.id == id).values(
        headling=updated_recipe.headling,
        text=updated_recipe.text
    )

    await session.execute(stmt)
    await session.commit()

    return await get_recipe_by_id(session, id)


@router.put("/", response_model=RecipeResponse)
@limiter.limit("30/minute")
async def update_recipe(
    request: Request, id: int, updated_recipe: RecipeCreate, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(current_user)
) -> RecipeResponse:
    """Updating recipe with passed id."""
    new_recipe = await _update_recipe(session, user, id, updated_recipe)

    return recipe_response(new_recipe)


async def _delete_recipe(session: AsyncSession, user: User, id: int) -> None:
    """Sub-function for `delete_recipe`."""
    recipe = await get_recipe_by_id(session, id)

    if not recipe:
        raise HTTPException(HTTP_404_NOT_FOUND, "Recipe not found")
    elif recipe.author_id != user.id:
        raise HTTPException(
            HTTP_403_FORBIDDEN, "You aren't an author of this recipe"
        )

    await session.delete(recipe)
    await session.commit()


@router.delete("/", response_model=dict[str, str])
@limiter.limit("30/minute")
async def delete_recipe(
    request: Request, id: int, user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict[str, str]:
    """Deletes a recipe with passed id."""
    await _delete_recipe(session, user, id)

    return {"status": "The recipe has been successfully deleted"}
