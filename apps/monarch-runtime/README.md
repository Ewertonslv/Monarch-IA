# Monarch Runtime

Camada canonica do runtime principal do Monarch.

Objetivo:

- concentrar os pontos de entrada do app principal
- preparar a futura migracao completa do runtime para dentro de `apps/`
- manter compatibilidade com os imports atuais do repositorio

Estado atual:

- `main.py`: wrapper do entrypoint principal
- `cli.py`: wrapper da CLI atual
- `telegram_bot.py`: reexport do bot atual

Observacao:

- O codigo-fonte operacional ainda continua em `main.py`, `interfaces/`, `core/`, `agents/`, `storage/` e `tools/`.
- Esta pasta passa a ser o caminho canonico para a organizacao do runtime, sem forcar uma quebra brusca do projeto agora.
