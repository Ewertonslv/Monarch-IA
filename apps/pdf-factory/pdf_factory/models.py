from __future__ import annotations

from pydantic import BaseModel, Field


class BriefInput(BaseModel):
    title: str = Field(min_length=3)
    audience: str = Field(min_length=3)
    objective: str = Field(min_length=3)
    tone: str = Field(default="pratico")
    format_hint: str = Field(default="guia")
    key_points: list[str] = Field(default_factory=list)
    call_to_action: str | None = None


class DocumentSection(BaseModel):
    heading: str
    summary: str
    bullets: list[str] = Field(default_factory=list)


class DocumentPlan(BaseModel):
    slug: str
    title: str
    subtitle: str
    audience: str
    objective: str
    sections: list[DocumentSection]
    call_to_action: str | None = None

