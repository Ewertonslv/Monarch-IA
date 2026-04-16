"""Configuracoes do Achadinhos."""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    catalog_file: Path = Path("./catalog.json")
    shortlist_dir: Path = Path("./output")

    model_config = {"env_prefix": "ACHADINHOS_"}


settings = Settings()
