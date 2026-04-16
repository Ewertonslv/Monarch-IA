from sqlalchemy import select

from app.models.approval import Approval
from app.db.session import AsyncSessionLocal
from app.models.business_unit import BusinessUnit
from app.models.project import Project
from app.models.project_metric import ProjectMetric
from app.models.roadmap_item import RoadmapItem
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
        "source_path": ".",
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
        "source_path": "apps/whatsapp-notion-bot",
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
        "stage": "building",
        "source_path": "apps/pdf-factory",
        "main_goal": "Criar ativos digitais de venda recorrente.",
        "current_focus": "Conectar o scaffold local a briefs e saidas reais.",
        "next_action": "Definir a primeira linha de PDFs e validar um artefato completo.",
    },
    {
        "business_unit_slug": "conteudo",
        "name": "Instagram Automation",
        "slug": "instagram-automation",
        "description": "Automacoes e experimentos operacionais para Instagram.",
        "project_type": "automation",
        "status": "incubating",
        "priority": "medium",
        "stage": "building",
        "source_path": "apps/instagram-automation",
        "main_goal": "Automatizar parte da operacao de Instagram.",
        "current_focus": "Integrar pesquisa, fila e publicacao assistida ao Hub.",
        "next_action": "Transformar a fila local em backlog operacional rastreavel.",
    },
    {
        "business_unit_slug": "conteudo",
        "name": "Canal Dark",
        "slug": "canal-dark",
        "description": "Operacao de conteudo dark para alcance e monetizacao.",
        "project_type": "content",
        "status": "incubating",
        "priority": "high",
        "stage": "building",
        "source_path": "apps/canal-dark",
        "main_goal": "Criar maquina de conteudo e receita.",
        "current_focus": "Usar o backlog local de pautas para iniciar a operacao.",
        "next_action": "Escolher o nicho principal e produzir o primeiro roteiro completo.",
    },
    {
        "business_unit_slug": "produtos-fisicos",
        "name": "TikTok Shop",
        "slug": "tiktok-shop",
        "description": "Operacao comercial com produtos fisicos e conteudo.",
        "project_type": "ecommerce",
        "status": "incubating",
        "priority": "high",
        "stage": "building",
        "source_path": "apps/tiktok-shop",
        "main_goal": "Criar frente de vendas de produtos fisicos.",
        "current_focus": "Converter shortlist em oferta, script e validacao.",
        "next_action": "Escolher o primeiro produto e montar a primeira oferta testavel.",
    },
    {
        "business_unit_slug": "produtos-fisicos",
        "name": "Achadinhos",
        "slug": "achadinhos",
        "description": "Pipeline para descobrir produtos fisicos vendaveis.",
        "project_type": "ecommerce",
        "status": "incubating",
        "priority": "high",
        "stage": "building",
        "source_path": "apps/achadinhos",
        "main_goal": "Encontrar produtos com potencial de venda e viralizacao.",
        "current_focus": "Usar o scaffold de scoring para estruturar a shortlist inicial.",
        "next_action": "Preencher o catalogo com candidatos reais e gerar o primeiro ranking.",
    },
    {
        "business_unit_slug": "labs",
        "name": "Solo Leveling Lab",
        "slug": "solo-leveling-lab",
        "description": "Projeto autoral e laboratorio de producao criativa.",
        "project_type": "lab",
        "status": "incubating",
        "priority": "medium",
        "stage": "building",
        "source_path": "apps/solo-leveling-lab",
        "main_goal": "Explorar producao criativa com potencial autoral.",
        "current_focus": "Materializar a tese criativa em experimento executavel.",
        "next_action": "Definir o primeiro artefato e iniciar o ciclo de aprendizado.",
    },
]

