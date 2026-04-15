from sqlalchemy import select

from app.models.approval import Approval
from app.db.session import AsyncSessionLocal
from app.models.business_unit import BusinessUnit
from app.models.project import Project
from app.models.project_metric import ProjectMetric
from app.models.task import Task

BUSINESS_UNITS = [
    {
        "name": "Conteudo",
        "slug": "conteudo",
        "description": "Operacoes de midia, criacao e distribuicao de conteudo.",
    },
    {
        "name": "Produtos Fisicos",
        "slug": "produtos-fisicos",
        "description": "Operacoes de achadinhos, e-commerce e TikTok Shop.",
    },
    {
        "name": "Produtos Digitais",
        "slug": "produtos-digitais",
        "description": "PDFs vendiveis, bundles e ativos digitais.",
    },
    {
        "name": "Automacoes",
        "slug": "automacoes",
        "description": "Bots, integracoes e utilitarios operacionais.",
    },
    {
        "name": "Labs",
        "slug": "labs",
        "description": "Experimentos criativos e projetos autorais.",
    },
]

PROJECTS = [
    {
        "business_unit_slug": "automacoes",
        "name": "Monarch AI",
        "slug": "monarch-ai",
        "description": "Nucleo de orquestracao e criacao de projetos.",
        "project_type": "internal_tool",
        "status": "active",
        "priority": "critical",
        "stage": "building",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Monarch AI",
        "main_goal": "Virar o sistema operacional da operacao inteira.",
        "current_focus": "Estruturar a fase 1 do monarch core.",
        "next_action": "Implementar cadastros centrais e dashboard inicial.",
    },
    {
        "business_unit_slug": "automacoes",
        "name": "WhatsApp Notion Bot",
        "slug": "whatsapp-notion-bot",
        "description": "Bot financeiro com Z-API, Claude e Notion.",
        "project_type": "automation",
        "status": "active",
        "priority": "high",
        "stage": "testing",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Monarch AI\\apps\\whatsapp-notion-bot\\whatsapp_notion_bot",
        "main_goal": "Registrar gastos via WhatsApp.",
        "current_focus": "Preparar deploy em producao.",
        "next_action": "Subir no servidor com Nginx e SSL.",
    },
    {
        "business_unit_slug": "produtos-digitais",
        "name": "PDF Factory",
        "slug": "pdf-factory",
        "description": "Pipeline para criacao de PDFs vendiveis.",
        "project_type": "product",
        "status": "incubating",
        "priority": "medium",
        "stage": "planning",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Criar ativos digitais de venda recorrente.",
        "current_focus": "Mapear nichos e estruturas de produto.",
        "next_action": "Definir primeira linha de PDFs a validar.",
    },
    {
        "business_unit_slug": "conteudo",
        "name": "Instagram Automation",
        "slug": "instagram-automation",
        "description": "Automacoes e experimentos operacionais para Instagram.",
        "project_type": "automation",
        "status": "incubating",
        "priority": "medium",
        "stage": "planning",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Automatizar parte da operacao de Instagram.",
        "current_focus": "Mapear fluxos seguros e objetivos reais.",
        "next_action": "Separar publicacao, pesquisa e resposta por modulo.",
    },
    {
        "business_unit_slug": "conteudo",
        "name": "Canal Dark",
        "slug": "canal-dark",
        "description": "Operacao de conteudo dark para alcance e monetizacao.",
        "project_type": "content",
        "status": "incubating",
        "priority": "high",
        "stage": "discovery",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Criar maquina de conteudo e receita.",
        "current_focus": "Definir nichos, formatos e pipeline.",
        "next_action": "Selecionar nicho principal e 10 ideias iniciais.",
    },
    {
        "business_unit_slug": "produtos-fisicos",
        "name": "TikTok Shop",
        "slug": "tiktok-shop",
        "description": "Operacao comercial com produtos fisicos e conteudo.",
        "project_type": "ecommerce",
        "status": "incubating",
        "priority": "high",
        "stage": "discovery",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Criar frente de vendas de produtos fisicos.",
        "current_focus": "Modelar operacao e captacao de produtos.",
        "next_action": "Definir criterios de produto vencedor.",
    },
    {
        "business_unit_slug": "produtos-fisicos",
        "name": "Achadinhos",
        "slug": "achadinhos",
        "description": "Pipeline para descobrir produtos fisicos vendaveis.",
        "project_type": "ecommerce",
        "status": "incubating",
        "priority": "high",
        "stage": "discovery",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Encontrar produtos com potencial de venda e viralizacao.",
        "current_focus": "Criar criterio de selecao e catalogacao.",
        "next_action": "Definir fontes e sinais de validacao.",
    },
    {
        "business_unit_slug": "labs",
        "name": "Solo Leveling Lab",
        "slug": "solo-leveling-lab",
        "description": "Projeto autoral e laboratorio de producao criativa.",
        "project_type": "lab",
        "status": "incubating",
        "priority": "medium",
        "stage": "discovery",
        "source_path": "D:\\Users\\Ewerton-viggo\\Documents\\Claude-Workspace-main",
        "main_goal": "Explorar producao criativa com potencial autoral.",
        "current_focus": "Separar o escopo de laboratorio da operacao comercial.",
        "next_action": "Definir o primeiro experimento validavel.",
    },
]

