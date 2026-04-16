from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DiscoverySource:
    name: str
    channel: str
    trust_level: str = "medium"


@dataclass(slots=True)
class ProductCandidate:
    title: str
    category: str
    source: str
    price: float
    estimated_sale_price: float
    visual_hook: int
    novelty: int
    demonstration_ease: int
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoredCandidate:
    slug: str
    title: str
    category: str
    source: str
    margin_ratio: float
    score: float
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProductShortlist:
    title: str
    items: list[ScoredCandidate] = field(default_factory=list)
