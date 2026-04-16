# Monarch AI

Sistema multi-agente que automatiza desenvolvimento SaaS.

## Apps (CLI locais, sem custo de API)

| App | Comando |
|---|---|
| achadinhos | `python -m achadinhos add/sortlist/catalog` |
| canal-dark | `python -m canal_dark new/backlog/script` |
| instagram-automation | `python -m instagram_automation research/queue/approve` |
| solo-leveling-lab | `python -m solo_leveling_lab experiment/outline` |
| tiktok-shop | `python -m tiktok_shop plan/validate/score` |
| pdf-factory | `python -m pdf_factory run --title X --audience Y` |

## CLI Natural

```bash
python -m interfaces.cli "shortlist de achadinhos"
python -m interfaces.cli "experimento solo leveling sobre X"
python -m interfaces.cli "crie o projeto canal dark para nicho de Y"
```

## Sistema principal

```bash
python main.py           # web + telegram
python -m pytest         # testes
```

**Stack:** Python 3.14, Anthropic SDK, FastAPI, Telegram, SQLite.

**Regras:** CLI local antes de API. Smart dispatch: Sonnet para implementar, Haiku para testes/boilerplate.
