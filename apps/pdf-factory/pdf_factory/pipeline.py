from __future__ import annotations

import re

from pdf_factory.models import BriefInput, DocumentPlan, DocumentSection


DEFAULT_SECTION_HEADINGS = [
    "Panorama inicial",
    "Fundamentos",
    "Plano de aplicacao",
    "Checklist final",
]


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "documento"


def build_document_plan(brief: BriefInput) -> DocumentPlan:
    points = list(brief.key_points)
    sections: list[DocumentSection] = []

    for index, heading in enumerate(DEFAULT_SECTION_HEADINGS):
        section_points = points[index:: len(DEFAULT_SECTION_HEADINGS)] or [
            f"Aplicar {brief.objective.lower()} com foco em {brief.audience.lower()}."
        ]
        sections.append(
            DocumentSection(
                heading=heading,
                summary=_build_section_summary(brief, heading),
                bullets=section_points[:4],
            )
        )

    subtitle = (
        f"{brief.format_hint.title()} para {brief.audience.lower()} com foco em {brief.objective.lower()}."
    )

    return DocumentPlan(
        slug=slugify(brief.title),
        title=brief.title.strip(),
        subtitle=subtitle,
        audience=brief.audience.strip(),
        objective=brief.objective.strip(),
        sections=sections,
        call_to_action=brief.call_to_action,
    )


def render_markdown(plan: DocumentPlan) -> str:
    lines = [
        f"# {plan.title}",
        "",
        plan.subtitle,
        "",
        f"Publico: {plan.audience}",
        f"Objetivo: {plan.objective}",
    ]

    for section in plan.sections:
        lines.extend(
            [
                "",
                f"## {section.heading}",
                "",
                section.summary,
            ]
        )
        if section.bullets:
            lines.append("")
            lines.extend(f"- {bullet}" for bullet in section.bullets)

    if plan.call_to_action:
        lines.extend(
            [
                "",
                "## Proximo passo",
                "",
                plan.call_to_action,
            ]
        )

    return "\n".join(lines).strip() + "\n"


def build_output_filename(plan: DocumentPlan, extension: str = "md") -> str:
    safe_extension = extension.strip(".").lower() or "md"
    return f"{plan.slug}.{safe_extension}"


def _build_section_summary(brief: BriefInput, heading: str) -> str:
    return (
        f"{heading} pensado para um material em tom {brief.tone.lower()}, "
        f"orientado a {brief.audience.lower()} e focado em {brief.objective.lower()}."
    )

