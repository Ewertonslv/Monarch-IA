from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class OfferAngle:
    title: str
    problem: str
    promise: str
    audience: str
    call_to_action: str


@dataclass(slots=True)
class VideoScript:
    hook: str
    beats: list[str] = field(default_factory=list)
    close: str = ""


@dataclass(slots=True)
class ValidationPlan:
    product_title: str
    offer_angle: OfferAngle
    video_script: VideoScript
    checklist: list[str] = field(default_factory=list)
