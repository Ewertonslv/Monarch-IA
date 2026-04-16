from __future__ import annotations

import re

from instagram_automation.models import ContentAngle, PublicationChecklist, QueueItem, ResearchInput


DEFAULT_FORMATS = ["reel curto", "carrossel", "post de autoridade"]
DEFAULT_REVIEW_NOTES = [
    "Validar se o conteudo respeita as politicas da plataforma.",
    "Conferir se a promessa do post esta alinhada com a oferta real.",
    "Revisar tom, clareza e proximidade com o publico.",
]


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "conteudo-instagram"


def build_content_angles(research: ResearchInput) -> list[ContentAngle]:
    pillars = research.content_pillars or ["educacao", "prova", "oferta"]
    signals = research.signals or [f"Destravar {research.objective.lower()}."]
    references = research.references or [research.niche]

    angles: list[ContentAngle] = []
    for index, pillar in enumerate(pillars):
        signal = signals[index % len(signals)]
        reference = references[index % len(references)]
        format_hint = DEFAULT_FORMATS[index % len(DEFAULT_FORMATS)]
        title = _build_title(pillar, signal)
        angles.append(
            ContentAngle(
                title=title,
                hook=_build_hook(research, signal),
                format_hint=format_hint,
                pillar=pillar,
                rationale=(
                    f"Une o pilar {pillar.lower()} com o sinal '{signal}' e referencia "
                    f"de {reference.lower()} para avancar o objetivo de {research.objective.lower()}."
                ),
                source_signals=[signal, reference],
            )
        )

    return angles


def choose_queue_item(research: ResearchInput, angles: list[ContentAngle]) -> QueueItem:
    selected = angles[0] if angles else build_content_angles(research)[0]
    caption_outline = [
        selected.hook,
        f"Mostre um exemplo pratico ligado a {selected.pillar.lower()}.",
        f"Conecte o conteudo ao objetivo: {research.objective}.",
        research.call_to_action,
    ]
    hashtags = _build_hashtags(research, selected)

    return QueueItem(
        slug=slugify(selected.title),
        title=selected.title,
        hook=selected.hook,
        format_hint=selected.format_hint,
        pillar=selected.pillar,
        objective=research.objective,
        audience=research.audience,
        caption_outline=caption_outline,
        hashtags=hashtags,
        call_to_action=research.call_to_action,
        review_notes=list(DEFAULT_REVIEW_NOTES),
    )


def render_caption_brief(item: QueueItem) -> str:
    lines = [
        f"# {item.title}",
        "",
        f"Formato sugerido: {item.format_hint}",
        f"Pilar: {item.pillar}",
        f"Publico: {item.audience}",
        f"Objetivo: {item.objective}",
        "",
        "## Hook",
        "",
        item.hook,
        "",
        "## Estrutura da legenda",
        "",
    ]
    lines.extend(f"- {point}" for point in item.caption_outline)
    lines.extend(
        [
            "",
            "## CTA",
            "",
            item.call_to_action,
            "",
            "## Hashtags sugeridas",
            "",
            " ".join(item.hashtags),
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_publication_checklist(item: QueueItem) -> PublicationChecklist:
    return PublicationChecklist(
        title=f"Checklist de publicacao: {item.title}",
        items=[
            "Revisar o conteudo final manualmente antes de publicar.",
            "Confirmar que a CTA esta alinhada com a oferta ou objetivo.",
            "Garantir que a capa, thumbnail ou primeiro frame estejam claros.",
            "Validar horario, formato e contexto da postagem.",
            "Registrar feedback e performance apos a publicacao.",
        ]
        + item.review_notes,
    )


def _build_title(pillar: str, signal: str) -> str:
    cleaned_signal = signal.rstrip(".!? ")
    return f"{pillar.title()}: {cleaned_signal}"


def _build_hook(research: ResearchInput, signal: str) -> str:
    return (
        f"Se voce quer {research.objective.lower()}, comece entendendo isto: "
        f"{signal.rstrip('.!? ')}."
    )


def _build_hashtags(research: ResearchInput, angle: ContentAngle) -> list[str]:
    base_tags = [
        _sanitize_hashtag(research.niche),
        _sanitize_hashtag(angle.pillar),
        _sanitize_hashtag(research.objective),
    ]
    return [tag for tag in base_tags if tag]


def _sanitize_hashtag(value: str) -> str:
    compact = re.sub(r"[^a-zA-Z0-9]+", "", value.lower())
    return f"#{compact}" if compact else ""
