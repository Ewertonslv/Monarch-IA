"""CLI interface for Monarch AI — submit tasks from the terminal."""
import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path

# Ensure the project root is on sys.path when running as an installed command
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def _normalize_cli_input(raw_input: str) -> str:
    raw_input = raw_input.strip()
    raw_input = re.sub(r'^(orquestrador[:,]?\s*)', '', raw_input, flags=re.I)
    return raw_input


def _print_progress(agent_name: str, status: str, payload: dict[str, object] | None) -> None:
    if status == "starting":
        print(f"\n>> [{agent_name}] Starting...")
        return

    if status == "finished":
        print(f"OK [{agent_name}] Finished")
        if payload:
            confidence = payload.get("confidence")
            concerns = payload.get("concerns")
            if confidence is not None:
                print(f"    confidence: {confidence}")
            if concerns:
                print("    concerns:")
                for concern in concerns:
                    print(f"      - {concern}")
        return

    if status == "failed":
        print(f"!! [{agent_name}] Failed: {payload.get('error') if payload else 'unknown error'}")
        return

    if status == "retrying":
        print(f".. [{agent_name}] Retrying...")
        return


def _print_task_summary(task) -> None:
    print(f"\n{'='*60}")
    print("Task summary")
    print(f"Status : {task.status.value.upper()}")
    if task.branch_name:
        print(f"Branch : {task.branch_name}")
    if task.requirements:
        print("\nRequirements:")
        for key, value in task.requirements.items():
            print(f"  {key}: {value}")
    if task.architecture:
        print("\nArchitecture:")
        for key, value in task.architecture.items():
            print(f"  {key}: {value}")
    if task.plan:
        print("\nPlan steps:")
        for index, step in enumerate(task.plan, start=1):
            title = step.get("title") if isinstance(step, dict) else str(step)
            print(f"  {index}. {title}")
    print(f"{'='*60}\n")


async def _run_plan_only(raw_input: str) -> None:
    from config import config
    from agents.architecture import ArchitectureAgent
    from agents.discovery import DiscoveryAgent
    from agents.planning import PlanningAgent
    from agents.prioritization import PrioritizationAgent
    from core.task import Task
    from storage.database import Database

    db = Database(config.database_url)
    await db.init()

    task = Task(raw_input=raw_input)
    print(f"\n[plan-only] Running for: {raw_input}")
    print(f"   Task ID: {task.task_id}\n")

    agents = [
        DiscoveryAgent(),
        PrioritizationAgent(),
        ArchitectureAgent(),
        PlanningAgent(),
    ]

    for agent in agents:
        print(f"\n=== {agent.label} ===")
        result = await agent.run(task)
        print(f"    confidence: {result.confidence:.2f}")
        if result.concerns:
            print("    concerns:")
            for concern in result.concerns:
                print(f"      - {concern}")

    _print_task_summary(task)
    await db.close()
    sys.exit(0)


async def _run_cli(raw_input: str, verbose: bool = True) -> None:
    from config import config
    from core.task import Task, TaskStatus
    from core.orchestrator import Orchestrator
    from storage.database import Database

    db = Database(config.database_url)
    await db.init()

    orchestrator = Orchestrator(db, progress_callback=_print_progress if verbose else None)
    task = Task(raw_input=raw_input)

    # For CLI mode, auto-approve both gates
    original_request_approval = orchestrator._request_approval

    async def _auto_approve(task, stage):  # noqa: ANN001
        print(f"\n[AUTO-APPROVE] Stage: {stage}")
        task.status = TaskStatus.RUNNING
        await db.update_task(task)
        return True

    orchestrator._request_approval = _auto_approve  # type: ignore[method-assign]

    print(f"\n[monarch] Starting pipeline for: {raw_input}")
    print(f"   Task ID: {task.task_id}\n")

    result = await orchestrator.run(task)

    _print_task_summary(result)
    if result.pr_url:
        print(f"PR URL : {result.pr_url}")
    if result.branch_name:
        print(f"Branch : {result.branch_name}")
    print(f"\nHistory ({len(result.history)} entries):")
    for entry in result.history[-10:]:
        print(f"  {entry.agent:20s} {entry.action:30s} {entry.detail}")
    print(f"{'='*60}\n")

    await db.close()

    sys.exit(0 if result.status.value == "done" else 1)


