"""CLI para TikTok Shop."""
from pathlib import Path

import rich.console
import rich.table
import typer

from tiktok_shop.models import ValidationPlan
from tiktok_shop.pipeline import build_validation_plan, render_validation_plan

app = typer.Typer(help="TikTok Shop — transforme candidatos em planos de validacao comercial.")
console = rich.console.Console()


@app.command()
def plan(
    title: str = typer.Option(..., "--title", "-t", help="Titulo do produto"),
    category: str = typer.Option(..., "--category", "-c", help="Categoria"),
    source: str = typer.Option(..., "--source", "-s", help="Fonte do candidato"),
    price: float = typer.Option(..., "--price", "-p", help="Preco de custo"),
    sale_price: float = typer.Option(..., "--sale-price", help="Preco de venda"),
    score: float = typer.Option(..., "--score", help="Score do candidato"),
    margin: float = typer.Option(..., "--margin", help="Margem potencial"),
    audience: str = typer.Option(
        "compradores por impulso com interesse visual",
        "--audience",
        "-a",
        help="Publico-alvo",
    ),
    output: Path | None = typer.Option(None, "--output", "-o", help="Salvar plano em arquivo"),
) -> None:
    """Gera plano de validacao comercial para um produto."""
    from dataclasses import dataclass

    @dataclass(slots=True)
    class _DummyCandidate:
        slug: str
        title: str
        category: str
        source: str
        margin_ratio: float
        score: float
        strengths: list
        risks: list

    import re
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower())

    candidate = _DummyCandidate(
        slug=slug,
        title=title,
        category=category,
        source=source,
        margin_ratio=margin,
        score=score,
        strengths=[],
        risks=[],
    )

    plan = build_validation_plan(candidate, audience=audience)
    md = render_validation_plan(plan)

    console.print(f"\n[bold green]{plan.product_title}[/bold green]")
    console.print(f"[cyan]Angulo:[/cyan] {plan.offer_angle.title}")
    console.print(f"[cyan]Margem:[/cyan] {margin}x | [cyan]Score:[/cyan] {score}\n")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md, encoding="utf-8")
        console.print(f"[green]Plano salvo em: {output}[/green]")
    else:
        console.print(md)


@app.command()
def checklist(
    title: str = typer.Option(..., "--title", "-t", help="Titulo do produto"),
    category: str = typer.Option(..., "--category", "-c", help="Categoria"),
    source: str = typer.Option("shortlist", "--source", "-s", help="Fonte"),
    price: float = typer.Option(50.0, "--price", "-p", help="Preco de custo"),
    sale_price: float = typer.Option(120.0, "--sale-price", help="Preco de venda"),
    score: float = typer.Option(7.0, "--score", help="Score"),
    margin: float = typer.Option(1.4, "--margin", help="Margem"),
) -> None:
    """Mostra checklist de validacao para um produto."""
    import re
    from dataclasses import dataclass

    @dataclass(slots=True)
    class _Dummy:
        slug: str
        title: str
        category: str
        source: str
        margin_ratio: float
        score: float
        strengths: list
        risks: list

    candidate = _Dummy(
        slug=re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()),
        title=title,
        category=category,
        source=source,
        margin_ratio=margin,
        score=score,
        strengths=[],
        risks=[],
    )

    plan = build_validation_plan(candidate)
    console.print(f"\n[bold cyan]Checklist: {plan.product_title}[/bold cyan]\n")
    for i, item in enumerate(plan.checklist, 1):
        console.print(f"  {i}. {item}")


if __name__ == "__main__":
    app()
