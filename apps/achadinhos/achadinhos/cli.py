"""CLI para Achadinhos."""
import csv
import json
import sys
from pathlib import Path

import rich.console
import rich.table
import typer

from achadinhos.config import settings
from achadinhos.models import ProductCandidate, ProductShortlist
from achadinhos.pipeline import build_shortlist, render_shortlist_markdown, score_candidate

app = typer.Typer(help="Achadinhos — descubra, catogue e priorize produtos.")
console = rich.console.Console()


def _load_catalog() -> list[ProductCandidate]:
    path = settings.catalog_file
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [ProductCandidate(**item) for item in data]
    except Exception:
        return []


def _save_catalog(candidates: list[ProductCandidate]) -> None:
    settings.catalog_file.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "title": c.title,
            "category": c.category,
            "source": c.source,
            "price": c.price,
            "estimated_sale_price": c.estimated_sale_price,
            "visual_hook": c.visual_hook,
            "novelty": c.novelty,
            "demonstration_ease": c.demonstration_ease,
            "notes": c.notes,
        }
        for c in candidates
    ]
    settings.catalog_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@app.command()
def add(
    title: str = typer.Option(..., "--title", "-t", help="Nome do produto"),
    category: str = typer.Option("geral", "--category", "-c", help="Categoria"),
    source: str = typer.Option("manual", "--source", "-s", help="Fonte/ fornecedor"),
    price: float = typer.Option(..., "--price", "-p", help="Preco de custo"),
    sale_price: float = typer.Option(..., "--sale-price", help="Preco de venda estimado"),
    visual_hook: int = typer.Option(7, "--visual-hook", help="Apelo visual (1-10)"),
    novelty: int = typer.Option(6, "--novelty", help="Novidade (1-10)"),
    demonstration_ease: int = typer.Option(7, "--demo", help="Facilidade de demonstracao (1-10)"),
) -> None:
    """Adiciona um produto candidato ao catalogo."""
    candidate = ProductCandidate(
        title=title,
        category=category,
        source=source,
        price=price,
        estimated_sale_price=sale_price,
        visual_hook=visual_hook,
        novelty=novelty,
        demonstration_ease=demonstration_ease,
    )

    catalog = _load_catalog()
    catalog.append(candidate)
    _save_catalog(catalog)

    scored = score_candidate(candidate)
    console.print(f"[green]+ Candidato adicionado:[/green] {candidate.title}")
    console.print(f"  Score: {scored.score:.2f} | Margem: {scored.margin_ratio:.2f}x")


@app.command()
def add_file(
    input_file: Path = typer.Argument(..., help="Arquivo CSV com colunas: title,category,source,price,sale_price,visual_hook,novelty,demonstration_ease"),
) -> None:
    """Importa candidatos em massa de um arquivo CSV."""
    try:
        rows = list(csv.DictReader(input_file.open(encoding="utf-8")))
    except Exception as exc:
        console.print(f"[red]Erro ao ler arquivo: {exc}[/red]")
        raise typer.Exit(1)

    catalog = _load_catalog()
    added = 0
    for row in rows:
        try:
            row["price"] = float(row["price"])
            row["estimated_sale_price"] = float(row["sale_price"])
            row["visual_hook"] = int(row["visual_hook"])
            row["novelty"] = int(row["novelty"])
            row["demonstration_ease"] = int(row["demonstration_ease"])
            catalog.append(ProductCandidate(**row))
            added += 1
        except Exception as exc:
            console.print(f"[yellow]Linha ignorada: {exc}[/yellow]")

    _save_catalog(catalog)
    console.print(f"[green]{added} candidatos adicionados ao catalogo.[/green]")


