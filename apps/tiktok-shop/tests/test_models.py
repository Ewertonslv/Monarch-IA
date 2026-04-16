"""Testes para modelos do TikTok Shop."""
from dataclasses import dataclass

from tiktok_shop.models import OfferAngle, ValidationPlan, VideoScript
from tiktok_shop.pipeline import build_offer_angle, build_validation_plan, build_video_script


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


def test_offer_angle_fields():
    c = _DummyCandidate("s", "Teste", "cat", "src", 1.5, 8.0, [], [])
    angle = build_offer_angle(c)
    assert "Teste" in angle.title
    assert angle.call_to_action


def test_video_script_defaults():
    v = VideoScript(hook="Hook", beats=["b1", "b2"])
    assert v.close == ""


def test_validation_plan_fields():
    c = _DummyCandidate("s", "T", "cat", "src", 1.2, 7.5, [], [])
    plan = build_validation_plan(c)
    assert plan.product_title == "T"
    assert len(plan.checklist) == 4


def test_build_video_script_contains_hook():
    c = _DummyCandidate("s", "Proj", "cat", "src", 1.5, 8.0, [], [])
    angle = build_offer_angle(c)
    script = build_video_script(c, angle)
    assert "proj" in script.hook.lower()
    assert len(script.beats) == 3
