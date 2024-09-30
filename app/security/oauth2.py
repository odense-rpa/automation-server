from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
#oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="token", tokenUrl="token",auto_error=False)

