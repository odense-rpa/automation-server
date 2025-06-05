from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    database_url: str = "postgresql://localhost:5432/ats"
    encryption_key: str = "set me in the env file"
    password_salt: str = "set me in the env file"
    test_database_url: str = "postgresql://localhost:5432/ats_test"
    
    

settings = Settings()
