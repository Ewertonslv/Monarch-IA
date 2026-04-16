"""Testes para modelos do Achadinhos."""
from achadinhos.models import ProductCandidate, ScoredCandidate
from achadinhos.pipeline import score_candidate


def test_product_candidate_all_fields():
    candidate = ProductCandidate(
        title="Teste",
        category="categoria",
        source="fonte",
        price=100.0,
        estimated_sale_price=250.0,
        visual_hook=7,
        novelty=8,
        demonstration_ease=6,
        notes=["obs1", "obs2"],
    )
    assert candidate.title == "Teste"
    assert candidate.price == 100.0


def test_score_candidate_full():
    candidate = ProductCandidate(
        title="Produto Teste",
        category="eletronicos",
        source="fornecedor",
        price=50.0,
        estimated_sale_price=200.0,
        visual_hook=9,
        novelty=9,
        demonstration_ease=9,
    )
    scored = score_candidate(candidate)
    assert scored.score > 7.0
    assert scored.margin_ratio == 3.0
    assert len(scored.strengths) >= 3


def test_score_candidate_low_margin():
    candidate = ProductCandidate(
        title="Margem Baixa",
        category="utilitario",
        source="fornecedor",
        price=100.0,
        estimated_sale_price=105.0,
        visual_hook=3,
        novelty=3,
        demonstration_ease=3,
    )
    scored = score_candidate(candidate)
    assert scored.score < 4.0
    assert any("Margem apertada" in r for r in scored.risks)
    assert scored.margin_ratio == 0.05


def test_score_candidate_zero_price():
    candidate = ProductCandidate(
        title="Zero",
        category="t",
        source="s",
        price=0.0,
        estimated_sale_price=100.0,
        visual_hook=5,
        novelty=5,
        demonstration_ease=5,
    )
    scored = score_candidate(candidate)
    assert scored.margin_ratio == 0.0
