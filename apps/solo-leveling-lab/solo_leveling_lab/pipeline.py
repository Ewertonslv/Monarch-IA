from __future__ import annotations

from solo_leveling_lab.models import ExperimentCycle, LabBrief, LabExperiment


def build_experiment(brief: LabBrief) -> LabExperiment:
    inspirations = ", ".join(brief.inspirations) if brief.inspirations else "referencias autorais proprias"
    return LabExperiment(
        title=f"Experimento: {brief.format_hint.title()}",
        concept=(
            f"Aplicar a tese '{brief.thesis}' em um formato {brief.format_hint.lower()} "
            f"com foco em {brief.objective.lower()} e inspiracoes em {inspirations}."
        ),
        artifact_outline=[
            "Definir recorte exato do experimento.",
            "Produzir um primeiro artefato curto ou prototipo.",
            "Registrar o que torna esse experimento autoral e memoravel.",
        ],
        validation_signal="Avaliar se o artefato transmite a tese com clareza e identidade propria.",
    )


def build_experiment_cycle(experiment: LabExperiment) -> ExperimentCycle:
    return ExperimentCycle(
        title=experiment.title,
        next_steps=[
            "Produzir a primeira versao do artefato.",
            "Revisar consistencia entre tese, formato e entrega.",
            "Registrar o que deve mudar no proximo ciclo.",
        ],
        learnings_to_capture=[
            "Quais partes do conceito ficaram fortes ou fracas.",
            "Que tipo de resposta emocional ou estetica o experimento gera.",
            "Se vale expandir, cortar ou redirecionar o formato.",
        ],
    )


def render_experiment_plan(experiment: LabExperiment, cycle: ExperimentCycle) -> str:
    lines = [
        f"# {experiment.title}",
        "",
        "## Conceito",
        "",
        experiment.concept,
        "",
        "## Artefato inicial",
        "",
    ]
    lines.extend(f"- {item}" for item in experiment.artifact_outline)
    lines.extend(
        [
            "",
            "## Sinal de validacao",
            "",
            experiment.validation_signal,
            "",
            "## Proximo ciclo",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in cycle.next_steps)
    lines.extend(
        [
            "",
            "## Aprendizados a capturar",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in cycle.learnings_to_capture)
    return "\n".join(lines).strip() + "\n"
