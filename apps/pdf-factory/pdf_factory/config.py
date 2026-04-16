"""Configuracoes do PDF Factory."""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    output_dir: Path = Path("./output")
    template_dir: Path = Path(__file__).parent.parent / "templates"
    default_template: str = "minimal"
    pdf_engine: str = "weasyprint"

    model_config = {"env_prefix": "PDF_FACTORY_"}


settings = Settings()
