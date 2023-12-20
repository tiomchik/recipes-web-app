from typing import Any

import httpx

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from database import User


async def post(
    url: str, data: dict | None = None, json: dict | None = None
) -> Any | httpx.Response:
    """Sends a `POST` request to passed url and returns a JSON response or `Reponse` instance if status code 204."""
    async with httpx.AsyncClient() as client:
        if json:
            response = await client.post(url, json=json)
        elif data:
            response = await client.post(url, data=data)
        else:
            return "bro u forgot to pass data or json:("

        if response.status_code != 204:
            return response.json()

        return response


def show_errors(
    request: Request, templates: Jinja2Templates, user: User, errors: list,
    template: str
) -> _TemplateResponse:
    """Returns a `TemplateResponse` with errors."""
    return templates.TemplateResponse(
        template, context={
            "request": request, "user": user, "errors": errors
        }
    )
