# Monarch AI

Sistema multi-agente que automatiza desenvolvimento SaaS.

## Leitura inicial para qualquer IA

Antes de usar qualquer IA neste repositorio, peca para ela ler:

- `docs/ai-operator-context.md`
- `docs/active-incubations.md`

Esses arquivos explicam o papel do `Monarch AI`, a finalidade de cada projeto-filho, a regra operacional `CLI-first` e o backlog incubado mais recente dos projetos ativos.

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

## CLI de Incubacao

```bash
python -m interfaces.cli ideate "perfil de instagram sobre IA para vender servicos" --project instagram
python -m interfaces.cli incubate "canal dark de cortes diarios com afiliados" --project canal-dark
python -m interfaces.cli incubate "catalogo de produtos afiliados para videos curtos" --project achadinhos
python -m interfaces.cli projects
```

## Sistema principal

```bash
python main.py           # web + telegram
python -m pytest         # testes
```

**Stack:** Python 3.14, Anthropic SDK, FastAPI, Telegram, SQLite.

**Regras:** CLI local antes de API. Smart dispatch: Sonnet para implementar, Haiku para testes/boilerplate.
