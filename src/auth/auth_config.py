from fastapi_users.authentication import (
    CookieTransport, JWTStrategy, AuthenticationBackend
)
from fastapi_users import FastAPIUsers

from auth.manager import get_user_manager
from database import User
from config import SECRET

cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
optional_current_user = fastapi_users.current_user(optional=True)
