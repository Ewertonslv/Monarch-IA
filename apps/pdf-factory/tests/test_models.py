"""Testes para modelos."""
import pytest
from pydantic import ValidationError

from pdf_factory.models import BriefInput, DocumentSection, DocumentPlan
from pdf_factory.pipeline import build_document_plan


def test_brief_input_valid():
    brief = BriefInput(
        title="Teste",
        audience="equipe",
        objective="validar",
    )
    assert brief.tone == "pratico"
    assert brief.format_hint == "guia"
    assert brief.key_points == []


def test_brief_input_with_all_fields():
    brief = BriefInput(
        title="Guia Completo",
        audience="vendedores",
        objective="fechar mais ventas",
        tone="urgente",
        format_hint="checklist",
        key_points=["Ponto A", "Ponto B"],
        call_to_action="Venda hoje.",
    )
    assert brief.tone == "urgente"
    assert brief.call_to_action == "Venda hoje."


def test_brief_input_title_too_short():
    with pytest.raises(ValidationError):
        BriefInput(title="ab", audience="equipe", objective="validar")


def test_brief_input_audience_too_short():
    with pytest.raises(ValidationError):
        BriefInput(title="Teste", audience="ab", objective="validar")


def test_document_section_defaults():
    section = DocumentSection(heading="Intro", summary="Resumo")
    assert section.bullets == []


def test_document_plan():
    section = DocumentSection(heading="Teste", summary="Resumo", bullets=["a", "b"])
    plan = DocumentPlan(
        slug="teste",
        title="Teste",
        subtitle="Subtitulo",
        audience="equipe",
        objective="validar",
        sections=[section],
    )
    assert plan.call_to_action is None


def test_build_document_plan_distributes_points():
    brief = BriefInput(
        title="Guia",
        audience="equipe",
        objective="objetivo",
        key_points=["A", "B", "C", "D", "E", "F", "G", "H"],
    )
    plan = build_document_plan(brief)
    assert len(plan.sections) == 4
    assert plan.sections[0].bullets == ["A", "E"]
    assert plan.sections[1].bullets == ["B", "F"]
