from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    debug: bool = False
    database_url: str = "postgresql://localhost:5432/ats"
    encryption_key: str = "set me in the env file"
    password_salt: str = "set me in the env file"
    test_database_url: str = "postgresql://localhost:5432/ats_test"
    

settings = Settings()
