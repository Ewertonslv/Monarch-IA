# Monarch Runtime

Wrapper canonico para os pontos de entrada do Monarch AI.

## Execução

```bash
# Da raiz do monach-IA
PYTHONPATH=. python apps/monarch_runtime/main.py          # web + telegram
PYTHONPATH=. python apps/monarch_runtime/cli.py run "..." # CLI
```

## Estrutura

| Arquivo | O que faz |
|---|---|
| `main.py` | Executa `main.main()` da raiz |
| `cli.py` | Executa `interfaces.cli.main()` da raiz |
| `telegram_bot.py` | Wrapper do Telegram bot |

## Nota

O codigo-fonte real permanece em `main.py`, `interfaces/`, `core/`, `agents/`, `storage/` e `tools/` na raiz do monach-IA. Esta pasta e o caminho canonico de organizacao — nao duplica nada.
