"""Renderizacao HTML e PDF."""
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pdf_factory.config import settings
from pdf_factory.models import DocumentPlan

logger = logging.getLogger(__name__)

_env: Environment | None = None


def _get_env() -> Environment:
    global _env
    if _env is None:
        template_dir = settings.template_dir
        if template_dir.exists():
            _env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(["html", "xml"]),
            )
        else:
            _env = Environment(autoescape=select_autoescape(["html", "xml"]))
    return _env


def reset_env() -> None:
    global _env
    _env = None


def render_html(plan: DocumentPlan, template: str = "minimal") -> str:
    """Renderiza o plano em HTML usando o template especificado."""
    template_dir = settings.template_dir
    if template_dir.exists():
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
    else:
        env = Environment(autoescape=select_autoescape(["html", "xml"]))

    try:
        template_obj = env.get_template(f"{template}.html")
    except Exception as e:
        logger.warning("Template '%s' nao encontrado, usando 'minimal': %s", template, e)
        template_obj = env.get_template("minimal.html")

    return template_obj.render(plan=plan)


def render_pdf(html_content: str, output_path: Path) -> bool:
    """Gera PDF a partir de HTML. Retorna True se bem-sucedido."""
    try:
        import weasyprint

        from weasyprint import HTML  # type: ignore[import]

        HTML(string=html_content).write_pdf(str(output_path))
        return True
    except ImportError:
        logger.warning("WeasyPrint nao instalado. Instale com: pip install weasyprint")
        return False
    except OSError:
        logger.warning("WeasyPrint nao conseguiu carregar bibliotecas nativas (GTK). Use Docker ou instale as dependencias no Linux.")
        return False
    except Exception as exc:
        logger.warning("Erro ao gerar PDF: %s", exc)
        return False
