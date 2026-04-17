"""CLI para Instagram Automation."""
import json
from pathlib import Path

import rich.console
import rich.table
import typer

from instagram_automation.config import settings
from instagram_automation.models import QueueItem, ResearchInput
from instagram_automation.pipeline import (
    build_content_angles,
    build_publication_checklist,
    choose_queue_item,
    render_caption_brief,
)

app = typer.Typer(help="Instagram Automation - pesquise, proponha, aprove e publique.")
console = rich.console.Console()


def _load_queue() -> list[QueueItem]:
    path = settings.queue_file
    if not path.exists():
        return []
    try:
        return [QueueItem(**item) for item in json.loads(path.read_text(encoding="utf-8"))]
    except Exception:
        return []


def _save_queue(queue: list[QueueItem]) -> None:
    settings.queue_file.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "slug": i.slug,
            "title": i.title,
            "hook": i.hook,
            "format_hint": i.format_hint,
            "pillar": i.pillar,
            "objective": i.objective,
            "audience": i.audience,
            "caption_outline": i.caption_outline,
            "hashtags": i.hashtags,
            "call_to_action": i.call_to_action,
            "status": i.status,
            "approval_channel": i.approval_channel,
            "revision_count": i.revision_count,
            "feedback_history": i.feedback_history,
            "draft_caption": i.draft_caption,
            "review_notes": i.review_notes,
        }
        for i in queue
    ]
    settings.queue_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_queue_item(queue: list[QueueItem], index: int) -> QueueItem:
    if index < 1 or index > len(queue):
        console.print("[red]Indice invalido.[/red]")
        raise typer.Exit(1)
    return queue[index - 1]


@app.command()
def research(
    niche: str = typer.Option(..., "--niche", "-n", help="Nicho"),
    objective: str = typer.Option("gerar valor para o publico", "--objective", "-o", help="Objetivo"),
    audience: str = typer.Option("seguidores do nicho", "--audience", "-a", help="Publico-alvo"),
    pillars: str = typer.Option("educacao,prova,oferta", "--pillars", help="Pilares separados por virgula"),
    cta: str = typer.Option("Direcione para o proximo passo.", "--cta", help="Call to action"),
) -> None:
    """Submete uma pesquisa e adiciona proposta na fila de aprovacao."""
    research_input = ResearchInput(
        niche=niche,
        objective=objective,
        audience=audience,
        content_pillars=[p.strip() for p in pillars.split(",") if p.strip()],
        call_to_action=cta,
    )

    angles = build_content_angles(research_input)
    item = choose_queue_item(research_input, angles)

    queue = _load_queue()
    queue.append(item)
    _save_queue(queue)

    console.print(f"[green]+ Proposta adicionada a fila:[/green] {item.title}")
    console.print(
        "  "
        f"Formato: {item.format_hint} | Pilar: {item.pillar} | "
        f"Status: {item.status} | Canal: {item.approval_channel}"
    )


