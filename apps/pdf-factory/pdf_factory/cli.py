"""CLI para PDF Factory."""
import json
import sys
from pathlib import Path

import rich.console
import rich.progress
import rich.table
import typer

from pdf_factory.config import settings
from pdf_factory.models import BriefInput
from pdf_factory.pipeline import build_document_plan, build_output_filename, render_markdown
from pdf_factory.render import render_html, render_pdf, reset_env

app = typer.Typer(help="PDF Factory — transforme briefs em ativos digitais.")
console = rich.console.Console()


@app.command()
def run(
    title: str = typer.Option(..., "--title", "-t", help="Titulo do documento"),
    audience: str = typer.Option("publico geral", "--audience", "-a", help="Publico-alvo"),
    objective: str = typer.Option("informar e engajar", "--objective", "-o", help="Objetivo principal"),
    tone: str = typer.Option("pratico", "--tone", help="Tom do documento"),
    format_hint: str = typer.Option("guia", "--format-hint", help="Formato do documento"),
    call_to_action: str | None = typer.Option(None, "--cta", help="Call to action"),
    output: Path | None = typer.Option(None, "--output", help="Diretorio de saida"),
    template: str = typer.Option("pro", "--template", help="Template a usar"),
    output_format: str = typer.Option("all", "--output-format", help="Formato: md, html, pdf, all"),
) -> None:
    """Gera um documento a partir de parametros via linha de comando."""
    brief = BriefInput(
        title=title,
        audience=audience,
        objective=objective,
        tone=tone,
        format_hint=format_hint,
        call_to_action=call_to_action,
    )
    _process_and_output(brief, output, template, output_format)


@app.command()
def run_file(
    input_file: Path = typer.Argument(..., help="Arquivo JSON com o briefing"),
    output: Path | None = typer.Option(None, "--output", help="Diretorio de saida"),
    template: str = typer.Option("pro", "--template", help="Template a usar"),
    output_format: str = typer.Option("all", "--output-format", help="Formato: md, html, pdf, all"),
) -> None:
    """Gera um documento a partir de um arquivo JSON de briefing."""
    try:
        data = json.loads(input_file.read_text(encoding="utf-8"))
    except Exception as exc:
        console.print(f"[red]Erro ao ler arquivo: {exc}[/red]")
        raise typer.Exit(1)

    try:
        brief = BriefInput(**data)
    except Exception as exc:
        console.print(f"[red]Brief invalido: {exc}[/red]")
        raise typer.Exit(1)

    _process_and_output(brief, output, template, output_format)


@app.command()
def templates() -> None:
    """Lista templates disponiveis."""
    template_dir = settings.template_dir
    if not template_dir.exists():
        console.print("[yellow]Diretorio de templates nao encontrado.[/yellow]")
        return

    table = rich.table.Table(title="Templates Disponiveis")
    table.add_column("Nome", style="cyan")
    table.add_column("Arquivo", style="dim")

    for path in sorted(template_dir.glob("*.html")):
        table.add_row(path.stem, path.name)

    console.print(table)


def _process_and_output(
    brief: BriefInput,
    output: Path | None,
    template: str,
    output_format: str,
) -> None:
    reset_env()
    output_dir = output or settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    plan = build_document_plan(brief)
    filename_base = build_output_filename(plan)

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Gerando documento...", total=None)

        if output_format in ("md", "all"):
            md_path = output_dir / f"{filename_base}.md"
            md_path.write_text(render_markdown(plan), encoding="utf-8")
            console.print(f"[green]Markdown: {md_path}[/green]")

        if output_format in ("html", "all"):
            html_content = render_html(plan, template=template)
            html_path = output_dir / f"{filename_base}.html"
            html_path.write_text(html_content, encoding="utf-8")
            console.print(f"[green]HTML: {html_path}[/green]")

        if output_format in ("pdf", "all"):
            html_content = render_html(plan, template=template)
            pdf_path = output_dir / f"{filename_base}.pdf"
            ok = render_pdf(html_content, pdf_path)
            if ok:
                console.print(f"[green]PDF: {pdf_path}[/green]")
            else:
                console.print("[yellow]PDF nao gerado (weasyprint pode nao estar instalado).[/yellow]")

    console.print(f"\n[bold green]Concluido![/bold green] {output_dir}")


if __name__ == "__main__":
    app()
