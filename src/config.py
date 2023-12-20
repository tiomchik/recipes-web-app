from pathlib import Path
from secrets import token_urlsafe
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

SECRET = token_urlsafe()
PROTOCOL = "http"
HOST = "localhost"
PORT = 8000
