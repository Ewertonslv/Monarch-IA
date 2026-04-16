from instagram_automation.models import ResearchInput
from instagram_automation.pipeline import (
    build_content_angles,
    build_publication_checklist,
    choose_queue_item,
    render_caption_brief,
    slugify,
)


def test_slugify_normalizes_instagram_title():
    assert slugify("Autoridade para Reels 2026!") == "autoridade-para-reels-2026"


def test_build_content_angles_creates_one_angle_per_pillar():
    research = ResearchInput(
        niche="marketing de conteudo",
        objective="gerar mais leads qualificados",
        audience="criadores e operadores digitais",
        content_pillars=["educacao", "prova", "bastidores"],
        signals=[
            "Posts com contexto performam melhor que dicas soltas",
            "Reels curtos com tese forte elevam retencao",
        ],
        references=["concorrentes", "casos reais"],
    )

    angles = build_content_angles(research)

    assert len(angles) == 3
    assert angles[0].pillar == "educacao"
    assert "gerar mais leads qualificados" in angles[0].hook


def test_choose_queue_item_defaults_to_safe_approval_flow():
    research = ResearchInput(
        niche="instagram b2b",
        objective="criar um calendario de posts mais consistente",
        audience="equipes pequenas de marketing",
        content_pillars=["educacao"],
    )

    item = choose_queue_item(research, [])

    assert item.status == "awaiting_approval"
    assert item.review_notes
    assert item.hashtags[0] == "#instagramb2b"


def test_render_caption_brief_contains_cta_and_hashtags():
    research = ResearchInput(
        niche="negocios locais",
        objective="atrair atendimento qualificado",
        audience="donos de negocio",
        content_pillars=["oferta"],
        call_to_action="Convide a pessoa a pedir o diagnostico pelo direct.",
    )

    item = choose_queue_item(research, build_content_angles(research))
    brief = render_caption_brief(item)

    assert "## CTA" in brief
    assert "#negocioslocais" in brief
    assert "diagnostico pelo direct" in brief


def test_publication_checklist_keeps_manual_review_steps():
    research = ResearchInput(
        niche="criacao de conteudo",
        objective="publicar com mais consistencia",
        audience="social medias",
    )

    item = choose_queue_item(research, build_content_angles(research))
    checklist = build_publication_checklist(item)

    assert checklist.items[0] == "Revisar o conteudo final manualmente antes de publicar."
    assert any("politicas da plataforma" in step for step in checklist.items)
