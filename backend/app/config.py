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
    
    # Scheduler configuration
    scheduler_enabled: bool = True
    scheduler_interval: int = 10  # seconds between scheduler runs
    scheduler_error_backoff: int = 30  # seconds to wait after scheduler errors
    scheduler_max_parameter_length: int = 1000  # maximum parameter length
    

settings = Settings()
