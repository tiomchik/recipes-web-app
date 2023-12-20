from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Depends, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_302_FOUND
from starlette.templating import _TemplateResponse
from sqlalchemy.ext.asyncio import AsyncSession
from json.decoder import JSONDecodeError

from pages import templates
from auth.utils import check_email, check_password, check_passwords, _login
from auth.auth_config import optional_current_user
from config import PROTOCOL, HOST, PORT
from database import User, get_async_session
from recipes.router import (
    _create_recipe, _get_recipes, _update_recipe, _delete_recipe
)
from recipes.schemas import RecipeCreate, RecipeResponse
from recipes.utils import validate_recipe_fields
from base_utils import post, show_errors

router = APIRouter(
    tags=["Pages"],
)


@router.get("/")
async def index(
    request: Request,
    page: int = 1, session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user),
) -> _TemplateResponse:
    """Home page."""
    context = {"request": request, "user": user}
    try:
        recipes = await _get_recipes(session, page=page)
    except HTTPException:
        recipes = None
    else:
        context["paginator"] = recipes.pop()

    context["recipes"] = recipes

    return templates.TemplateResponse("index.html", context)


@router.get("/register/")
async def register(
    request: Request, user: User = Depends(optional_current_user)
) -> _TemplateResponse:
    """Register page with form."""
    return templates.TemplateResponse(
        "auth/register.html", context={"request": request, "user": user}
    )


@router.post("/register/", response_model=None)
async def register(
    request: Request, username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()], password1: Annotated[str, Form()],
    user: User = Depends(optional_current_user)
) -> _TemplateResponse | RedirectResponse:
    """Processes a data from register page form."""
    errors = []

    # Fields validation
    if user:
        errors.append("You already authorized")
    if not username:
        errors.append("Username field is required")
    elif len(username) < 4:
        errors.append("Username is too short (less than 4 characters)")
    elif len(username) > 30:
        errors.append("Username is too long (more than 30 characters)")

    await check_email(email, errors)

    await check_passwords(password, password1, errors)

    if errors:
        return show_errors(
            request, templates, user, errors, "auth/register.html"
        )

    # Creating a new user
    user_dict = {
        "username": username, "email": email, "password": password
    }
    try:
        user = await post(f"{PROTOCOL}://{HOST}:{PORT}/auth/register", json=user_dict)
    # If user already exists, but occurs SQLAlchemy exception
    except JSONDecodeError:
        errors.append("User already exists")
        return show_errors(
            request, templates, user, errors, "auth/register.html"
        )
    else:
        # Some more validations
        if user.get("detail") == "REGISTER_USER_ALREADY_EXISTS":
            errors.append("User already exists")
        elif user.get("detail") and user.get("detail").get("ctx").get("reason"):
            errors.append(user["detail"]["ctx"]["reason"])

    if errors:
        return show_errors(
            request, templates, user, errors, "auth/register.html"
        )

    return await _login(request, templates, data={
        "username": user_dict["email"],
        "password": user_dict["password"]
    }, after_register=True)


@router.get("/login/")
async def login(
    request: Request, user: User = Depends(optional_current_user)
) -> _TemplateResponse:
    """Login page with form."""
    return templates.TemplateResponse(
        "auth/login.html", context={"request": request, "user": user}
    )


@router.post("/login/", response_model=None)
async def login(
    request: Request, email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user: User = Depends(optional_current_user)
) -> _TemplateResponse | RedirectResponse:
    """Processes a data from login page form."""
    errors = []

    if user:
        errors.append("You already authorized")

    await check_email(email, errors)

    await check_password(password, errors)

    if errors:
        return show_errors(
            request, templates, user, errors, "auth/login.html"
        )

    return await _login(request, templates, data={
        "username": email, "password": password
    })


@router.get("/logout/", response_model=None)
async def logout(
    request: Request, user: User = Depends(optional_current_user)
) -> RedirectResponse | _TemplateResponse:
    """Logout page."""
    if not user:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    response = templates.TemplateResponse(
        "/auth/logout.html", {"request": request}
    )
    response.delete_cookie("fastapiusersauth")

    return response


