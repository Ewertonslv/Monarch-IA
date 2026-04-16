# Roadmap v2 — Monarch AI

## Visão Geral

O Monarch AI tem duas camadas:

| Camada | O que é | Precisa API? |
|---|---|---|
| **Sistema Principal** | 11 agentes que recebem tarefa em linguagem natural e geram PRs | ✅ SIM |
| **Apps CLI** | 6 ferramentas locais para tarefas específicas | ❌ NÃO |

---

## Camada 1: Sistema Principal (requer API)

### O que é
Pipeline de agentes que:
1. Recebe uma tarefa em texto ("crie uma landing page")
2. Entende requisitos
3. Gera código
4. Cria PR no GitHub

### Precisa de API? ✅ SIM

**Por quê:**
- Os agentes usam LLM (Claude) para:
  - Entender linguagem natural
  - Decidir próximos passos
  - Gerar código
  - Escrever testes
  - Fazer code review
- Sem API, o sistema principal não funciona

**Alternativa se API expirou:**
- Usar apenas os Apps CLI (camada 2)
- Implementar agentes com modelos locais (futuro)

---

## Camada 2: Apps CLI (não requer API)

### O que são
6 ferramentas stand-alone que executam tarefas específicas localmente.

### Precisa de API? ❌ NÃO

**Por quê:**
- Toda lógica é código Python puro
- Não usam LLM para gerar conteúdo
- Entrada → Processamento local → Saída
- Sem custo de API

### Apps disponíveis

| App | O que faz | Exemplo de uso |
|---|---|---|
| `achadinhos` | Descobre e prioriza produtos | `python -m achadinhos add --title "X" --price 70` |
| `canal-dark` | Cria pautas e roteiros | `python -m canal_dark new --niche "historias"` |
| `instagram-automation` | Pesquisa e aprova conteúdo | `python -m instagram_automation research --niche "beleza"` |
| `solo-leveling-lab` | Transforma ideias em experimentos | `python -m solo_leveling_lab experiment --thesis "X"` |
| `tiktok-shop` | Valida comercialmente produtos | `python -m tiktok_shop plan --title "Y"` |
| `pdf-factory` | Gera documentos profissionais | `python -m pdf_factory run --title "Guia"` |

---

## Roadmap Detalhado

---

## Fase 1: Potencializar o Sistema (2-3 dias)

### 1. Agente de Auto-Test
**Precisa API:** ✅ SIM

**Por quê:** Gera testes usando LLM para entender o código e criar casos de teste relevantes. Usa Haiku (modelo barato).

**Alternativa sem API:** Templates fixos de testes (limitado).

---

### 2. Agente de Auto-Deploy
**Precisa API:** ❌ NÃO

**Por quê:** Apenas executa comandos de shell (git pull, docker compose). Não precisa de IA.

**O que faz:**
- SSH para servidor
- Roda scripts de deploy
- Verifica healthcheck
- Rollback se falhar

---

### 3. Agente de Code Review
**Precisa API:** ✅ SIM

**Por quê:** Analisa código usando LLM para identificar:
- Bugs potenciais
- Problemas de segurança
- Performance
- Estilo

**Alternativa sem API:** Linters estáticos (ruff, pylint) - já existem.

---

### 4. Circuit Breaker Visual
**Precisa API:** ❌ NÃO

**Por quê:** Apenas lê logs e exibe dashboards. Não gera conteúdo com IA.

**O que faz:**
- Monitora status dos agentes
- Mostra histórico de falhas
- Alertas via Telegram (webhook simples)

---

## Fase 2: Novos Apps de Negócio (3-4 dias)

### 5. copywriter-pro
**Precisa API:** ✅ SIM

**Por quê:** Gera copy usando LLM para:
- Entender o produto/serviço
- Adaptar tom e estilo
- Criar variações A/B

**Sem API:** Não é possível gerar texto dinâmico.

---

### 6. metric-analyzer
**Precisa API:** ⚠️ TALVEZ

**Por quê:** 
- Análise de padrões pode usar regras fixas
- Mas recomendações inteligentes precisam de LLM
- Decisão: depende do nível de personalização

**Alternativa sem API:** Dashboard com métricas brutas + alertas de thresholds.

---

### 7. ads-generator
**Precisa API:** ✅ SIM

**Por quê:** Gera:
- Copy para anúncios
- Estratégia de targeting
- Sugestões de orçamento

**Sem API:** Templates pré-definidos (limitado).

---

### 8. seo-content
**Precisa API:** ✅ SIM

