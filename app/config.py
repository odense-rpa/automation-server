from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    database_url: str = "sqlite:///automation.db"
    encryption_key: str = "set me in the env file"
    password_salt: str = "set me in the env file"

    jwt_secret_key: str = "set me in the env file"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30    
    
    

settings = Settings()
