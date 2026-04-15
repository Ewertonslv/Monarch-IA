from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Monarch Core", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8010, alias="APP_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://monarch:monarch@postgres:5432/monarch",
        alias="DATABASE_URL",
    )
    cors_origins: list[str] = Field(default=["*"], alias="CORS_ORIGINS")
    auto_seed: bool = Field(default=False, alias="AUTO_SEED")
    api_key: str | None = Field(default=None, alias="MONARCH_CORE_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
