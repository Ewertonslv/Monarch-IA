from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ResearchInput:
    niche: str
    objective: str
    audience: str
    content_pillars: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    call_to_action: str = "Direcione a pessoa para o proximo passo com clareza."


@dataclass(slots=True)
class ContentAngle:
    title: str
    hook: str
    format_hint: str
    pillar: str
    rationale: str
    source_signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class QueueItem:
    slug: str
    title: str
    hook: str
    format_hint: str
    pillar: str
    objective: str
    audience: str
    caption_outline: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    call_to_action: str = ""
    status: str = "awaiting_approval"
    approval_channel: str = "telegram"
    revision_count: int = 0
    feedback_history: list[str] = field(default_factory=list)
    draft_caption: str = ""
    review_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PublicationChecklist:
    title: str
    items: list[str] = field(default_factory=list)
