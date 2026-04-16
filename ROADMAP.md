# Roadmap — Monarch AI

## Resumo

Sistema multi-agente que automatiza desenvolvimento SaaS. Já possui 10 apps funcionais e 6 CLIs operacionais. Este roadmap expande o ecossistema em 5 fases.

---

## Fase 1: Potencializar o Sistema (2-3 dias)

### 1. Agente de Auto-Test
- Gera testes unitários automaticamente após cada PR
- Usa Haiku (custo baixo) para gerar覆盖率 de testes
- Valida que o código implementa o que o plano especificou

### 2. Agente de Auto-Deploy
- Faz deploy automaticamente após testes passarem
- Integração com Hetzner/DigitalOcean via SSH
- Rollback automático se healthcheck falhar

### 3. Agente de Code Review
- Analisa PRs antes de mesclar
- Verifica: estilo, segurança, performance, documentação
- Feedback inline no GitHub

### 4. Circuit Breaker Visual
- Dashboard mostrando saúde dos agentes em tempo real
- Histórico de falhas e recoverys
- Alertas via Telegram quando agente cai

---

## Fase 2: Novos Apps de Negócio (3-4 dias)

### 5. copywriter-pro
- Gera copy para ads, landing pages, email marketing
- Templates: AIDA, PAS, storytelling
- Suporte a múltiplos tons: formal, casual, urgente

### 6. metric-analyzer
- Analisa métricas de Instagram/TikTok
- Dashboard de crescimento
- Sugestões de ações baseadas em padrões

### 7. ads-generator
- Cria campanhas completas para Meta/TikTok Ads
- Briefing → copy → imagens → targeting → budget
- Exporta para formato nativo das plataformas

### 8. seo-content
- Gera artigos otimizados para SEO
- Pesquisa de keywords automaticamente
- Meta description, headers, internal linking

---

## Fase 3: Monetização (2-3 dias)

### 9. Landing Page
- Página de apresentação do Monarch AI
- Demonstração interativa
- Formulário de contato/trial

### 10. Sistema de Pricing
- Planos: Free (5 tasks/mês), Pro ($29/mês - ilimitado), Enterprise (custom)
- Integração com Stripe/Pagar.me
- Faturação mensal/anual

### 11. API Key System
- Autenticação para usuários externos
- Rate limiting por plano
- Dashboard de uso por API key

### 12. Dashboard de Uso
- Mostra tokens gastos por cliente
- Histórico de requisições
- Alertas de orçamento

---

## Fase 4: Ecossistema Integrado (2-3 dias)

### 13. Funil Completo

```
achadinhos (descoberta)
    ↓
tiktok-shop (validação comercial)
    ↓
pdf-factory (material de venda)
    ↓
instagram-automation (divulgação)
    ↓
canal-dark (conteúdo recorrente)
```

- Cada app passa dados para o próximo automaticamente
- Estado compartilhado em SQLite centralizado
- CLI único que orchestrates todo funil

### 14. Orquestrador de CLIs
- CLI central que coordena todos os apps
- `monarch funnel --produto "Escova Secadora"`
- Execução paralela onde possível

### 15. Banco de Dados Unificado
- SQLite compartilhado entre apps
- Tabelas: produtos, campanhas, métricas, tarefas
- Migrações com Alembic

### 16. Webhook de Eventos
- Apps se notificam quando algo muda
- Sistema pub/sub interno
- Fila de eventos assíncronos

---

## Fase 5: Lançamento (1-2 dias)

### 17. README Comercial
- Descrição vendável no GitHub
- Badges: tests, coverage, version
- Screenshots e GIFs do sistema

### 18. Demo Video
- Vídeo mostrando o sistema em ação
- 2-3 minutos
- Narração + legenda

### 19. Documentação API
- OpenAPI/Swagger para devs
- Postman collection
- Exemplos em Python, JS, curl

### 20. CI/CD Otimizado
- GitHub Actions com cache e paralelismo
- Testes em múltiplas versões de Python
- Deploy automático em staging

---

## Tempo Total

- Fase 1: 2-3 dias
- Fase 2: 3-4 dias
- Fase 3: 2-3 dias
- Fase 4: 2-3 dias
- Fase 5: 1-2 dias

**Total: ~12-18 dias**

---

## Prioridade Recomendada

1. **Fase 4 (Ecossistema)** — conecta o que já existe e gera valor imediato
2. **Fase 2 (Novos Apps)** — expande capacidades de negócio
3. **Fase 1 (Agentes)** — fortalece o core system
4. **Fase 3 (Monetização)** — prepara para revenue
5. **Fase 5 (Lançamento)** — coloca no ar

---

## Status Atual

### Sistema Principal (monach-IA)
- 11 agentes implementados
- FastAPI + Telegram Bot + CLI
- SQLite + SQLAlchemy
- 94 testes passando

### Apps em apps/
| App | Status | Tests |
|---|---|---|
| monarch-core | ✅ Funcional | — |
| monarch-web | ✅ Funcional | — |
| monarch-runtime | ✅ Wrapper | — |
| pdf-factory | ✅ Completo | 19 |
| achadinhos | ✅ Completo | 8 |
| instagram-automation | ✅ Completo | 10 |
| canal-dark | ✅ Completo | 10 |
| tiktok-shop | ✅ Completo | 8 |
| solo-leveling-lab | ✅ Completo | 8 |
| whatsapp-notion-bot | ✅ Funcional | — |

**Total de testes nos apps: 63**

---

## Dependências Externas

- ANTHROPIC_API_KEY (Anthropic)
- GITHUB_TOKEN (GitHub API)
- TELEGRAM_BOT_TOKEN (Telegram)
- Z-API_KEY (WhatsApp Bot)
- NOTION_API_KEY (Notion)
- Stripe/Pagar.me (futuro, monetização)
