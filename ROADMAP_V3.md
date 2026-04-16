# Roadmap v3 — Monarch AI (Revisado)

## Corrigindo Conceitos

Errei em alguns pontos. Aqui está a verdade:

| Item | Minha claim | Realidade |
|---|---|---|
| Auto-test | Usa API | ❌ Pode ser template-based |
| Landing page | Usa API | ❌ É HTML/CSS puro |
| Ads-generator | Usa API | ⚠️ Templates podem funcionar |
| SEO-content | Usa API | ⚠️ Templates + tools |

---

## O Verdadeiro Uso de API

### Quando a API é NECESSÁRIA
- Gerar texto criativo/único (copy, artigos, descrições)
- Entender contexto complexo
- Tom e estilo personalizado
- Respostas dinâmicas

### Quando a API é DESPENSÁVEL
- Templates fixos (landing pages, ads)
- Análise estática (testes, code review básico)
- Processamento de dados (métricas)
- Geração de estrutura (roteiros)

---

## Itens Revisados

### 1. Agente de Auto-Test
**API necessária:** ❌ NÃO

**Por quê:**
- Analisa estrutura do código (AST parsing)
- Aplica templates de teste por tipo de arquivo
- Detecta padrões (CRUD → testes de integração)
-覆盖率 baseado em templates

**Funciona assim:**
```
Código Python → Analisa imports, funções, classes
              → Seleciona template de teste
              → Preenche com nomes reais
              → Gera test_*.py
```

---

### 2. Agente de Auto-Deploy
**API necessária:** ❌ NÃO

**Por quê:** Apenas executa shell commands.

---

### 3. Agente de Code Review
**API necessária:** ⚠️ OPCIONAL

**Versão sem API:**
- Ruff para estilo
- Pylint para bugs
- Bandit para segurança
- Semântica limitada

**Versão com API (avançado):**
- Análise de contexto
- Sugestões de refatoração
- Padrões de arquitetura

---

### 4. Circuit Breaker Visual
**API necessária:** ❌ NÃO

**Por quê:** Apenas lê logs e exibe.

---

### 5. copywriter-pro
**API necessária:** ✅ SIM

**Por quê:** Gera texto único e criativo. Templates não funcionam aqui.

---

### 6. metric-analyzer
**API necessária:** ❌ NÃO

**Por quê:**
- Recebe dados (CSV, JSON, API do Instagram)
- Calcula métricas (crescimento, engajamento)
- Aplica regras fixas (alertas de queda)
- Gera dashboard

**Não precisa de IA para:**
- Plotar gráficos
- Calcular médias
- Detectar anomalias por threshold

---

### 7. ads-generator
**API necessária:** ⚠️ OPCIONAL

**Versão sem API:**
- Templates de copy (AIDA, PAS)
- Estrutura fixa de anuncio
- Targeting baseado em regras
- Variações por número (não por IA)

**Versão com API (avançado):**
- Copy personalizado por produto
- Targeting dinâmico
- A/B testing inteligente

---

### 8. seo-content
**API necessária:** ⚠️ OPCIONAL

**Versão sem API:**
- Templates de artigo (intro, corpo, conclusão)
- Estrutura SEO fixa (H1, H2, meta)
- Keyword research via APIs públicas (Google, Ubersuggest)

**Versão com API (avançado):**
- Conteúdo unique e Engaging
- Otimização semântica
- Sugestões de internal linking

---

### 9. Landing Page
**API necessária:** ❌ NÃO

**Por quê:**
- Templates HTML/CSS prontos
- Seção Hero, Features, Pricing, CTA
- Formulário de contato (endpoint simples)
- Zero processamento dinâmico

**Funciona assim:**
```
Escolhe template (startup, produto, portfolio)
Preenche dados (nome, descrição, features)
Gera index.html
```

---

### 10. Sistema de Pricing
**API necessária:** ❌ NÃO

**Por quê:** Lógica de negócio em Python.

---

### 11. API Key System
**API necessária:** ❌ NÃO

**Por quê:** JWT + hash + rate limiting.

---

### 12. Dashboard de Uso
**API necessária:** ❌ NÃO

**Por quê:** Apenas lê logs e exibe.

---

### 13. Funil Completo
**API necessária:** ❌ NÃO

**Por quê:** Integração de apps via CLI + JSON.

---

### 14. Orquestrador de CLIs
**API necessária:** ❌ NÃO

**Por quê:** Executa comandos em sequência.

---

### 15. Banco de Dados Unificado
**API necessária:** ❌ NÃO

**Por quê:** SQLite + SQLAlchemy.

---

### 16. Webhook de Eventos
**API necessária:** ❌ NÃO

**Por quê:** Pub/sub em Python.

---

### 17. README Comercial
**API necessária:** ❌ NÃO

**Por quê:** Markdown estático.

---