@app.command()
def queue(
    status: str | None = typer.Option(None, "--status", "-s", help="Filtrar por status"),
) -> None:
    """Lista todas as propostas na fila."""
    queue_items = _load_queue()
    if status:
        queue_items = [i for i in queue_items if i.status == status]

    if not queue_items:
        msg = f"[yellow]Fila vazia ou nenhum item com status '{status or 'todos'}'.[/yellow]"
        console.print(msg)
        return

    status_label = {
        "awaiting_approval": "pending",
        "approved": "approved",
        "published": "published",
        "rejected": "rejected",
        "needs_revision": "needs_revision",
    }

    table = rich.table.Table(title=f"Fila de Conteudo ({len(queue_items)} itens)")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Titulo", style="cyan")
    table.add_column("Formato", style="magenta")
    table.add_column("Pilar", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Revisoes", justify="right", style="yellow")

    for i, item in enumerate(queue_items, 1):
        label = status_label.get(item.status, "unknown")
        table.add_row(
            str(i),
            item.title[:35],
            item.format_hint,
            item.pillar,
            f"{label} {item.status}",
            str(item.revision_count),
        )

    console.print(table)


@app.command()
def brief(
    title: str | None = typer.Option(None, "--title", "-t", help="Titulo da proposta"),
    index: int | None = typer.Option(None, "--index", "-i", help="Numero na fila (1-based)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Salvar em arquivo"),
) -> None:
    """Mostra o caption brief de uma proposta."""
    queue_items = _load_queue()
    if not queue_items:
        console.print("[yellow]Fila vazia.[/yellow]")
        raise typer.Exit(1)

    if index is not None:
        if index < 1 or index > len(queue_items):
            console.print(f"[red]Indice invalido. Use 1 a {len(queue_items)}.[/red]")
            raise typer.Exit(1)
        item = queue_items[index - 1]
    elif title:
        item = next((i for i in queue_items if title.lower() in i.title.lower()), None)
        if not item:
            console.print(f"[red]Proposta '{title}' nao encontrada.[/red]")
            raise typer.Exit(1)
    else:
        item = queue_items[0]

    md = render_caption_brief(item)
    if output:
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        out = settings.output_dir / f"{item.slug}.md"
        out.write_text(md, encoding="utf-8")
        console.print(f"[green]Brief salvo em: {out}[/green]")
    else:
        console.print(md)


@app.command()
def checklist(
    title: str | None = typer.Option(None, "--title", "-t", help="Titulo da proposta"),
    index: int | None = typer.Option(None, "--index", "-i", help="Numero na fila (1-based)"),
) -> None:
    """Mostra o checklist de publicacao de uma proposta."""
    queue_items = _load_queue()
    if not queue_items:
        console.print("[yellow]Fila vazia.[/yellow]")
        raise typer.Exit(1)

    if index:
        item = _get_queue_item(queue_items, index)
    elif title:
        item = next((i for i in queue_items if title.lower() in i.title.lower()), None)
        if not item:
            console.print(f"[red]Proposta '{title}' nao encontrada.[/red]")
            raise typer.Exit(1)
    else:
        item = queue_items[0]

    cl = build_publication_checklist(item)
    console.print(f"\n[bold cyan]{cl.title}[/bold cyan]\n")
    for i, step in enumerate(cl.items, 1):
        console.print(f"  {i}. {step}")


@app.command()
def approve(
    index: int = typer.Argument(..., help="Numero na fila para aprovar (1-based)"),
) -> None:
    """Aprova uma proposta na fila."""
    queue_items = _load_queue()
    item = _get_queue_item(queue_items, index)
    item.status = "approved"
    _save_queue(queue_items)
    console.print(f"[green]Proposta #{index} aprovada: {item.title}[/green]")


@app.command("request-changes")
def request_changes(
    index: int = typer.Argument(..., help="Numero na fila para solicitar ajuste (1-based)"),
    note: str = typer.Option(..., "--note", "-n", help="Feedback para ajuste"),
) -> None:
    """Marca uma proposta como precisando de ajuste e registra o feedback."""
    queue_items = _load_queue()
    item = _get_queue_item(queue_items, index)
    item.status = "needs_revision"
    item.revision_count += 1
    item.feedback_history.append(note)
    _save_queue(queue_items)
    console.print(f"[yellow]Ajustes solicitados para #{index}: {item.title}[/yellow]")
    console.print(f"  Feedback: {note}")


@app.command()
def feedback(
    index: int = typer.Argument(..., help="Numero na fila para mostrar feedback (1-based)"),
) -> None:
    """Mostra o historico de feedback de uma proposta."""
    queue_items = _load_queue()
    item = _get_queue_item(queue_items, index)

    if not item.feedback_history:
        console.print("[yellow]Nenhum feedback registrado.[/yellow]")
        return

    console.print(f"\n[bold cyan]Feedback de {item.title}[/bold cyan]\n")
    for i, note in enumerate(item.feedback_history, 1):
        console.print(f"  {i}. {note}")


@app.command()
def requeue(
    index: int = typer.Argument(..., help="Numero na fila para reenviar a aprovacao (1-based)"),
    note: str | None = typer.Option(None, "--note", "-n", help="Observacao sobre o ajuste aplicado"),
) -> None:
    """Reenvia uma proposta ajustada para nova aprovacao."""
    queue_items = _load_queue()
    item = _get_queue_item(queue_items, index)
    item.status = "awaiting_approval"
    if note:
        item.feedback_history.append(f"Ajuste aplicado: {note}")
    _save_queue(queue_items)
    console.print(f"[green]Proposta #{index} reenviada para aprovacao: {item.title}[/green]")


@app.command()
def reject(
    index: int = typer.Argument(..., help="Numero na fila para rejeitar (1-based)"),
) -> None:
    """Rejeita uma proposta na fila."""
    queue_items = _load_queue()
    item = _get_queue_item(queue_items, index)
    item.status = "rejected"
    _save_queue(queue_items)
    console.print(f"[red]Proposta #{index} rejeitada: {item.title}[/red]")


@app.command()
def remove(
    index: int = typer.Argument(..., help="Numero na fila para remover (1-based)"),
) -> None:
    """Remove uma proposta da fila."""
    queue_items = _load_queue()
    _get_queue_item(queue_items, index)
    removed = queue_items.pop(index - 1)
    _save_queue(queue_items)
    console.print(f"[dim]Removido: {removed.title}[/dim]")


if __name__ == "__main__":
    app()