TASKS = [
    {
        "project_slug": "monarch-ai",
        "title": "Definir backlog da fase 1",
        "description": "Quebrar a fase 1 do monarch hub em entregas executaveis.",
        "task_type": "planning",
        "status": "in_progress",
        "priority": "critical",
        "owner_type": "agent",
        "owner_name": "planner",
        "approval_required": False,
    },
    {
        "project_slug": "canal-dark",
        "title": "Escolher nicho inicial",
        "description": "Selecionar nicho principal e formato do canal dark.",
        "task_type": "research",
        "status": "todo",
        "priority": "high",
        "owner_type": "human",
        "owner_name": "ewerton",
        "approval_required": True,
    },
    {
        "project_slug": "achadinhos",
        "title": "Definir criterios de produto vencedor",
        "description": "Mapear sinais de margem, apelo e potencial de viralizacao.",
        "task_type": "research",
        "status": "todo",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "offer_hunter",
        "approval_required": False,
    },
]

APPROVALS = [
    {
        "project_slug": "canal-dark",
        "task_title": "Escolher nicho inicial",
        "title": "Aprovar nicho inicial do Canal Dark",
        "summary": "Escolher o primeiro nicho da operacao antes de partir para roteiros e producao.",
        "status": "pending",
    }
]

PROJECT_METRICS = [
    {
        "project_slug": "canal-dark",
        "metric_name": "videos_published",
        "metric_value": 12,
        "metric_unit": "count",
    },
    {
        "project_slug": "tiktok-shop",
        "metric_name": "revenue_brl",
        "metric_value": 1850,
        "metric_unit": "BRL",
    },
    {
        "project_slug": "achadinhos",
        "metric_name": "products_tested",
        "metric_value": 24,
        "metric_unit": "count",
    },
]


async def seed_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BusinessUnit.slug))
        existing_slugs = set(result.scalars().all())

        units_by_slug: dict[str, BusinessUnit] = {}
        for item in BUSINESS_UNITS:
            if item["slug"] not in existing_slugs:
                session.add(BusinessUnit(**item))

        await session.commit()

        result = await session.execute(select(BusinessUnit))
        for unit in result.scalars().all():
            units_by_slug[unit.slug] = unit

        project_result = await session.execute(select(Project.slug))
        existing_projects = set(project_result.scalars().all())
        projects_by_slug: dict[str, Project] = {}

        for project_data in PROJECTS:
            if project_data["slug"] in existing_projects:
                continue

            unit = units_by_slug[project_data["business_unit_slug"]]
            session.add(
                Project(
                    business_unit_id=unit.id,
                    name=project_data["name"],
                    slug=project_data["slug"],
                    description=project_data["description"],
                    project_type=project_data["project_type"],
                    status=project_data["status"],
                    priority=project_data["priority"],
                    stage=project_data["stage"],
                    source_path=project_data["source_path"],
                    main_goal=project_data["main_goal"],
                    current_focus=project_data["current_focus"],
                    next_action=project_data["next_action"],
                )
            )

        await session.commit()

        result = await session.execute(select(Project))
        for project in result.scalars().all():
            projects_by_slug[project.slug] = project

        task_result = await session.execute(select(Task.title, Task.project_id))
        existing_tasks = {(title, project_id) for title, project_id in task_result.all()}

        for task_data in TASKS:
            project = projects_by_slug[task_data["project_slug"]]
            identity = (task_data["title"], project.id)
            if identity in existing_tasks:
                continue

            session.add(
                Task(
                    project_id=project.id,
                    title=task_data["title"],
                    description=task_data["description"],
                    task_type=task_data["task_type"],
                    status=task_data["status"],
                    priority=task_data["priority"],
                    owner_type=task_data["owner_type"],
                    owner_name=task_data["owner_name"],
                    approval_required=task_data["approval_required"],
                )
            )

        await session.commit()

        task_records = await session.execute(select(Task))
        tasks_by_identity = {(task.title, task.project_id): task for task in task_records.scalars().all()}

        approval_result = await session.execute(select(Approval.title, Approval.project_id))
        existing_approvals = {(title, project_id) for title, project_id in approval_result.all()}

        for approval_data in APPROVALS:
            project = projects_by_slug[approval_data["project_slug"]]
            identity = (approval_data["title"], project.id)
            if identity in existing_approvals:
                continue

            task = tasks_by_identity.get((approval_data["task_title"], project.id))
            session.add(
                Approval(
                    project_id=project.id,
                    task_id=task.id if task else None,
                    title=approval_data["title"],
                    summary=approval_data["summary"],
                    status=approval_data["status"],
                )
            )

        await session.commit()

        metric_result = await session.execute(select(ProjectMetric.metric_name, ProjectMetric.project_id))
        existing_metrics = {(metric_name, project_id) for metric_name, project_id in metric_result.all()}

        for metric_data in PROJECT_METRICS:
            project = projects_by_slug[metric_data["project_slug"]]
            identity = (metric_data["metric_name"], project.id)
            if identity in existing_metrics:
                continue

            session.add(
                ProjectMetric(
                    project_id=project.id,
                    metric_name=metric_data["metric_name"],
                    metric_value=metric_data["metric_value"],
                    metric_unit=metric_data["metric_unit"],
                )
            )

        await session.commit()
