from solo_leveling_lab.models import LabBrief
from solo_leveling_lab.pipeline import build_experiment, build_experiment_cycle, render_experiment_plan


def test_build_experiment_uses_thesis_and_format():
    brief = LabBrief(
        thesis="misturar progressao visual com tensao narrativa",
        format_hint="video ensaio curto",
        objective="criar um piloto autoral",
        inspirations=["anime", "motion design"],
    )

    experiment = build_experiment(brief)

    assert "video ensaio curto" in experiment.title.lower()
    assert "misturar progressao visual" in experiment.concept


def test_build_experiment_cycle_contains_next_steps():
    brief = LabBrief(
        thesis="evolucao visual com atmosfera de game",
        format_hint="animatic",
        objective="testar um conceito de serie curta",
    )

    cycle = build_experiment_cycle(build_experiment(brief))

    assert len(cycle.next_steps) == 3
    assert any("primeira versao" in step for step in cycle.next_steps)


def test_render_experiment_plan_contains_sections():
    brief = LabBrief(
        thesis="camadas de progressao simbolica",
        format_hint="storyboard experimental",
        objective="descobrir uma linguagem propria",
    )

    experiment = build_experiment(brief)
    cycle = build_experiment_cycle(experiment)
    markdown = render_experiment_plan(experiment, cycle)

    assert "## Conceito" in markdown
    assert "## Artefato inicial" in markdown
    assert "## Proximo ciclo" in markdown
