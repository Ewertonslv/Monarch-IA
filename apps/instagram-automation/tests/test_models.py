"""Testes para modelos do Instagram Automation."""
from instagram_automation.models import ContentAngle, QueueItem, ResearchInput
from instagram_automation.pipeline import build_content_angles, choose_queue_item


def test_research_input_defaults():
    r = ResearchInput(
        niche="teste",
        objective="teste",
        audience="teste",
    )
    assert r.call_to_action == "Direcione a pessoa para o proximo passo com clareza."
    assert r.content_pillars == []
    assert r.signals == []


def test_queue_item_default_status():
    item = QueueItem(
        slug="test",
        title="Teste",
        hook="Hook",
        format_hint="reel",
        pillar="educacao",
        objective="teste",
        audience="teste",
    )
    assert item.status == "awaiting_approval"
    assert item.approval_channel == "telegram"
    assert item.revision_count == 0
    assert item.feedback_history == []


def test_build_content_angles_fills_signals_when_empty():
    r = ResearchInput(
        niche="beleza",
        objective="vender mais",
        audience="mulheres 25-40",
        content_pillars=["educacao"],
    )
    angles = build_content_angles(r)
    assert len(angles) == 1
    assert angles[0].pillar == "educacao"
    assert "vender mais" in angles[0].hook


def test_choose_queue_item_includes_hashtags():
    r = ResearchInput(
        niche="fitness digital",
        objective="gerar leads",
        audience="personal trainers",
        content_pillars=["prova"],
    )
    item = choose_queue_item(r, build_content_angles(r))
    assert item.status == "awaiting_approval"
    assert item.approval_channel == "telegram"
    assert any(h.startswith("#") for h in item.hashtags)
    assert item.caption_outline
    assert item.draft_caption
    assert item.review_notes


def test_build_content_angles_multiple_pillars():
    r = ResearchInput(
        niche="tech",
        objective="vender cursos",
        audience="devs iniciantes",
        content_pillars=["educacao", "prova", "oferta"],
        signals=["Sinal A", "Sinal B", "Sinal C"],
    )
    angles = build_content_angles(r)
    assert len(angles) == 3
    assert angles[0].pillar == "educacao"
    assert angles[1].pillar == "prova"
    assert angles[2].pillar == "oferta"
