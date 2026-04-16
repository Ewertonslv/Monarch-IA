from achadinhos.models import ProductCandidate
from achadinhos.pipeline import build_shortlist, render_shortlist_markdown, score_candidate, slugify


def test_slugify_normalizes_product_name():
    assert slugify("Mini Projetor Portatil 4K!") == "mini-projetor-portatil-4k"


def test_score_candidate_highlights_strengths_for_strong_product():
    candidate = ProductCandidate(
        title="Mini Projetor Portatil",
        category="eletronicos",
        source="fornecedor teste",
        price=120.0,
        estimated_sale_price=299.0,
        visual_hook=9,
        novelty=8,
        demonstration_ease=9,
    )

    scored = score_candidate(candidate)

    assert scored.score > 8
    assert any("Margem potencial forte" in item for item in scored.strengths)
    assert any("facil de demonstrar" in item for item in scored.strengths)


def test_build_shortlist_orders_candidates_by_score():
    candidates = [
        ProductCandidate(
            title="Organizador Simples",
            category="casa",
            source="fonte a",
            price=20.0,
            estimated_sale_price=39.0,
            visual_hook=4,
            novelty=3,
            demonstration_ease=5,
        ),
        ProductCandidate(
            title="Escova Secadora Premium",
            category="beleza",
            source="fonte b",
            price=70.0,
            estimated_sale_price=179.0,
            visual_hook=9,
            novelty=7,
            demonstration_ease=8,
        ),
    ]

    shortlist = build_shortlist(candidates, limit=1)

    assert len(shortlist.items) == 1
    assert shortlist.items[0].title == "Escova Secadora Premium"


def test_render_shortlist_markdown_contains_rank_and_score():
    shortlist = build_shortlist(
        [
            ProductCandidate(
                title="Luminaria Sensorial",
                category="decoracao",
                source="fonte c",
                price=35.0,
                estimated_sale_price=99.0,
                visual_hook=8,
                novelty=8,
                demonstration_ease=7,
            )
        ]
    )

    markdown = render_shortlist_markdown(shortlist)

    assert "# Shortlist inicial de achadinhos" in markdown
    assert "## 1. Luminaria Sensorial" in markdown
    assert "- Score:" in markdown