### 18. Demo Video
**API necessária:** ❌ NÃO

**Por quê:** Gravação de tela.

---

### 19. Documentação API
**API necessária:** ❌ NÃO

**Por quê:** OpenAPI gera automaticamente.

---

### 20. CI/CD Otimizado
**API necessária:** ❌ NÃO

**Por quê:** GitHub Actions + scripts.

---

## Resumo Revisado

### Precisa de API (geração de texto único)

| Item | Motivo |
|---|---|
| copywriter-pro | Texto criativo |

**Total: 1 item (5%)**

### API Opcional (melhora com IA)

| Item | Sem API | Com API |
|---|---|---|
| code-review | Ruff/Pylint | Análise semântica |
| ads-generator | Templates | Copy personalizado |
| seo-content | Templates | Artigos únicos |

**Total: 3 itens (15%)**

### NÃO precisa de API (lógica + templates)

| Item | Motivo |
|---|---|
| auto-test | Templates + AST |
| auto-deploy | Shell commands |
| circuit-breaker | Logs |
| metric-analyzer | Dados + regras |
| landing-page | HTML/CSS |
| pricing | Lógica |
| api-key | Auth |
| dashboard | Logs |
| funil | CLI + JSON |
| orquestrador | Shell |
| banco-dados | SQLite |
| webhook | Pub/sub |
| readme | Markdown |
| demo | Gravação |
| docs | OpenAPI |
| cicd | GitHub Actions |

**Total: 16 itens (80%)**

---

## Conclusão

**80% do roadmap pode ser construído SEM API.**

**copywriter-pro é o único item que REALMENTE precisa de API** para geração de texto único.

Os outros 2 (code-review, ads-generator, seo-content) funcionam com templates, mas ficam melhores com IA.

---

## Prioridade Sem API

### Fase 1: Core (sem API)
1. Auto-test (templates)
2. Auto-deploy (shell)
3. Circuit breaker (logs)
4. Code review (ruff/pylint)

### Fase 2: Monetização (sem API)
5. Landing page (HTML/CSS)
6. Pricing
7. API key
8. Dashboard

### Fase 3: Ecossistema (sem API)
9. Funil completo
10. Orquestrador
11. Banco unificado
12. Webhooks

### Fase 4: Apps (API opcional)
13. copywriter-pro (✅ precisa API)
14. ads-generator (templates + opcional API)
15. seo-content (templates + opcional API)
16. metric-analyzer (dados + regras)

### Fase 5: Lançamento (sem API)
17. README
18. Demo
19. Docs
20. CI/CD

---

## MCP Servers (Gratuitos)

### 🎨 Geração Visual
| MCP | O que faz | Status |
|-----|-----------|--------|
| Stitch | Gera UI/web designs (HTML) | ✅ Configurado |
| EverArt | Gera imagens (DALL-E, Flux) | ⬜ |

### 🔍 Busca & Informação
| MCP | O que faz | Status |
|-----|-----------|--------|
| Brave Search | Busca na web | ⬜ |
| Web Search (SearXNG) | Meta-busca sem API | ⬜ |
| Fetch | Baixa e limpa páginas web | ✅ Configurado |

### 📁 Arquivos & Sistema
| MCP | O que faz | Status |
|-----|-----------|--------|
| Filesystem | Ler/escrever arquivos locais | ⬜ |
| Google Drive | Arquivos no Drive | ⬜ |

### 🛠️ Desenvolvimento
| MCP | O que faz | Status |
|-----|-----------|--------|
| GitHub | Issues, PRs, repositório | ✅ Configurado |
| Sentry | Monitoramento de erros | ⬜ |
| PostgreSQL | Acesso a bancos | ⬜ |

### 💬 Comunicação
| MCP | O que faz | Status |
|-----|-----------|--------|
| Slack | Enviar mensagens, canais | ⬜ |
| Notion | Ler/escrever páginas | ⬜ (já temos) |

---

## Prioridade de Implementação

### 🔴 Essenciais (precisa ter)
| MCP | Por quê |
|-----|---------|
| **Filesystem** | Fundamental para os CLIs existentes - ler/escrever arquivos, criar projetos |
| **Stitch** | ✅ Já configurado - criar UIs automaticamente |
| **GitHub** | Já usa a API do GitHub - unifica issues, PRs, code review |

### 🟡 Importantes (vale a pena)
| MCP | Por quê |
|-----|---------|
| **Fetch** | Research - buscar conteúdo de páginas para contexto |
| **Brave Search** | Pesquisa web sem custo de API |
| **EverArt** | Gerar imagens para capas de PDFs, posts Instagram |

### 🟢 Opcional
| MCP | Por quê |
|-----|---------|
| **Notion** | Já temos integração manual |
| **Slack** | Notificações de pipeline |
| **Sentry** | Monitoramento (depois que tiver algo em produção)
