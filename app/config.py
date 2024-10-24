from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    database_url: str = "sqlite:///automation.db"
    encryption_key: str = "set me in the env file"
    password_salt: str = "set me in the env file"

    
    

settings = Settings()
