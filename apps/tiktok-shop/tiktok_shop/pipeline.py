from __future__ import annotations

from typing import Any

from tiktok_shop.models import OfferAngle, ValidationPlan, VideoScript


def build_offer_angle(
    candidate: Any,
    *,
    audience: str = "compradores por impulso com interesse visual",
) -> OfferAngle:
    return OfferAngle(
        title=f"Oferta inicial para {candidate.title}",
        problem="A maioria das ofertas parece generica e nao mostra beneficio rapido.",
        promise=(
            f"Apresentar {candidate.title} como uma solucao simples, visual e facil de entender "
            f"em poucos segundos."
        ),
        audience=audience,
        call_to_action="Convide a pessoa a abrir o link ou pedir mais detalhes imediatamente.",
    )


def build_video_script(candidate: Any, angle: OfferAngle) -> VideoScript:
    return VideoScript(
        hook=f"Voce precisa ver como {candidate.title.lower()} chama atencao em segundos.",
        beats=[
            f"Mostrar o produto em uso com foco no beneficio principal de {candidate.category.lower()}.",
            "Comparar rapidamente o antes e depois ou o problema e a solucao.",
            f"Refocar no apelo visual e na rapidez de entendimento da oferta: {angle.promise}",
        ],
        close=angle.call_to_action,
    )


def build_validation_plan(candidate: Any) -> ValidationPlan:
    angle = build_offer_angle(candidate)
    script = build_video_script(candidate, angle)
    checklist = [
        "Confirmar se a margem suporta teste inicial de oferta.",
        "Garantir que o video deixa o beneficio evidente nos primeiros segundos.",
        "Validar pagina, link ou canal de conversao antes de publicar.",
        "Registrar CTR, comentarios e sinais de compra apos a primeira rodada.",
    ]
    return ValidationPlan(
        product_title=candidate.title,
        offer_angle=angle,
        video_script=script,
        checklist=checklist,
    )


def render_validation_plan(plan: ValidationPlan) -> str:
    lines = [
        f"# {plan.product_title}",
        "",
        "## Angulo de oferta",
        "",
        f"- Titulo: {plan.offer_angle.title}",
        f"- Problema: {plan.offer_angle.problem}",
        f"- Promessa: {plan.offer_angle.promise}",
        f"- Publico: {plan.offer_angle.audience}",
        "",
        "## Script curto",
        "",
        f"- Hook: {plan.video_script.hook}",
    ]
    lines.extend(f"- Beat: {beat}" for beat in plan.video_script.beats)
    lines.extend(
        [
            f"- Fechamento: {plan.video_script.close}",
            "",
            "## Checklist de validacao",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in plan.checklist)
    return "\n".join(lines).strip() + "\n"
