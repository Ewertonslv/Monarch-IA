"""Configuracoes do Instagram Automation."""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    queue_file: Path = Path("./queue.json")
    output_dir: Path = Path("./output")
    default_pillars: list[str] = ["educacao", "prova", "oferta"]

    model_config = {"env_prefix": "INSTA_"}


settings = Settings()