TASKS = [
    {
        "project_slug": "monarch-ai",
        "title": "Fechar fase 1 operacional do Monarch AI",
        "description": "Concluir cadastros centrais, dashboard, pipeline multiagente estavel, execucao persistida e base confiavel para os demais projetos.",
        "task_type": "coding",
        "status": "in_progress",
        "priority": "critical",
        "owner_type": "agent",
        "owner_name": "monarch_builder",
        "approval_required": False,
    },
    {
        "project_slug": "whatsapp-notion-bot",
        "title": "Levar WhatsApp Notion Bot para operacao completa",
        "description": "Finalizar deploy, webhook, persistencia, observabilidade e fluxo ponta a ponta de registro de gastos em producao.",
        "task_type": "deploy",
        "status": "todo",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "ops_bot",
        "approval_required": False,
    },
    {
        "project_slug": "pdf-factory",
        "title": "Implementar MVP operacional do PDF Factory",
        "description": "Criar pipeline que recebe um briefing, gera estrutura, produz PDF final e organiza o ativo para venda.",
        "task_type": "coding",
        "status": "in_progress",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "product_builder",
        "approval_required": False,
    },
    {
        "project_slug": "instagram-automation",
        "title": "Implementar fluxo seguro do Instagram Automation",
        "description": "Separar pesquisa, fila de conteudo, aprovacao e publicacao/preparacao assistida em modulos claros.",
        "task_type": "coding",
        "status": "in_progress",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "growth_automation",
        "approval_required": False,
    },
    {
        "project_slug": "canal-dark",
        "title": "Implementar maquina inicial do Canal Dark",
        "description": "Definir nicho, produzir backlog inicial e montar pipeline de pauta, roteiro, producao e publicacao.",
        "task_type": "research",
        "status": "in_progress",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "content_operator",
        "approval_required": False,
    },
    {
        "project_slug": "achadinhos",
        "title": "Implementar sistema de descoberta do Achadinhos",
        "description": "Montar fluxo de coleta, catalogacao, scoring e shortlist de produtos fisicos com potencial de venda.",
        "task_type": "research",
        "status": "in_progress",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "offer_hunter",
        "approval_required": False,
    },
    {
        "project_slug": "tiktok-shop",
        "title": "Implementar operacao inicial do TikTok Shop",
        "description": "Conectar selecao de produtos, conteudo e oferta em uma rotina minima de validacao comercial.",
        "task_type": "deploy",
        "status": "in_progress",
        "priority": "high",
        "owner_type": "agent",
        "owner_name": "commerce_operator",
        "approval_required": False,
    },
    {
        "project_slug": "solo-leveling-lab",
        "title": "Transformar Solo Leveling Lab em experimento executavel",
        "description": "Definir um experimento autoral concreto, o entregavel inicial e o pipeline minimo para produzi-lo.",
        "task_type": "planning",
        "status": "in_progress",
        "priority": "medium",
        "owner_type": "agent",
        "owner_name": "creative_lab",
        "approval_required": False,
    },
]

