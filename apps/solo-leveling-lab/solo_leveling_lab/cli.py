"""CLI para Solo Leveling Lab."""
from pathlib import Path

import rich.console
import rich.table
import typer

from solo_leveling_lab.models import LabBrief
from solo_leveling_lab.pipeline import build_experiment, build_experiment_cycle, render_experiment_plan

app = typer.Typer(help="Solo Leveling Lab — experimente, produza e registre aprendizados.")
console = rich.console.Console()


@app.command()
def experiment(
    thesis: str = typer.Option(..., "--thesis", "-t", help="Tese criativa"),
    format_hint: str = typer.Option(
        "video ensaio",
        "--format",
        "-f",
        help="Formato do experimento",
    ),
    objective: str = typer.Option("explorar e iterar", "--objective", "-o", help="Objetivo do experimento"),
    inspirations: str = typer.Option("", "--inspirations", "-i", help="Inspiracoes separadas por virgula"),
    output: Path | None = typer.Option(None, "--output", "-O", help="Salvar plano em arquivo"),
) -> None:
    """Cria um novo experimento criativo com plano de execucao."""
    brief = LabBrief(
        thesis=thesis,
        format_hint=format_hint,
        objective=objective,
        inspirations=[ins.strip() for ins in inspirations.split(",") if ins.strip()],
    )

    experiment = build_experiment(brief)
    cycle = build_experiment_cycle(experiment)
    md = render_experiment_plan(experiment, cycle)

    console.print(f"\n[bold cyan]Experimento:[/bold cyan] {experiment.title}\n")
    console.print(f"[dim]{experiment.concept}[/dim]\n")
    console.print("[bold]Artefato:[/bold]")
    for item in experiment.artifact_outline:
        console.print(f"  - {item}")

    console.print(f"\n[bold]Proximo ciclo:[/bold]")
    for i, step in enumerate(cycle.next_steps, 1):
        console.print(f"  {i}. {step}")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md, encoding="utf-8")
        console.print(f"\n[green]Plano salvo em: {output}[/green]")


@app.command()
def cycle(
    thesis: str = typer.Option(..., "--thesis", "-t", help="Tese criativa"),
    format_hint: str = typer.Option("video ensaio", "--format", "-f", help="Formato"),
    objective: str = typer.Option(..., "--objective", "-o", help="Objetivo"),
) -> None:
    """Mostra ciclo de experimento com proximos passos e aprendizados."""
    brief = LabBrief(thesis=thesis, format_hint=format_hint, objective=objective)
    exp = build_experiment(brief)
    cycle = build_experiment_cycle(exp)

    console.print(f"\n[bold cyan]{cycle.title}[/bold cyan]\n")

    console.print("[bold]Proximo ciclo:[/bold]")
    for i, step in enumerate(cycle.next_steps, 1):
        console.print(f"  {i}. {step}")

    console.print("\n[bold]Aprendizados a capturar:[/bold]")
    for i, item in enumerate(cycle.learnings_to_capture, 1):
        console.print(f"  {i}. {item}")


if __name__ == "__main__":
    app()
