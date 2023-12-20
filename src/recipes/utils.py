from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Recipe
from .schemas import RecipeResponse


async def validate_recipe_fields(
    headling: str, text: str, errors: list
) -> None:
    """Validates recipe fields and adds errors in `errors` list."""
    if not headling:
        errors.append("Headling field is required")
    elif not text:
        errors.append("Text field is required")
    elif len(headling) < 10:
        errors.append("Headling is too short (less than 10 characters)")
    elif len(headling) > 50:
        errors.append("Headling is too long (more than 50 characters)")
    elif len(text) < 10:
        errors.append("Text is too short (less than 10 characters)")


def recipe_response(
    recipe: Recipe, full_text: bool = False
) -> RecipeResponse:
    """Creating an `RecipeResponse` instance with passed recipe."""
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    max_text_len = 110

    if full_text or len(recipe.text) < max_text_len:
        return RecipeResponse(
            id=recipe.id, headling=recipe.headling, text=recipe.text,
            pub_date=recipe.pub_date, author=recipe.author.username
        )
    elif len(recipe.text) > max_text_len:
        return RecipeResponse(
            id=recipe.id, headling=recipe.headling,
            text=f"{recipe.text[:max_text_len]}...",
            pub_date=recipe.pub_date,
            author=recipe.author.username
        )


async def get_recipe_by_id(session: AsyncSession, id: int) -> Recipe | None:
    """Getting recipe with passed id."""
    stmt = select(Recipe).where(Recipe.id == id)
    result = await session.execute(stmt)
    recipe = result.scalars().first()

    return recipe