APPROVALS = [
    {
        "project_slug": "monarch-ai",
        "task_title": "Fechar fase 1 operacional do Monarch AI",
        "title": "Aprovar escopo da fase 1 do Monarch AI",
        "summary": "Validar que o Monarch AI sera a base operacional antes de acelerar as demais frentes.",
        "status": "pending",
    },
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

ROADMAP_ITEMS = [
    {
        "project_slug": "monarch-ai",
        "title": "Sistema operacional da operacao",
        "description": "Objetivo final: transformar o Monarch AI no centro de projetos, tarefas, aprovacoes, execucoes e agentes. MVP: Hub funcional, pipeline estavel, persistencia confiavel e deploy reproduzivel. Dependencias: nenhuma. Pronto quando: cadastros centrais, dashboard, aprovacoes e execucao multiagente funcionarem sem travar.",
        "phase": "foundation",
        "status": "in_progress",
        "priority": "critical",
        "order_index": 10,
    },
    {
        "project_slug": "whatsapp-notion-bot",
        "title": "Operacao ponta a ponta no WhatsApp",
        "description": "Objetivo final: receber mensagem, classificar, registrar no Notion e manter logs confiaveis. MVP: webhook ativo, fluxo real de gastos funcionando em producao e observabilidade minima. Dependencias: infra pronta e deploy consistente. Pronto quando: gasto enviado via WhatsApp cair no Notion com confiabilidade operacional.",
        "phase": "delivery",
        "status": "in_progress",
        "priority": "high",
        "order_index": 20,
    },
    {
        "project_slug": "pdf-factory",
        "title": "Pipeline de ativos digitais vendaveis",
        "description": "Objetivo final: transformar briefs em PDFs comercializaveis. MVP: uma linha de produto com template fixo, geracao padronizada e arquivo final organizado. Dependencias: Monarch AI estavel. Pronto quando: um briefing gerar um PDF final pronto para venda ou validacao comercial.",
        "phase": "mvp",
        "status": "planned",
        "priority": "high",
        "order_index": 30,
    },
    {
        "project_slug": "instagram-automation",
        "title": "Automacao segura de operacao no Instagram",
        "description": "Objetivo final: modularizar pesquisa, fila, aprovacao e publicacao assistida. MVP: pesquisa + geracao + fila de posts em fluxo seguro. Dependencias: base interna estavel e regras claras de automacao. Pronto quando: houver um pipeline modular reutilizavel para operar conteudo sem improviso manual.",
        "phase": "mvp",
        "status": "in_progress",
        "priority": "high",
        "order_index": 40,
    },
    {
        "project_slug": "canal-dark",
        "title": "Maquina de conteudo dark com nicho definido",
        "description": "Objetivo final: operar conteudo dark com pauta, roteiro, producao e distribuicao. MVP: um nicho principal, backlog inicial e primeiras pecas produzidas pelo fluxo novo. Dependencias: reaproveitamento parcial de automacoes de conteudo. Pronto quando: o canal tiver pipeline repetivel e primeiras publicacoes produzidas dentro dele.",
        "phase": "mvp",
        "status": "in_progress",
        "priority": "high",
        "order_index": 50,
    },
    {
        "project_slug": "achadinhos",
        "title": "Motor de descoberta e scoring de produtos",
        "description": "Objetivo final: encontrar e priorizar produtos fisicos com potencial comercial. MVP: catalogacao, criterios de analise e shortlist inicial. Dependencias: nenhuma tecnica forte. Pronto quando: houver fluxo claro para captar, pontuar e indicar produtos vencedores.",
        "phase": "discovery_to_mvp",
        "status": "in_progress",
        "priority": "high",
        "order_index": 60,
    },
    {
        "project_slug": "tiktok-shop",
        "title": "Operacao comercial inicial de TikTok Shop",
        "description": "Objetivo final: conectar produto, conteudo, oferta e validacao comercial. MVP: um produto validado em ciclo minimo de venda. Dependencias: Achadinhos. Pronto quando: houver um fluxo comercial minimo com produto selecionado, conteudo produzido e validacao de oferta.",
        "phase": "go_to_market",
        "status": "in_progress",
        "priority": "high",
        "order_index": 70,
    },
    {
        "project_slug": "solo-leveling-lab",
        "title": "Experimento autoral fechado e executavel",
        "description": "Objetivo final: transformar o lab em experimento criativo com entregavel concreto. MVP: um experimento definido com objetivo, formato e pipeline minimo de producao. Dependencias: baixa prioridade frente as frentes comerciais. Pronto quando: existir um experimento autoral completo, com escopo e primeiro entregavel produzido.",
        "phase": "lab",
        "status": "in_progress",
        "priority": "medium",
        "order_index": 80,
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

        project_result = await session.execute(select(Project))
        existing_projects = {project.slug: project for project in project_result.scalars().all()}
        projects_by_slug: dict[str, Project] = {}

        for project_data in PROJECTS:
            existing_project = existing_projects.get(project_data["slug"])
            unit = units_by_slug[project_data["business_unit_slug"]]
            if existing_project:
                existing_project.business_unit_id = unit.id
                existing_project.name = project_data["name"]
                existing_project.description = project_data["description"]
                existing_project.project_type = project_data["project_type"]
                existing_project.status = project_data["status"]
                existing_project.priority = project_data["priority"]
                existing_project.stage = project_data["stage"]
                existing_project.source_path = project_data["source_path"]
                existing_project.main_goal = project_data["main_goal"]
                existing_project.current_focus = project_data["current_focus"]
                existing_project.next_action = project_data["next_action"]
                continue

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

        task_records = await session.execute(select(Task))
        tasks_by_identity = {(task.title, task.project_id): task for task in task_records.scalars().all()}

        for task_data in TASKS:
            project = projects_by_slug[task_data["project_slug"]]
            identity = (task_data["title"], project.id)
            existing_task = tasks_by_identity.get(identity)
            if existing_task:
                existing_task.description = task_data["description"]
                existing_task.task_type = task_data["task_type"]
                existing_task.status = task_data["status"]
                existing_task.priority = task_data["priority"]
                existing_task.owner_type = task_data["owner_type"]
                existing_task.owner_name = task_data["owner_name"]
                existing_task.approval_required = task_data["approval_required"]
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

        roadmap_records = await session.execute(select(RoadmapItem))
        roadmap_items_by_identity = {
            (item.title, item.project_id): item for item in roadmap_records.scalars().all()
        }

        for item_data in ROADMAP_ITEMS:
            project = projects_by_slug[item_data["project_slug"]]
            identity = (item_data["title"], project.id)
            existing_item = roadmap_items_by_identity.get(identity)
            if existing_item:
                existing_item.description = item_data["description"]
                existing_item.phase = item_data["phase"]
                existing_item.status = item_data["status"]
                existing_item.priority = item_data["priority"]
                existing_item.order_index = item_data["order_index"]
                continue

            session.add(
                RoadmapItem(
                    project_id=project.id,
                    title=item_data["title"],
                    description=item_data["description"],
                    phase=item_data["phase"],
                    status=item_data["status"],
                    priority=item_data["priority"],
                    order_index=item_data["order_index"],
                )
            )

        await session.commit()
