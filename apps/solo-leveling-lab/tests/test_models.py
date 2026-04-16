"""Testes para modelos do Solo Leveling Lab."""
from solo_leveling_lab.models import ExperimentCycle, LabBrief, LabExperiment
from solo_leveling_lab.pipeline import build_experiment, build_experiment_cycle


def test_lab_brief_fields():
    b = LabBrief(thesis="tese", format_hint="video", objective="obj")
    assert b.thesis == "tese"
    assert b.inspirations == []


def test_lab_experiment_defaults():
    e = LabExperiment(title="T", concept="C", artifact_outline=["a1"])
    assert e.validation_signal == ""


def test_experiment_cycle_defaults():
    c = ExperimentCycle(title="T", next_steps=["n1"])
    assert c.learnings_to_capture == []


def test_build_experiment_uses_format():
    b = LabBrief(thesis="t", format_hint="animatic", objective="o")
    e = build_experiment(b)
    assert "animatic" in e.title.lower()
    assert e.artifact_outline


def test_build_experiment_cycle_contains_next_steps():
    b = LabBrief(thesis="t", format_hint="f", objective="o")
    e = build_experiment(b)
    c = build_experiment_cycle(e)
    assert len(c.next_steps) == 3
    assert len(c.learnings_to_capture) == 3
