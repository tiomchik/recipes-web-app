from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from auth.auth_config import fastapi_users, auth_backend
from auth.schemas import UserRead, UserCreate
from config import limiter
from recipes.router import router as recipes_router
from pages.router import router as pages_router

app = FastAPI(title="Recipes")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Static files
if __name__ == "main":
    app.mount(f"/static/", StaticFiles(directory="static"), name="static")

# Auth routers
auth_router = fastapi_users.get_auth_router(auth_backend)
app.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"],
)

register_router = fastapi_users.get_register_router(UserRead, UserCreate)
app.include_router(
    register_router,
    prefix="/auth",
    tags=["auth"],
)

# Other routers
app.include_router(recipes_router)
app.include_router(pages_router)
