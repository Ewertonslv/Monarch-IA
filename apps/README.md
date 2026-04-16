# Apps

Pastas canonicas de aplicacoes do ecossistema.

## Status

| App | Status | Descricao |
|---|---|---|
| `monarch-core` | **FUNCIONAL** | API FastAPI + SQLAlchemy com 8 entidades, migrations, Docker |
| `monarch-web` | **PARCIAL** | Painel FastAPI que consome monarch-core |
| `monarch-runtime` | **WRAPPER** | Wrapper para entrypoints da raiz |
| `pdf-factory` | **COMERCIAL** | Pipeline CLI de briefs para MD/HTML/PDF com testes |
| `achadinhos` | **COMERCIAL** | Pipeline CLI de discovery e scoring de produtos |
| `instagram-automation` | **COMERCIAL** | Pipeline CLI de pesquisa, fila e aprovacao |
| `canal-dark` | **COMERCIAL** | Pipeline CLI de pautas e roteiros |
| `tiktok-shop` | **COMERCIAL** | Pipeline CLI de oferta e validacao comercial |
| `solo-leveling-lab` | **COMERCIAL** | Pipeline CLI de experimento criativo |
| `whatsapp-notion-bot` | **FUNCIONAL** | Bot Z-API + Claude + Notion com Docker |

## apps/ vs raiz

- **apps/**: caminho canonico para todas as aplicacoes
- **whatsapp_notion_bot/ (raiz)**: legado — referencias canonicas estao em `apps/whatsapp-notion-bot/`
- **monarch_phase1/**:_DEPRECADO — conteudo antigo em `apps/monarch-core/`
