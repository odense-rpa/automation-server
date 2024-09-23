import base64
from datetime import datetime, timedelta

from typing import Optional


from fastapi.param_functions import Form
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class OAuth2ClientCredentials:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret


def resolve_client_credentials(request: Request) -> Optional[OAuth2ClientCredentials]:
    # If the header has a basic auth, we will decode client credentials and secret from there
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Basic "):
        encoded = authorization.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        client_id, client_secret = decoded.split(":")

        return OAuth2ClientCredentials(client_id=client_id, client_secret=client_secret)

    return None


def resolve_form_credentials(
    username: Optional[str] = Form(None), password: Optional[str] = Form(None)
) -> Optional[OAuth2PasswordRequestForm]:
    if username and password:
        return OAuth2PasswordRequestForm(username=username, password=password)

    return None
