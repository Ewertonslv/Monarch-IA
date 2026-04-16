"""Testes para renderizacao HTML e PDF."""
import tempfile
from pathlib import Path

from pdf_factory.models import BriefInput, DocumentPlan, DocumentSection
from pdf_factory.pipeline import build_document_plan
from pdf_factory.render import render_html, render_pdf


def _make_plan() -> DocumentPlan:
    brief = BriefInput(
        title="Guia de Teste",
        audience="desenvolvedores",
        objective="validar renderizacao",
        tone="tecnico",
        format_hint="checklist",
        call_to_action="Execute o checklist agora.",
        key_points=["Ponto 1", "Ponto 2", "Ponto 3", "Ponto 4"],
    )
    return build_document_plan(brief)


def test_render_html_minimal_template():
    plan = _make_plan()
    html = render_html(plan, template="minimal")
    assert plan.title in html
    assert plan.audience in html
    assert plan.objective in html
    assert "<!DOCTYPE html>" in html


def test_render_html_sales_template():
    plan = _make_plan()
    html = render_html(plan, template="sales")
    assert plan.title in html
    assert "Proximo Passo" in html or "Acao Recomendada" in html


def test_render_html_dark_template():
    plan = _make_plan()
    html = render_html(plan, template="dark")
    assert plan.title in html
    assert "#0f0f0f" in html


def test_render_html_fallback_unknown_template():
    plan = _make_plan()
    html = render_html(plan, template="inexistente")
    assert plan.title in html


def test_render_pdf_with_weasyprint():
    plan = _make_plan()
    html = render_html(plan)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    ok = render_pdf(html, tmp_path)
    if ok:
        assert tmp_path.exists()
        assert tmp_path.stat().st_size > 0
    tmp_path.unlink(missing_ok=True)


def test_render_html_contains_all_sections():
    plan = _make_plan()
    html = render_html(plan)
    for section in plan.sections:
        assert section.heading in html


def test_render_html_cta_only_when_present():
    brief_without_cta = BriefInput(
        title="Sem CTA",
        audience="teste",
        objective="teste",
    )
    plan = build_document_plan(brief_without_cta)
    html = render_html(plan)
    assert "Proximo Passo" not in html
    assert "Acao Recomendada" not in html


def test_render_html_with_cta():
    plan = _make_plan()
    html = render_html(plan)
    assert "Execute o checklist agora." in html