# -----------------------------------------------------------------------------
# Natural language intent routing — maps plain text to local CLI commands
# -----------------------------------------------------------------------------

import subprocess
from pathlib import Path

_ROUTER: list[tuple[list[str], Path, list[str]]] = [
    # (keywords, app_dir, [args])
    # Achadinhos — specific commands FIRST
    (
        ["shortlist", "ranking", "melhores produtos", "prioridade"],
        Path(__file__).resolve().parent.parent / "apps" / "achadinhos",
        ["python", "-m", "achadinhos", "shortlist"],
    ),
    (
        ["catalogo", "lista de produtos"],
        Path(__file__).resolve().parent.parent / "apps" / "achadinhos",
        ["python", "-m", "achadinhos", "catalog"],
    ),
    (
        ["achadinhos", "produto", "scoring", "margem", "fornecedor"],
        Path(__file__).resolve().parent.parent / "apps" / "achadinhos",
        ["python", "-m", "achadinhos", "add"],
    ),
    # Canal Dark
    (
        ["canal dark", "pauta", "roteiro", "backlog"],
        Path(__file__).resolve().parent.parent / "apps" / "canal-dark",
        ["python", "-m", "canal_dark", "new"],
    ),
    # Instagram Automation
    (
        ["instagram", "reels", "post", "conteudo", "carrossel", "pilar"],
        Path(__file__).resolve().parent.parent / "apps" / "instagram-automation",
        ["python", "-m", "instagram_automation", "research"],
    ),
    (
        ["fila", "aprovacao", "aprova", "reject"],
        Path(__file__).resolve().parent.parent / "apps" / "instagram-automation",
        ["python", "-m", "instagram_automation", "queue"],
    ),
    # Solo Leveling Lab
    (
        ["solo leveling", "lab", "experimento", "criativo"],
        Path(__file__).resolve().parent.parent / "apps" / "solo-leveling-lab",
        ["python", "-m", "solo_leveling_lab", "experiment"],
    ),
    # TikTok Shop
    (
        ["tiktok", "shop", "oferta", "validacao"],
        Path(__file__).resolve().parent.parent / "apps" / "tiktok-shop",
        ["python", "-m", "tiktok_shop", "plan"],
    ),
    # PDF Factory — generico, por ultimo
    (
        ["pdf", "documento", "relatorio", "contrato", "proposta", "guia", "vendas", "ofert", "apresentacao"],
        Path(__file__).resolve().parent.parent / "apps" / "pdf-factory",
        ["python", "-m", "pdf_factory", "run"],
    ),
]


def _route_natural_language(raw_input: str) -> tuple[Path, list[str]] | None:
    raw_lower = raw_input.lower().strip()

    for keywords, app_dir, base_cmd in _ROUTER:
        if any(kw in raw_lower for kw in keywords):
            return app_dir, base_cmd

    return None


def _extract_natural_arg(raw_input: str, patterns: list[str]) -> str | None:
    """Extract a value from natural language using prefix patterns."""
    raw_lower = raw_input.lower()
    for pattern in patterns:
        idx = raw_lower.find(pattern)
        if idx >= 0:
            start = idx + len(pattern)
            end = raw_lower.find(" --", start)
            if end < 0:
                end = len(raw_input)
            val = raw_input[start:end].strip().strip(",").strip(".").strip('"').strip("'")
            if val and len(val) > 1:
                return val
    return None