**Por quê:** Gera artigos otimizados usando LLM para:
- Pesquisar keywords
- Estruturar conteúdo
- Otimizar meta tags

**Sem API:** Geração de templates estáticos.

---

## Fase 3: Monetização (2-3 dias)

### 9. Landing Page
**Precisa API:** ❌ NÃO

**Por quê:** Página estática em HTML/CSS. Sem processamento dinâmico.

---

### 10. Sistema de Pricing
**Precisa API:** ❌ NÃO

**Por quê:** Lógica de negócio em Python. Integração com Stripe usa SDK, não LLM.

**O que faz:**
- Planos free/pro/enterprise
- Controle de uso
- Cobrança via Stripe/Pagar.me

---

### 11. API Key System
**Precisa API:** ❌ NÃO

**Por quê:** Sistema de autenticação clássico (JWT, hash). Não usa LLM.

---

### 12. Dashboard de Uso
**Precisa API:** ❌ NÃO

**Por quê:** Apenas lê logs e exibe métricas. Código Python puro.

---

## Fase 4: Ecossistema Integrado (2-3 dias)

### 13. Funil Completo
**Precisa API:** ❌ NÃO

**Por quê:** Conecta apps existentes via CLI e arquivos JSON. Não usa IA.

**Fluxo:**
```
achadinhos → produtos.json
    ↓
tiktok-shop → plano.json
    ↓
pdf-factory → documento.pdf
    ↓
instagram-automation → fila.json
```

---

### 14. Orquestrador de CLIs
**Precisa API:** ❌ NÃO

**Por quê:** Apenas executa comandos em sequência/paralelo. Sem IA.

**O que faz:**
- `monarch funnel --produto "Escova Secadora"`
- Coordena todos os apps
- Passa dados entre eles

---

### 15. Banco de Dados Unificado
**Precisa API:** ❌ NÃO

**Por quê:** SQLite + SQLAlchemy. Arquitetura de dados pura.

---

### 16. Webhook de Eventos
**Precisa API:** ❌ NÃO

**Por quê:** Sistema pub/sub interno em Python. Não usa IA.

---

## Fase 5: Lançamento (1-2 dias)

### 17. README Comercial
**Precisa API:** ❌ NÃO

**Por quê:** Markdown estático. Você escreve o conteúdo.

---

### 18. Demo Video
**Precisa API:** ❌ NÃO

**Por quê:** Gravação de tela + edição. Você mesmo grava.

---

### 19. Documentação API
**Precisa API:** ❌ NÃO

**Por quê:** OpenAPI gera automaticamente a partir do código FastAPI.

---

### 20. CI/CD Otimizado
**Precisa API:** ❌ NÃO

**Por quê:** GitHub Actions executa scripts. Não usa IA.

---

## Resumo Final

### Itens que PRECISAM de API

| # | Item | Motivo |
|---|---|---|
| 1 | Sistema principal (11 agentes) | Gera código com LLM |
| 1 | Agente de auto-test | Gera testes com LLM |
| 3 | Agente de code review | Analisa código com LLM |
| 5 | copywriter-pro | Gera texto com LLM |
| 7 | ads-generator | Gera copy com LLM |
| 8 | seo-content | Gera artigos com LLM |

**Total: 6 itens (30%)**

### Itens que NÃO precisam de API

| # | Item | Motivo |
|---|---|---|
| 2 | Agente de auto-deploy | Apenas executa shell |
| 4 | Circuit breaker visual | Apenas lê logs |
| 6 | metric-analyzer | Regras fixas (talvez LLM) |
| 9-12 | Monetização | Lógica de negócio |
| 13-16 | Ecossistema | Integração de apps |
| 17-20 | Lançamento | Docs e CI/CD |

**Total: 14 itens (70%)**

---

## Conclusão

Você pode construir **70% do roadmap sem gastar um centavo de API**. 

A **Fase 4 (Ecossistema)** é 100% gratuita e conecta tudo que já existe.

As **Fases 1-2** que usam API podem usar **Haiku** (modelo mais barato) para manter custos baixos.

---

## Status Atual

### Sistema Principal
- 11 agentes ✅ (requer API)
- 94 testes ✅

### Apps CLI
- pdf-factory ✅ (19 testes)
- achadinhos ✅ (8 testes)
- instagram-automation ✅ (10 testes)
- canal-dark ✅ (10 testes)
- tiktok-shop ✅ (8 testes)
- solo-leveling-lab ✅ (8 testes)

**Total apps: 6 (100% funcionais sem API)**
