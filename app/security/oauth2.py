from fastapi.security import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="token", tokenUrl="token",auto_error=False)

