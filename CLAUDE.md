# Monarch AI

Sistema multi-agente que automatiza desenvolvimento SaaS. Recebe tarefa em linguagem natural e entrega PR testado no GitHub.

**Stack:** Python 3.14, Anthropic SDK, FastAPI, Telegram Bot, SQLite.

## Execução

```bash
python main.py              # web + telegram
python -m pytest            # todos os testes
python -m interfaces.cli    # CLI natural
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
apps/          # 10 aplicacoes stand-alone
infra/         # deploy, scripts
```

## Apps (em apps/)

| App | Descricao |
|---|---|
| monarch-core | API FastAPI + SQLAlchemy |
| monarch-web | Painel FastAPI (consome monarch-core) |
| monarch-runtime | Wrapper entrypoints |
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

## Skills

| Skill | Quando |
|---|---|
| brainstorming | Novas features, arquitetura |
| writing-plans | Antes de implementar |
| systematic-debugging | Pipeline falhando |
| security-review | APIs ou credenciais |
| cost-reducer | Auditar contexto e otimizar tokens |

## Design

- Sem LangChain/CrewAI — Anthropic SDK puro
- Prompt caching em todos os agentes (~80% reducao)
- Agentes retornam JSON, parse via `_extract_json()`
- Circuit breaker por agente
- 2 gates de aprovacao humana

## REGRAS DE OTIMIZACAO

### Smart Model Dispatch

| Tarefa | Modelo | Custo |
|---|---|---|
| Implementar agentes novos | Sonnet | $$ |
| Modificar orchestrator | Sonnet | $$ |
| Arquitetura de novos agentes | Opus | $$$ |
| Planejamento de pipeline | Opus | $$$ |
| Gerar tests unitarios | Haiku | $ |
| Criar README / boilerplate | Haiku | $ |
| Corrigir lint e formatacao | Haiku | $ |
| Templates HTML/CSS/CLI | Haiku | $ |
| Operacoes em batch | Haiku | $ |
| Tudo nos apps/ via CLI | ZERO API | $0 |

### Contexto < 150 linhas

Audite duplicacoes se este arquivo crescer demais.

### CLI Natural antes de API

SEMPRE tente `python -m interfaces.cli` antes de acionar agentes via API.
