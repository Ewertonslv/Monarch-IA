# Monarch Phase 1 Core API

> Pasta legada temporaria. O caminho canonico agora e `apps/monarch-core/`.

Base inicial do `monarch-core` para centralizar unidades de negocio, projetos e ideias.

## Componentes

- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic

## Recursos desta entrega

- `GET /health`
- CRUD inicial de `business_units`
- CRUD inicial de `projects`
- CRUD inicial de `ideas`
- CRUD inicial de `tasks`
- CRUD inicial de `approvals`
- CRUD inicial de `executions`
- `GET /api/dashboard/overview`
- `GET /api/dashboard/activity`
- seed inicial com suas unidades e projetos atuais

## Variaveis

Copie `.env.example` para `.env` e ajuste.
Mantenha `AUTO_SEED=false` ate rodar a migration inicial.

## Rodando localmente

```bash
pip install -r monarch_phase1/core_api/requirements.txt
uvicorn app.main:app --app-dir monarch_phase1/core_api --reload --port 8010
```

## Alembic

```bash
alembic -c monarch_phase1/core_api/alembic.ini upgrade head
```

Depois da migration, se quiser popular dados iniciais automaticamente no start, ajuste:

```env
AUTO_SEED=true
```
