from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    debug: bool = False
    database_url: str = "postgresql://localhost:5432/ats"
    encryption_key: str = "set me in the env file"
    test_database_url: str = "postgresql://localhost:5432/ats_test"

    # Scheduler configuration
    scheduler_enabled: bool = True
    scheduler_interval: int = 10  # seconds between scheduler runs
    scheduler_error_backoff: int = 30  # seconds to wait after scheduler errors
    scheduler_max_parameter_length: int = 1000  # maximum parameter length

    # Comma-separated list of allowed CORS origins. Empty means same-origin
    # only, which is correct for the shipped compose topology where the
    # frontend and API share an nginx proxy. Set to "*" for development.
    cors_allow_origins: str = ""


settings = Settings()


def cors_origins() -> list[str]:
    """Parse `cors_allow_origins` into the list CORSMiddleware expects.

    Empty (the default) means no origins are allowed, which is correct for
    the shipped compose topology where the frontend and API share an nginx
    proxy and never make a cross-origin request in the first place.
    """
    return [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]
