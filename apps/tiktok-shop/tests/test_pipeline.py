"""Testes para pipeline do TikTok Shop."""
from dataclasses import dataclass

from tiktok_shop.pipeline import build_offer_angle, build_validation_plan, build_video_script, render_validation_plan


@dataclass(slots=True)
class _DummyCandidate:
    slug: str
    title: str
    category: str
    source: str
    margin_ratio: float
    score: float
    strengths: list
    risks: list


def _candidate() -> _DummyCandidate:
    return _DummyCandidate(
        slug="mini-projetor-portatil",
        title="Mini Projetor Portatil",
        category="eletronicos",
        source="shortlist local",
        margin_ratio=1.49,
        score=8.75,
        strengths=["Apelo visual alto."],
        risks=[],
    )


def test_build_offer_angle_uses_candidate_title():
    angle = build_offer_angle(_candidate())
    assert "Mini Projetor Portatil" in angle.title
    assert "solucao simples" in angle.promise


def test_build_video_script_contains_hook_and_beats():
    candidate = _candidate()
    angle = build_offer_angle(candidate)
    script = build_video_script(candidate, angle)
    assert "mini projetor portatil" in script.hook.lower()
    assert len(script.beats) == 3


def test_build_validation_plan_keeps_checklist():
    plan = build_validation_plan(_candidate())
    assert plan.product_title == "Mini Projetor Portatil"
    assert any("margem suporta" in item for item in plan.checklist)


def test_render_validation_plan_contains_sections():
    plan = build_validation_plan(_candidate())
    markdown = render_validation_plan(plan)
    assert "## Angulo de oferta" in markdown
    assert "## Script curto" in markdown
    assert "## Checklist de validacao" in markdown