@app.command()
def catalog(
    category: str | None = typer.Option(None, "--category", "-c", help="Filtrar por categoria"),
    min_score: float | None = typer.Option(None, "--min-score", help="Score minimo"),
) -> None:
    """Lista todos os candidatos do catalogo."""
    catalog = _load_catalog()
    if category:
        catalog = [c for c in catalog if c.category.lower() == category.lower()]

    if not catalog:
        console.print("[yellow]Catalogo vazio. Use 'achadinhos add' para adicionar candidatos.[/yellow]")
        return

    table = rich.table.Table(title=f"Catalogo ({len(catalog)} itens)")
    table.add_column("Titulo", style="cyan")
    table.add_column("Categoria", style="magenta")
    table.add_column("Custo", justify="right")
    table.add_column("Venda", justify="right")
    table.add_column("Margem", justify="right")
    table.add_column("VH", justify="center", style="blue")
    table.add_column("NOV", justify="center", style="blue")
    table.add_column("DEMO", justify="center", style="blue")

    for candidate in sorted(catalog, key=lambda c: c.price):
        scored = score_candidate(candidate)
        if min_score and scored.score < min_score:
            continue
        margin = f"{scored.margin_ratio:.1f}x"
        table.add_row(
            candidate.title[:30],
            candidate.category,
            f"R${candidate.price:.2f}",
            f"R${candidate.estimated_sale_price:.2f}",
            margin,
            str(candidate.visual_hook),
            str(candidate.novelty),
            str(candidate.demonstration_ease),
        )

    console.print(table)


@app.command()
def shortlist(
    limit: int = typer.Option(5, "--limit", "-l", help="Quantidade de itens na shortlist"),
    title: str = typer.Option("Shortlist de achadinhos", "--title", "-t", help="Titulo da shortlist"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Salvar shortlist em arquivo"),
    format: str = typer.Option("md", "--format", "-f", help="Formato: md, json, all"),
) -> None:
    """Gera a shortlist priorizada de candidatos."""
    catalog = _load_catalog()
    if not catalog:
        console.print("[yellow]Catalogo vazio.[/yellow]")
        raise typer.Exit(1)

    shortlist_obj = build_shortlist(catalog, limit=limit, title=title)

    table = rich.table.Table(title=title)
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Titulo", style="cyan")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Margem", justify="right")
    table.add_column("Forcas", style="dim")

    for i, item in enumerate(shortlist_obj.items, 1):
        strengths_str = "; ".join(s[:30] for s in item.strengths[:2])
        table.add_row(str(i), item.title[:25], f"{item.score:.2f}", f"{item.margin_ratio:.1f}x", strengths_str)

    console.print(table)

    if format in ("md", "all"):
        md = render_shortlist_markdown(shortlist_obj)
        if output:
            settings.shortlist_dir.mkdir(parents=True, exist_ok=True)
            out_path = settings.shortlist_dir / f"{output.stem}.md"
            out_path.write_text(md, encoding="utf-8")
            console.print(f"[green]Markdown salvo em: {out_path}[/green]")
        else:
            console.print("\n" + md)

    if format in ("json", "all"):
        data = {
            "title": shortlist_obj.title,
            "items": [
                {
                    "rank": i,
                    "slug": item.slug,
                    "title": item.title,
                    "category": item.category,
                    "source": item.source,
                    "margin_ratio": item.margin_ratio,
                    "score": item.score,
                    "strengths": item.strengths,
                    "risks": item.risks,
                }
                for i, item in enumerate(shortlist_obj.items, 1)
            ],
        }
        console.print("\n[bold]JSON:[/bold]")
        console.print_json(data=json.dumps(data, indent=2, ensure_ascii=False))


@app.command()
def score(
    title: str = typer.Option(..., "--title", "-t", help="Titulo do produto"),
) -> None:
    """Mostra o score detalhado de um produto do catalogo."""
    catalog = _load_catalog()
    candidate = next((c for c in catalog if c.title.lower() == title.lower()), None)
    if not candidate:
        console.print(f"[red]Produto '{title}' nao encontrado no catalogo.[/red]")
        raise typer.Exit(1)

    scored = score_candidate(candidate)
    console.print(f"\n[bold cyan]{scored.title}[/bold cyan]")
    console.print(f"Score total: [green]{scored.score:.2f}[/green] / 10")
    console.print(f"Margem potencial: [yellow]{scored.margin_ratio:.2f}x[/yellow]")
    console.print(f"Fonte: {scored.source}")
    console.print(f"Categoria: {scored.category}")
    console.print()

    if scored.strengths:
        console.print("[bold]Forcas:[/bold]")
        for s in scored.strengths:
            console.print(f"  [green]+ {s}[/green]")
    if scored.risks:
        console.print("[bold]Riscos:[/bold]")
        for r in scored.risks:
            console.print(f"  [red]- {r}[/red]")


if __name__ == "__main__":
    app()
