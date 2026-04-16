# Monarch AI — Contexto Compacto

Stack: Python 3.14, Anthropic SDK, FastAPI, Telegram Bot, SQLite, PyGithub, pytest.

## Execução

```bash
python main.py          # web + telegram
python -m pytest       # todos os testes
python -m pytest tests/unit/test_orchestrator.py -v
```

## Config (.env)

`ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GITHUB_REPO`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Arquitetura

```
core/          # orchestrator, task, circuit_breaker
agents/        # 11 agentes (discovery → observability)
tools/         # github, code, fs
storage/       # SQLite via SQLAlchemy
interfaces/    # web, telegram, cli
```

## Apps (em apps/)

| App | Descricao |
|---|---|
| monarch-core | API FastAPI + SQLAlchemy, 8 entidades |
| monarch-web | Painel FastAPI que consome monarch-core |
| monarch-runtime | Wrapper de entrypoints |
| pdf-factory | CLI: briefs → MD/HTML/PDF |
| achadinhos | CLI: discovery + scoring de produtos |
| instagram-automation | CLI: pesquisa, fila, aprovacao |
| canal-dark | CLI: pautas e roteiros |
| tiktok-shop | CLI: oferta e validacao comercial |
| solo-leveling-lab | CLI: experimento criativo |
| whatsapp-notion-bot | Bot Z-API + Notion |

## CLI Natural (sem API)

```bash
python -m interfaces.cli "shortlist de achadinhos"
python -m interfaces.cli "experimento solo leveling sobre X"
python -m interfaces.cli "crie o projeto canal dark para nicho de Y"
```

## Skills Disponiveis

| Skill | Quando |
|---|---|
| brainstorming | Novas features, arquitetura |
| writing-plans | Antes de implementar |
| systematic-debugging | Pipeline falhando |
| security-review | PRs com APIs ou credenciais |
| gh-fix-ci | CI quebrando |
| cost-reducer | Auditar contexto e otimizar tokens |

## Design

- Sem LangChain/CrewAI — Anthropic SDK puro
- Prompt caching em todos os agentes (~80% reducao)
- Agentes retornam JSON, parse via `_extract_json()`
- Circuit breaker por agente
- 2 gates de aprovacao humana

## Tests

94 testes unitarios + integracao. apps/ tem testes independentes.
