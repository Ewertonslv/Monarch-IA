"""CLI para Canal Dark."""
import json
from pathlib import Path

import rich.console
import rich.table
import typer

from canal_dark.models import ChannelBrief, TopicIdea
from canal_dark.pipeline import build_script_draft, build_topic_backlog, choose_priority_topic, render_script

app = typer.Typer(help="Canal Dark — produza pautas e roteiros para canais dark.")
console = rich.console.Console()


@app.command()
def new(
    niche: str = typer.Option(..., "--niche", "-n", help="Nicho do canal"),
    audience: str = typer.Option("publico geral", "--audience", "-a", help="Publico-alvo"),
    promise: str = typer.Option("entreter e informar", "--promise", "-p", help="Promessa do canal"),
    themes: str = typer.Option(
        "curiosidades,ranking,historia,comparacao",
        "--themes",
        help="Temas separados por virgula",
    ),
    output: Path | None = typer.Option(None, "--output", "-o", help="Salvar backlog em arquivo"),
) -> None:
    """Cria backlog inicial de pautas a partir do briefing de canal."""
    brief = ChannelBrief(
        niche=niche,
        audience=audience,
        promise=promise,
        themes=[t.strip() for t in themes.split(",") if t.strip()],
    )

    backlog = build_topic_backlog(brief)

    table = rich.table.Table(title=f"Backlog: {niche}")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Titulo", style="cyan")
    table.add_column("Tema", style="magenta")
    table.add_column("Hook", style="dim")

    for i, topic in enumerate(backlog, 1):
        table.add_row(str(i), topic.title[:40], topic.theme, topic.hook[:50])

    console.print(table)
    console.print(f"\n[dim]{len(backlog)} pautas geradas. Use 'canal-dark script --index {backlog[0].title.split()[0]}' para gerar o roteiro.[/dim]")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Backlog: {niche}\n", f"**Promessa:** {promise}\n", f"**Publico:** {audience}\n\n"]
        for i, topic in enumerate(backlog, 1):
            lines.extend([f"## {i}. {topic.title}\n", f"Hook: {topic.hook}\n", f"Angulo: {topic.angle}\n\n"])
        output.write_text("".join(lines), encoding="utf-8")
        console.print(f"[green]Backlog salvo em: {output}[/green]")


@app.command()
def script(
    topic: str = typer.Option(..., "--topic", "-t", help="Titulo da pauta"),
    niche: str = typer.Option("geral", "--niche", "-n", help="Nicho do canal"),
    audience: str = typer.Option("publico geral", "--audience", "-a", help="Publico-alvo"),
    promise: str = typer.Option("entreter e informar", "--promise", "-p", help="Promessa do canal"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Salvar roteiro em arquivo"),
) -> None:
    """Gera roteiro completo para uma pauta."""
    brief = ChannelBrief(niche=niche, audience=audience, promise=promise)
    backlog = build_topic_backlog(brief)

    selected = next((t for t in backlog if topic.lower() in t.title.lower()), backlog[0])
    script = build_script_draft(selected, brief)
    md = render_script(script)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md, encoding="utf-8")
        console.print(f"[green]Roteiro salvo em: {output}[/green]")
    else:
        console.print(md)


@app.command()
def list_themes(
    niche: str = typer.Option("geral", "--niche", "-n", help="Nicho do canal"),
    audience: str = typer.Option("publico geral", "--audience", "-a", help="Publico-alvo"),
    promise: str = typer.Option("entreter e informar", "--promise", "-p", help="Promessa do canal"),
) -> None:
    """Lista backlog completo de pautas."""
    brief = ChannelBrief(niche=niche, audience=audience, promise=promise)
    backlog = build_topic_backlog(brief)
    priority = choose_priority_topic(backlog)

    console.print(f"\n[bold cyan]Pauta prioritaria:[/bold cyan] {priority.title}")
    console.print(f"[dim]{priority.hook}[/dim]\n")

    for i, topic in enumerate(backlog[1:], 2):
        console.print(f"  {i}. {topic.title} [{topic.theme}]")


if __name__ == "__main__":
    app()
