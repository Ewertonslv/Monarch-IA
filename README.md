# Monarch Hub

Estrutura principal do repositorio:

- `apps/monarch-core/`: nucleo do hub com business units, projetos, ideias, tarefas, aprovacoes, execucoes e metricas
- `apps/monarch-web/`: copia canonica do painel web do hub
- `apps/monarch-runtime/`: wrappers canonicos do runtime principal do Monarch
- `apps/whatsapp-notion-bot/whatsapp_notion_bot/`: bot de WhatsApp para controle financeiro
- `infra/deploy/`: nginx, envs e configuracao de deploy
- `infra/scripts/`: bootstrap e automacao de deploy
- `interfaces/`: web app e bot do Telegram do Monarch
- `core/`, `agents/`, `storage/`, `tools/`: runtime atual do Monarch AI
- `tests/`: testes do app principal

Observacoes:

- Algumas pastas antigas como `deploy/`, `scripts/` e `monarch_phase1/core_api/` foram mantidas temporariamente como compatibilidade enquanto o ambiente ainda estava com lock para mover/remover diretorios.
- `interfaces/web/` tambem segue como compatibilidade temporaria; a copia canonica do painel agora esta em `apps/monarch-web/`.
- `main.py` e `interfaces/` continuam como runtime atual, mas `apps/monarch-runtime/` passa a ser o caminho canonico de entrada para a futura migracao.
- Os caminhos canonicos novos para seguir daqui em diante sao `apps/` e `infra/`.
