from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = Field(alias="ANTHROPIC_API_KEY")
    zapi_instance_id: str = Field(alias="ZAPI_INSTANCE_ID")
    zapi_token: str = Field(alias="ZAPI_TOKEN")
    zapi_client_token: str = Field(alias="ZAPI_CLIENT_TOKEN")
    notion_token: str = Field(alias="NOTION_TOKEN")
    notion_database_id: str = Field(alias="NOTION_DATABASE_ID")
    my_phone_number: str = Field(alias="MY_PHONE_NUMBER")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