def _build_cli_args(raw_input: str, base_cmd: list[str], app_dir: Path) -> list[str]:
    raw_lower = raw_input.lower()
    args = list(base_cmd)

    def pop_flag(flag: str) -> str | None:
        pattern = f"{flag} "
        idx = raw_lower.find(pattern)
        if idx >= 0:
            start = idx + len(pattern)
            end = raw_lower.find(" --", start)
            if end < 0:
                end = len(raw_input)
            return raw_input[start:end].strip().strip('"').strip("'")
        return None

    app_name = app_dir.name

    if app_name == "canal-dark":
        import re
        niche_match = re.search(r'canal\s*dark\s+(?:para\s+)?nicho\s+de\s+(\w[\w\s]*?)(?:\s+--|\s*$|$)', raw_lower)
        if niche_match:
            niche = niche_match.group(1).strip()
        else:
            niche = pop_flag("--niche") or _extract_natural_arg(raw_input, ["para nicho ", "nicho ", "sobre nicho "])
        audience = pop_flag("--audience") or _extract_natural_arg(raw_input, ["audiencia ", "para audiencia "])
        promise = pop_flag("--promise") or _extract_natural_arg(raw_input, ["promessa "])
        if niche:
            args.extend(["--niche", niche])
        if audience:
            args.extend(["--audience", audience])
        if promise:
            args.extend(["--promise", promise])

    elif app_name == "achadinhos":
        title = pop_flag("--title") or _extract_natural_arg(raw_input, ["produto ", "adicionar produto ", "adicione "])
        if title:
            import re
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', raw_input)
            words = title.split()
            category_parts = []
            title_parts = []
            price_vals = []
            for w in words:
                if re.match(r'^\d+$', w):
                    price_vals.append(w)
                elif re.match(r'^\d+\.\d+$', w):
                    price_vals.append(w)
                elif w in ("beleza", "casa", "tech", "fitness", "gamer", "pets", "feminino", "masculino", "infantil", "esportivo", "decoracao", "utilitario", "papelaria", "cozinha", "banho", "petshop", "auto"):
                    category_parts.append(w)
                else:
                    title_parts.append(w)
            if title_parts:
                args.extend(["--title", " ".join(title_parts)])
            if category_parts:
                args.extend(["--category", " ".join(category_parts)])
            else:
                args.extend(["--category", "geral"])
            if len(price_vals) >= 1:
                args.extend(["--price", price_vals[0]])
            if len(price_vals) >= 2:
                args.extend(["--sale-price", price_vals[1]])
            if len(price_vals) >= 3:
                args.extend(["--visual-hook", price_vals[2]])
            if len(price_vals) >= 4:
                args.extend(["--novelty", price_vals[3]])
            if len(price_vals) >= 5:
                args.extend(["--demo", price_vals[4]])

    elif app_name == "instagram-automation":
        import re
        insta_match = re.search(r'instagram\s+(?:pesquisa\s+)?sobre\s+(\w[\w\s]*?)(?:\s+para|\s+--|\s+audiencia|\s*$|$)', raw_lower)
        if insta_match:
            niche = insta_match.group(1).strip()
        else:
            niche = pop_flag("--niche") or _extract_natural_arg(raw_input, ["nicho ", "sobre ", "para nicho "])
        objective = pop_flag("--objective") or _extract_natural_arg(raw_input, ["objetivo ", "gerar ", "para gerar "])
        audience = pop_flag("--audience") or _extract_natural_arg(raw_input, ["audiencia ", "para audiencia "])
        if niche:
            args.extend(["--niche", niche])
        if objective:
            args.extend(["--objective", objective])
        if audience:
            args.extend(["--audience", audience])

    elif app_name == "solo-leveling-lab":
        thesis = pop_flag("--thesis") or _extract_natural_arg(raw_input, ["sobre ", "tese ", "experimento sobre "])
        format_hint = pop_flag("--format") or _extract_natural_arg(raw_input, ["formato "])
        if thesis:
            args.extend(["--thesis", thesis])
        if format_hint:
            args.extend(["--format", format_hint])

    elif app_name == "pdf-factory":
        import re
        pdf_match = re.search(r'documento\s+(?:sobre\s+)?(\w[\w\s]*?)(?:\s+para\s+audiencia|\s+para\s+a\s+audiencia|\s+--|\s*$|$)', raw_lower)
        if pdf_match:
            title = pdf_match.group(1).strip()
        else:
            title = pop_flag("--title") or _extract_natural_arg(raw_input, ["sobre ", "documento sobre "])
        audience_match = re.search(r'para\s+(?:a\s+)?audiencia\s+(\w[\w\s]*?)(?:\s+--|\s+para|\s*$|$)', raw_lower)
        if audience_match:
            audience = audience_match.group(1).strip()
        else:
            audience = pop_flag("--audience") or _extract_natural_arg(raw_input, ["audiencia ", "para audiencia "])
        objective = pop_flag("--objective") or _extract_natural_arg(raw_input, ["objetivo "])
        if title:
            args.extend(["--title", title])
        if audience:
            args.extend(["--audience", audience])
        if objective:
            args.extend(["--objective", objective])

    elif app_name == "tiktok-shop":
        title = pop_flag("--title") or _extract_natural_arg(raw_input, ["produto ", "oferta para "])
        if title:
            args.extend(["--title", title])

    # Generic flags (work across all apps)
    for flag in ["--price", "--sale-price", "--visual-hook", "--novelty", "--demo",
                  "--cta", "--score", "--margin", "--category", "--source"]:
        val = pop_flag(flag)
        if val:
            args.extend([flag, val])

    return args


