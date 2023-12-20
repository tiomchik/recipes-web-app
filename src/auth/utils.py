from typing import Any, Generator

from email_validator import validate_email, EmailNotValidError
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from config import PROTOCOL, HOST, PORT
from database import User, get_async_session
from base_utils import post, show_errors


async def get_user_db(
    session: AsyncSession = Depends(get_async_session)
) -> Generator[SQLAlchemyUserDatabase[User, Any], Any, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def check_email(email: str, errors: list) -> None:
    """Checks passed email and adds errors in `errors` list."""
    if not email:
        errors.append("Email field is required")
    try:
        validate_email(email)
    except EmailNotValidError:
        errors.append("The part after the @-sign is not valid. It is not within a valid top-level domain")


async def check_passwords(
    password: str, password1: str, errors: list
) -> None:
    """Checks passed passwords and adds errors in `errors` list."""
    if not password or not password1:
        errors.append("Password fields is required")
    elif password != password1:
        errors.append("Passwords don't match")
    await check_password(password, errors)


async def check_password(password: str, errors: list) -> None:
    """Checks passed password and adds errors in `errors` list."""
    if len(password) < 8:
        errors.append("Password is too short (less than 8 characters)")
    elif len(password) > 30:
        errors.append("Password is too long (more than 30 characters)")


async def _login(
    request: Request, templates: Jinja2Templates, data: dict,
    after_register: bool = False
) -> _TemplateResponse | RedirectResponse:
    """User login."""
    logged_user = await post(
        f"{PROTOCOL}://{HOST}:{PORT}/auth/jwt/login", data=data
    )

    if not after_register and isinstance(logged_user, dict):
        if logged_user.get("detail") == "LOGIN_BAD_CREDENTIALS":
            errors = ["Invalid credentials"]
            return show_errors(request, templates, errors, "auth/login.html")

    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        key="fastapiusersauth",
        value=logged_user.cookies["fastapiusersauth"]
    )

    return response
