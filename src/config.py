from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    DATABASE_URL: str = "sqlite:///./patients.db"
    LOG_LEVEL: str = "INFO"
    APP_TITLE: str = "Patient Registration API"
    APP_VERSION: str = "1.0.0"
    BACKEND_URL: str = "https://YOUR_BACKEND_URL"
    ENVIRONMENT: str = "development"

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