def _run_local_command(cmd: list[str], cwd: Path) -> int:
    print(f"\n[monarch] Routing to local command:")
    print(f"  {' '.join(cmd)}")
    print()
    result = subprocess.run(cmd, cwd=str(cwd))
    return result.returncode


# -----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="monarch",
        description="Monarch AI — Multi-agent SaaS development pipeline",
    )
    subparsers = parser.add_subparsers(dest="command")

    do_parser = subparsers.add_parser("do", help="Run a local command using plain text")
    do_parser.add_argument("input", nargs="+", help="What to do")
    do_parser.add_argument(
        "--ai",
        action="store_true",
        help="Force AI pipeline instead of local routing",
    )

    run_parser = subparsers.add_parser("run", help="Submit a task to the AI pipeline")
    run_parser.add_argument("input", nargs="+", help="Feature description")
    run_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-agent progress, confidence, and concerns",
    )
    run_parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Run only discovery, prioritization, architecture, and planning",
    )

    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        parser.parse_args()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print(
            "\n"
            "  Monarch CLI — Comandos disponiveis\n"
            "\n"
            "  Linguagem natural (local, sem API):\n"
            "\n"
            "    monarch \"crie o projeto canal dark para nicho de historia\"\n"
            "    monarch \"gere um documento sobre vendas para audiencia b2b\"\n"
            "    monarch \"adicione produto escova secadora beleza 70 179\"\n"
            "    monarch \"shortlist de achadinhos\"\n"
            "    monarch \"pesquisa instagram sobre marketing digital leads\"\n"
            "    monarch \"experimento solo leveling sobre progressao visual\"\n"
            "    monarch do \"crie o projeto canal dark\"   (explicito)\n"
            "\n"
            "  Pipeline de agentes (usa API/CLI):\n"
            "\n"
            "    monarch run \"crie uma landing page para meu produto\"\n"
            "    monarch run \"implemente autenticacao jwt no meu backend\" --plan-only\n"
            "\n"
            "  Help:\n"
            "\n"
            "    monarch help                          — este help\n"
            "    monarch do --help                     — ver ajuda do comando local\n"
            "    python -m <app> --help                — ajuda de cada app\n"
            "\n"
        )
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "do":
        args = parser.parse_args()
        raw_input = " ".join(args.input)
        normalized = _normalize_cli_input(raw_input)
        if args.ai:
            asyncio.run(_run_cli(normalized, verbose=True))
        else:
            routed = _route_natural_language(normalized)
            if routed:
                app_dir, base_cmd = routed
                cli_args = _build_cli_args(normalized, base_cmd, app_dir)
                sys.exit(_run_local_command(cli_args, app_dir))
            print("[monarch] Nao encontrei comando local para isso.")
            print("Use --ai para rodar via pipeline de agentes, ou 'monarch help' para ver todos os comandos.")
            sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "run":
        args = parser.parse_args()
        raw_input = " ".join(args.input)
        if args.plan_only:
            asyncio.run(_run_plan_only(_normalize_cli_input(raw_input)))
        else:
            asyncio.run(_run_cli(_normalize_cli_input(raw_input), verbose=args.verbose))
    elif len(sys.argv) > 1:
        raw_input = " ".join(sys.argv[1:])
        normalized = _normalize_cli_input(raw_input)

        routed = _route_natural_language(normalized)
        if routed:
            app_dir, base_cmd = routed
            cli_args = _build_cli_args(normalized, base_cmd, app_dir)
            sys.exit(_run_local_command(cli_args, app_dir))

        print("[monarch] No local match found — routing to AI pipeline...\n")
        asyncio.run(_run_cli(normalized, verbose=True))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
