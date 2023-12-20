import re

from fastapi.templating import Jinja2Templates
from fastapi.datastructures import URL
from markupsafe import Markup

templates = Jinja2Templates("templates")
templates.env.globals["URL"] = URL
templates.env.globals["str"] = str


def nl2br(value: str) -> Markup:
    """Filter that converts line breaks into HTML `<br>` and `<p>` tags. Taken from Jinja docs."""
    br = Markup("<br>\n")

    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}</p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return Markup(result)


templates.env.filters["nl2br"] = nl2br
