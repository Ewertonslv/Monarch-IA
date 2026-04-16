from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ChannelBrief:
    niche: str
    audience: str
    promise: str
    themes: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TopicIdea:
    title: str
    hook: str
    theme: str
    angle: str


@dataclass(slots=True)
class ScriptDraft:
    title: str
    opening: str
    beats: list[str] = field(default_factory=list)
    closing: str = ""