@router.get("/create/", response_model=None)
async def create(
    request: Request, user: User = Depends(optional_current_user)
) -> RedirectResponse | _TemplateResponse:
    """Create recipe page with form."""
    if not user:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        "/recipes/add-recipe.html", {"request": request, "user": user}
    )


@router.post("/create/", response_model=None)
async def create(
    request: Request, headling: Annotated[str, Form()],
    text: Annotated[str, Form()],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
) -> _TemplateResponse | RedirectResponse:
    """Processes a data from create recipe page form."""
    errors = []

    # Fields validation
    if not user:
        errors.append("You aren't authorized")

    await validate_recipe_fields(headling, text, errors)

    if errors:
        return show_errors(
            request, templates, user, errors, "/recipes/add-recipe.html"
        )

    # Creating recipe
    recipe = await _create_recipe(session, headling, text, user.id)

    return RedirectResponse(
        f"/recipe/{recipe.id}/", status_code=HTTP_302_FOUND
    )


@router.get("/recipe/{id}/")
async def recipe(
    request: Request, id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
) -> _TemplateResponse:
    """Recipe page."""
    context = {"request": request, "user": user}

    try:
        recipe = await _get_recipes(session, id=id)
    except HTTPException:
        return templates.TemplateResponse(
            "404.html", context, status_code=HTTP_404_NOT_FOUND
        )

    context["recipe"] = recipe
    recipes = await _get_recipes(session, size=3)
    recipes.pop()
    context["recipes"] = recipes
    

    return templates.TemplateResponse("/recipes/recipe.html", context)


@router.get("/update/{id}/", response_model=None)
async def update(
    request: Request, id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
) -> _TemplateResponse | RedirectResponse:
    """Update recipe page with form."""
    context = {"request": request, "user": user}

    try:
        recipe = await _get_recipes(session, id=id)
    except HTTPException:
        return templates.TemplateResponse(
            "404.html", context, status_code=HTTP_404_NOT_FOUND
        )

    if not user or user.username != recipe.author:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    context["recipe"] = recipe
    return templates.TemplateResponse("/recipes/update-recipe.html", context)


@router.post("/update/{id}/", response_model=None)
async def update(
    request: Request, id: int, headling: Annotated[str, Form()],
    text: Annotated[str, Form()],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
) -> RedirectResponse | _TemplateResponse:
    """Processes a data from update recipe page form."""
    errors = []
    recipe = await _get_recipes(session, id=id)

    # Fields validation
    if not user:
        errors.append("You aren't authorized")
    elif user.username != recipe.author:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    await validate_recipe_fields(headling, text, errors)

    if errors:
        return show_errors(
            request, templates, user, errors, "/recipes/update-recipe.html"
        )

    updated_recipe = RecipeCreate(headling=headling, text=text)
    api_response = await _update_recipe(
        session, user, id, updated_recipe
    )

    return RedirectResponse(
        f"/recipe/{api_response.id}/", status_code=HTTP_302_FOUND
    )


@router.get("/delete/{id}/", response_model=None)
async def delete(
    request: Request, id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
) -> _TemplateResponse | RedirectResponse:
    """Delete recipe page."""
    context = {"request": request, "user": user}
    try:
        recipe = await _get_recipes(session, id=id)
    except HTTPException:
        return templates.TemplateResponse(
            "404.html", context, status_code=HTTP_404_NOT_FOUND
        )

    if user.username != recipe.author:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    await _delete_recipe(session, user, id)

    return templates.TemplateResponse("/recipes/delete-recipe.html", context)


@router.get("/random/")
async def random_recipe(
    request: Request, session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse:
    """Getting random recipe and redirects to this page."""
    recipe = await _get_recipes(session, random=True)

    return RedirectResponse(
        f"/recipe/{recipe.id}/", status_code=HTTP_302_FOUND
    )


@router.get("/search/")
async def search(
    request: Request, search_query: str, page: int = 1,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(optional_current_user)
):
    """Searches for a recipe that matches the `search_query`."""
    context = {
        "request": request, "user": user, "search_query": search_query
    }

    try:
        recipes = await _get_recipes(session, search_query, page=page)
    except HTTPException:
        recipes = None
    else:
        context["recipes"] = recipes
        context["paginator"] = recipes.pop()

    return templates.TemplateResponse("search.html", context)
