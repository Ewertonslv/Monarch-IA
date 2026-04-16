from __future__ import annotations

import re

from achadinhos.models import ProductCandidate, ProductShortlist, ScoredCandidate


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "produto"


def score_candidate(candidate: ProductCandidate) -> ScoredCandidate:
    margin_ratio = _calculate_margin_ratio(candidate.price, candidate.estimated_sale_price)
    margin_score = min(margin_ratio * 10, 10)
    score = round(
        (margin_score * 0.35)
        + (candidate.visual_hook * 0.25)
        + (candidate.novelty * 0.2)
        + (candidate.demonstration_ease * 0.2),
        2,
    )

    strengths: list[str] = []
    risks: list[str] = []

    if margin_ratio >= 1.0:
        strengths.append("Margem potencial forte para teste de oferta.")
    else:
        risks.append("Margem apertada pode limitar testes pagos ou desconto.")

    if candidate.visual_hook >= 8:
        strengths.append("Apelo visual alto para conteudo de descoberta.")
    elif candidate.visual_hook <= 4:
        risks.append("Apelo visual baixo para formatos curtos.")

    if candidate.demonstration_ease >= 8:
        strengths.append("Produto facil de demonstrar em video.")
    elif candidate.demonstration_ease <= 4:
        risks.append("Demonstracao pode exigir criativo mais complexo.")

    if candidate.novelty >= 8:
        strengths.append("Boa sensacao de novidade para chamar atencao.")
    elif candidate.novelty <= 4:
        risks.append("Produto pode parecer comum demais sem angulo forte.")

    return ScoredCandidate(
        slug=slugify(candidate.title),
        title=candidate.title,
        category=candidate.category,
        source=candidate.source,
        margin_ratio=round(margin_ratio, 2),
        score=score,
        strengths=strengths,
        risks=risks,
    )


def build_shortlist(
    candidates: list[ProductCandidate],
    *,
    limit: int = 5,
    title: str = "Shortlist inicial de achadinhos",
) -> ProductShortlist:
    scored = sorted(
        (score_candidate(candidate) for candidate in candidates),
        key=lambda item: item.score,
        reverse=True,
    )
    return ProductShortlist(title=title, items=scored[:limit])


def render_shortlist_markdown(shortlist: ProductShortlist) -> str:
    lines = [f"# {shortlist.title}"]

    for index, item in enumerate(shortlist.items, start=1):
        lines.extend(
            [
                "",
                f"## {index}. {item.title}",
                "",
                f"- Categoria: {item.category}",
                f"- Fonte: {item.source}",
                f"- Score: {item.score}",
                f"- Margem potencial: {item.margin_ratio}",
            ]
        )
        if item.strengths:
            lines.append("- Forcas: " + "; ".join(item.strengths))
        if item.risks:
            lines.append("- Riscos: " + "; ".join(item.risks))

    return "\n".join(lines).strip() + "\n"


def _calculate_margin_ratio(cost_price: float, sale_price: float) -> float:
    if cost_price <= 0:
        return 0.0
    return max(sale_price - cost_price, 0.0) / cost_price
