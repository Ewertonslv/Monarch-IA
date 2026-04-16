"""Achadinhos — descoberta, catalogacao e priorizacao de produtos fisicos."""
from achadinhos.models import ProductCandidate, ProductShortlist, ScoredCandidate
from achadinhos.pipeline import build_shortlist, render_shortlist_markdown, score_candidate, slugify

__all__ = [
    "ProductCandidate",
    "ScoredCandidate",
    "ProductShortlist",
    "score_candidate",
    "build_shortlist",
    "render_shortlist_markdown",
    "slugify",
]
