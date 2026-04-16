from pdf_factory.models import BriefInput
from pdf_factory.pipeline import build_document_plan, build_output_filename, render_markdown, slugify


def test_slugify_normalizes_title():
    assert slugify("Guia de Vendas 2026!") == "guia-de-vendas-2026"


def test_build_document_plan_creates_sections():
    brief = BriefInput(
        title="Guia de Reels",
        audience="criadores iniciantes",
        objective="publicar reels com consistencia",
        key_points=[
            "Escolher um nicho claro",
            "Criar uma linha editorial simples",
            "Produzir em lote",
            "Acompanhar sinais de retencao",
        ],
    )

    plan = build_document_plan(brief)

    assert plan.slug == "guia-de-reels"
    assert len(plan.sections) == 4
    assert plan.sections[0].heading == "Panorama inicial"


def test_render_markdown_contains_core_content():
    brief = BriefInput(
        title="Checklist de Produto Digital",
        audience="infoprodutores",
        objective="validar uma primeira oferta",
        call_to_action="Escolha a primeira oferta e publique a pagina hoje.",
    )

    plan = build_document_plan(brief)
    markdown = render_markdown(plan)

    assert "# Checklist de Produto Digital" in markdown
    assert "## Proximo passo" in markdown
    assert "Escolha a primeira oferta" in markdown


def test_build_output_filename_uses_slug():
    brief = BriefInput(
        title="Plano de Oferta Express",
        audience="operadores digitais",
        objective="organizar um PDF de vendas",
    )

    plan = build_document_plan(brief)
    assert build_output_filename(plan) == "plano-de-oferta-express.md"
