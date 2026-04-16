import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Anthropic
    anthropic_api_key: str = Field(..., validation_alias="ANTHROPIC_API_KEY")

    # GitHub (optional — omit to run in local-only mode)
    github_token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    github_repo: str | None = Field(default=None, validation_alias="GITHUB_REPO")

    @property
    def github_enabled(self) -> bool:
        """True when a real GitHub repo is configured (not a placeholder)."""
        return bool(
            self.github_token
            and self.github_repo
            and self.github_repo not in ("owner/repo-name", "owner/repo")
        )

    # Telegram
    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., validation_alias="TELEGRAM_CHAT_ID")
    enable_telegram_polling: bool = Field(
        default=True, validation_alias="ENABLE_TELEGRAM_POLLING"
    )

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

    # Local mode — use claude CLI (Pro subscription) instead of API credits
    local_mode: bool = Field(default=False, validation_alias="LOCAL_MODE")

    # Behaviour
    max_agent_retries: int = Field(default=3, validation_alias="MAX_AGENT_RETRIES")
    approval_timeout_minutes: int = Field(
        default=60, validation_alias="APPROVAL_TIMEOUT_MINUTES"
    )
    confidence_threshold: float = Field(
        default=0.70, validation_alias="CONFIDENCE_THRESHOLD"
    )
    hub_read_only: bool = Field(
        default=True, validation_alias="HUB_READ_ONLY"
    )
    implementer_model: str = Field(
        default="claude-sonnet-4-6", validation_alias="IMPLEMENTER_MODEL"
    )
    implementer_max_tokens: int = Field(
        default=3200, validation_alias="IMPLEMENTER_MAX_TOKENS"
    )

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if not v or v == "":
            raise ValueError("ANTHROPIC_API_KEY is required")
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


config = Config()
