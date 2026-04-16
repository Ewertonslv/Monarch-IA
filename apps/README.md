# Apps

Pastas canonicas de aplicacoes do ecossistema:

- `monarch-core/`: API central do Monarch Hub
- `monarch-web/`: painel web atual do Monarch Hub
- `monarch-runtime/`: entrypoints canonicos do runtime principal do Monarch
- `pdf-factory/`: pipeline local de briefs para ativos digitais
- `instagram-automation/`: pipeline local de pesquisa, fila e publicacao assistida
- `achadinhos/`: pipeline local de descoberta, scoring e shortlist de produtos
- `tiktok-shop/`: pipeline local de oferta e validacao comercial inicial
- `whatsapp-notion-bot/`: bot WhatsApp -> Notion para controle financeiro

Observacao:

- a pasta raiz legada `whatsapp_notion_bot/` nao e a referencia principal para novas mudancas
- novas implementacoes devem priorizar sempre os caminhos canonicos dentro de `apps/`
