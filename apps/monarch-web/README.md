# Monarch Web

Painel web do Monarch Hub — interface FastAPI com Jinja2 que consome o monarch-core via API.

## Dependencias

O `monarch-web` depende do codigo do monach-IA na raiz. O `PYTHONPATH` precisa apontar para a raiz do projeto.

## Instalacao

```bash
pip install -r requirements.txt
```

## Execução

```bash
# Da raiz do monach-IA
PYTHONPATH=. python -m apps.monarch_web.app
# ou
PYTHONPATH=. uvicorn apps.monarch_web.app:app --reload --port 8000
```

## Endpoints principais

| Metodo | Path | Descricao |
|---|---|---|
| GET | `/` | Painel principal |
| GET | `/hub/overview` | Dashboard geral |
| GET | `/hub/projects` | Lista de projetos |
| GET | `/hub/ideas` | Lista de ideias |
| GET | `/hub/tasks` | Lista de tarefas |
| GET | `/hub/approvals` | Lista de aprovacoes |
| POST | `/tasks` | Criar tarefa |
| GET | `/ws` | WebSocket para updates em tempo real |

## Configuracao

As variaveis de ambiente sao lidas do `.env` na raiz do monach-IA. O app sincroniza com o `monarch-core` via `MONARCH_CORE_API_URL` e `MONARCH_CORE_API_KEY`.

## Modo read-only

Quando `HUB_READ_ONLY=true` (default), o painel e somente leitura. Use CLI ou Telegram para executar tarefas.

## Estrutura

```
monarch_web/
  app.py              # FastAPI completo com ~50 endpoints
  templates/
    hub.html          # Interface principal
    index.html        # Compatibilidade
  requirements.txt
  Dockerfile
```
