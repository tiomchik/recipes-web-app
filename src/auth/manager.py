from typing import Generator, Any

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin

from database import User
from config import SECRET
from auth.utils import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


async def get_user_manager(user_db=Depends(get_user_db)) -> Generator[UserManager, Any, None]:
    yield UserManager(user_db)
