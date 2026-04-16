from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LabBrief:
    thesis: str
    format_hint: str
    objective: str
    inspirations: list[str] = field(default_factory=list)


@dataclass(slots=True)
class LabExperiment:
    title: str
    concept: str
    artifact_outline: list[str] = field(default_factory=list)
    validation_signal: str = ""


@dataclass(slots=True)
class ExperimentCycle:
    title: str
    next_steps: list[str] = field(default_factory=list)
    learnings_to_capture: list[str] = field(default_factory=list)
