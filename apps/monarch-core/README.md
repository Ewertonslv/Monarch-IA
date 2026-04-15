# Monarch Phase 1 Core API

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
- CRUD inicial de `agent_profiles`
- CRUD inicial de `roadmap_items`
- `GET /api/dashboard/overview`
- `GET /api/dashboard/activity`
- `GET /api/dashboard/performance`
- seed inicial com suas unidades e projetos atuais

## Variaveis

Copie `.env.example` para `.env` e ajuste.
Mantenha `AUTO_SEED=false` ate rodar a migration inicial.

Se quiser proteger os endpoints `/api/*`, defina:

```env
MONARCH_CORE_API_KEY=seu-token-interno
```

Quando preenchida, toda chamada para `/api/*` precisa enviar header `X-API-Key`.

## Rodando localmente

```bash
pip install -r apps/monarch-core/requirements.txt
uvicorn app.main:app --app-dir apps/monarch-core --reload --port 8010
```

## Alembic

```bash
alembic -c apps/monarch-core/alembic.ini upgrade head
```

Depois da migration, se quiser popular dados iniciais automaticamente no start, ajuste:

```env
AUTO_SEED=true
```
