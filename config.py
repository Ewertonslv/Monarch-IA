import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Anthropic
    anthropic_api_key: str = Field(..., validation_alias="ANTHROPIC_API_KEY")

    # GitHub
    github_token: str = Field(..., validation_alias="GITHUB_TOKEN")
    github_repo: str = Field(..., validation_alias="GITHUB_REPO")

    # Telegram
    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., validation_alias="TELEGRAM_CHAT_ID")

    # Web UI
    web_port: int = Field(default=8000, validation_alias="WEB_PORT")
    web_secret_key: str = Field(
        default="change-me-in-production", validation_alias="WEB_SECRET_KEY"
    )
    monarch_core_api_url: str | None = Field(
        default=None, validation_alias="MONARCH_CORE_API_URL"
    )
    monarch_core_api_key: str | None = Field(
        default=None, validation_alias="MONARCH_CORE_API_KEY"
    )
    monarch_core_project_slug: str = Field(
        default="monarch-ai", validation_alias="MONARCH_CORE_PROJECT_SLUG"
    )

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./monarch_ai.db", validation_alias="DATABASE_URL"
    )

    # Behaviour
    max_agent_retries: int = Field(default=3, validation_alias="MAX_AGENT_RETRIES")
    approval_timeout_minutes: int = Field(
        default=60, validation_alias="APPROVAL_TIMEOUT_MINUTES"
    )
    confidence_threshold: float = Field(
        default=0.70, validation_alias="CONFIDENCE_THRESHOLD"
    )

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if not v or v == "":
            raise ValueError("ANTHROPIC_API_KEY is required")
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


config = Config()
