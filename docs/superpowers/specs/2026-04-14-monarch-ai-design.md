# Monarch AI — Design Spec

**Data:** 2026-04-14  
**Status:** Aprovado pelo usuário  
**Versão:** v1 (MVP interno)

---

## 1. Objetivo

Construir um sistema de agentes de IA autônomos para automatizar processos de desenvolvimento de software. O sistema recebe demandas em linguagem natural (via Claude Code ou Telegram), as transforma em código funcional testado e documentado, e entrega um PR no GitHub pronto para revisão humana — com intervenção mínima.

**Escopo v1:** Automação interna de desenvolvimento de software.  
**Fora do escopo v1:** Marketing, vendas, suporte, multi-tenancy, deploy automático em produção.

---

## 2. Stack Técnico

| Componente | Tecnologia |
|---|---|
| Linguagem principal | Python 3.12 |
| LLM | Claude (Anthropic SDK) com prompt caching |
| Orquestração | Custom — sem frameworks externos (LangChain, CrewAI) |
| Web UI | FastAPI + HTML/JS vanilla |
| Notificações | python-telegram-bot |
| GitHub | PyGithub |
| Persistência | SQLite (MVP) → PostgreSQL (produção) |
| Testes | pytest + pytest-asyncio |
| Linting/tipos | ruff + mypy |

---

## 3. Arquitetura

### Estrutura de Arquivos

```
monarch_ai/
├── core/
│   ├── orchestrator.py      # Gerencia fluxo, estado e decisões
│   ├── context.py           # TaskContext — persiste tudo de uma tarefa
│   └── task.py              # Modelo de tarefa (ID, status, histórico)
├── agents/
│   ├── base.py              # BaseAgent — loop Claude + tool_use
│   ├── discovery.py         # Agente de Descoberta/Requisitos
│   ├── prioritization.py    # Agente de Priorização
│   ├── architecture.py      # Agente de Arquitetura
│   ├── planning.py          # Agente de Planejamento Técnico
│   ├── devils_advocate.py   # Advogado do Diabo
│   ├── implementer.py       # Agente Implementador
│   ├── testing.py           # Agente de Testes
│   ├── reviewer.py          # Agente Revisor
│   ├── security.py          # Agente de Segurança/Compliance
│   ├── documentation.py     # Agente de Documentação
│   └── observability.py     # Agente de Observabilidade
├── tools/
│   ├── github_tools.py      # Ler/escrever código, criar branches/PRs
│   ├── code_tools.py        # Rodar testes, linter, análise estática
│   └── fs_tools.py          # Ler/escrever arquivos locais
├── interfaces/
│   ├── web/
│   │   ├── app.py           # FastAPI — rotas do painel
│   │   └── templates/       # HTML do painel de aprovação
│   ├── telegram_bot.py      # Bot Telegram — notificações + aprovações
│   └── cli.py               # Entry point CLI
├── storage/
│   ├── database.py          # Conexão e queries SQLite/PostgreSQL
│   └── models.py            # ORM models (Task, AgentRun, ApprovalRequest)
├── config.py                # Configuração via variáveis de ambiente
├── main.py                  # Entry point principal
└── tests/
    ├── unit/                # Testes unitários por agente
    ├── integration/         # Testes de integração entre agentes
    └── fixtures/            # Dados de teste reutilizáveis
```

---

## 4. Componentes Principais

### 4.1 BaseAgent (`agents/base.py`)

Classe base que todos os agentes herdam. Implementa o loop Claude com `tool_use` e prompt caching.

```python
class BaseAgent:
    model: str = "claude-opus-4-6"        # agentes críticos
    # ou "claude-haiku-4-5-20251001"      # agentes mecânicos
    
    async def run(self, context: TaskContext) -> AgentResult:
        # 1. Monta system prompt com cache_control
        # 2. Loop: chama Claude → processa tool_use → repete até text final
        # 3. Retorna AgentResult(output, confidence, concerns)
```

**Prompt caching:** o system prompt de cada agente é marcado com `cache_control: {"type": "ephemeral"}` — reduz custo em ~80% em chamadas repetidas.

### 4.2 TaskContext (`core/context.py`)

Objeto central persistido em banco a cada atualização.

```python
@dataclass
class TaskContext:
    task_id: str                    # "monarch-042"
    status: TaskStatus              # enum: PENDING, RUNNING, AWAITING_APPROVAL, DONE, FAILED
    raw_input: str                  # "Criar endpoint /users/{id}"
    requirements: dict | None       # output do Agente de Descoberta
    priority: str | None            # "MVP_V1" | "BACKLOG_V2" | "DISCARDED"
    architecture: dict | None       # output do Agente de Arquitetura
    plan: list[dict] | None         # passos do Agente de Planejamento
    devils_advocate_rounds: list    # objeções por rodada
    branch_name: str | None         # "feat/monarch-042-users-endpoint"
    pr_url: str | None              # URL do PR no GitHub
    test_results: dict | None       # pass/fail, cobertura
    review_report: dict | None      # qualidade + segurança
    history: list[HistoryEntry]     # log completo de cada ação
    created_at: datetime
    updated_at: datetime
```

### 4.3 Orquestrador (`core/orchestrator.py`)

Gerencia o fluxo completo. Não contém lógica de domínio — apenas decisões de fluxo.

**Responsabilidades:**
- Receber tarefa → criar `TaskContext` com ID único
- Invocar agentes em sequência
- Detectar falhas e aplicar estratégia de retry/escalonamento
- Pausar fluxo e solicitar aprovação humana em pontos críticos
- Persistir contexto após cada etapa
- Notificar interfaces (Web + Telegram) sobre mudanças de estado

**Não faz:**
- Escrever código
- Tomar decisões de conteúdo
- Interagir diretamente com GitHub

### 4.4 Agentes Especializados

| Agente | Modelo | Input | Output |
|---|---|---|---|
| Descoberta | Opus | raw_input + docs | requirements (User Stories + critérios de aceite) |
| Priorização | Haiku | requirements | priority + justificativa |
| Arquitetura | Opus | requirements | proposta técnica (componentes, tecnologias, APIs) |
| Planejamento | Sonnet | arquitetura | plano de execução (passos ordenados) |
| Advogado do Diabo | Opus | tudo acima | lista de objeções + riscos + perguntas |
| Implementador | Opus | plano + contexto do repo | código no branch + commit |
| Testes | Sonnet | código + requisitos | testes gerados + resultado de execução |
| Revisor | Sonnet | código + testes | relatório de qualidade |
| Segurança | Opus | código + config | relatório de vulnerabilidades |
| Documentação | Haiku | contexto completo | README/docstrings atualizados |
| Observabilidade | Haiku | código final | código instrumentado com logs/métricas |

### 4.5 Tools (Ferramentas dos Agentes)

**`github_tools.py`** — ferramentas que os agentes chamam via `tool_use`:
- `read_file(path, branch)` — lê arquivo do repo
- `list_files(path, branch)` — lista arquivos
- `write_file(path, content, branch, commit_message)` — escreve arquivo
- `create_branch(name, from_branch)` — cria branch
- `create_pr(title, body, head, base)` — abre PR como draft
- `get_pr_diff(pr_number)` — obtém diff do PR
- `run_ci_check(pr_number)` — verifica status do CI

**`code_tools.py`**:
- `run_tests(path, filter)` — executa pytest, retorna pass/fail + cobertura
- `run_linter(path)` — executa ruff
- `run_type_check(path)` — executa mypy
- `run_security_scan(path)` — executa bandit (SAST Python)

---

## 5. Fluxo de Dados

```
Entrada (Claude Code ou Telegram)
      │
      ▼
Orquestrador cria TaskContext (status: PENDING)
      │
      ├─► Agente de Descoberta    → requirements
      ├─► Agente de Priorização   → priority
      │      └── se DISCARDED: encerra, notifica
      │
      ├─► Agente de Arquitetura   → architecture
      ├─► Agente de Planejamento  → plan
      ├─► Advogado do Diabo (1ª)  → objeções
      │      └── se crítico: volta para Arquitetura/Planejamento (máx 2x)
      │
      │   [APROVAÇÃO HUMANA — Arquitetura]
      │
      ├─► Agente Implementador    → branch + código
      ├─► Agente de Testes        → testes + execução
      │      └── se falhou: volta para Implementador (máx 3x)
      │
      ├─► Agente Revisor          → relatório de qualidade
      ├─► Agente de Segurança     → relatório de segurança
      │      └── se crítico: PARA, escala humano imediatamente
      ├─► Advogado do Diabo (2ª)  → revisão final
      │
      │   [APROVAÇÃO HUMANA — PR Final]
      │
      ├─► Agente de Documentação  → docs atualizados
      └─► Agente de Observabilidade → logs/métricas
            │
            ▼
      PR aberto no GitHub (draft → ready for review)
      Notificação via Telegram + Web UI
```

---

## 6. Tratamento de Erros

| Tipo de Falha | Reação Automática | Limite | Escalação |
|---|---|---|---|
| LLM timeout / rate limit | Retry com backoff exponencial (2s→4s→8s) | 3x | Notifica humano |
| Agente retorna output inválido | Retry com prompt ajustado | 3x | Notifica humano |
| Testes falhando | Volta para Implementador com feedback | 3x | Notifica humano |
| Segurança crítica detectada | Para imediatamente, sem retry | — | Sempre humano |
| Ambiguidade alta (confidence < 70%) | Pausa e pergunta ao humano | — | Sempre humano |
| GitHub API indisponível | Retry exponencial | 5x | Pausa tarefa |
| Advogado levanta risco crítico | Volta para Arquitetura/Planejamento | 2x | Notifica humano |
| Circuit breaker ativo | Desabilita agente por 10min | 5 falhas/10min | Notifica imediatamente |

**Rollback:** Implementador sempre trabalha em branch isolada. Falha = branch deletada. `main` nunca é afetado sem aprovação humana explícita.

---

## 7. Interfaces

### Web UI (`http://localhost:8000`)

Três seções:
1. **Nova Tarefa** — campo de texto + botão Enviar
2. **Em Andamento** — lista de tarefas ativas com status em tempo real (WebSocket)
3. **Histórico** — tarefas concluídas e falhas com link para PR

Cada ponto de aprovação abre modal com:
- Proposta do agente (formatada)
- Objeções do Advogado do Diabo
- Botões: **Aprovar** / **Rejeitar + motivo** / **Pedir Revisão**

### Telegram Bot

**Notificações automáticas:**
- Tarefa iniciada
- Cada etapa concluída
- Aprovação necessária (com botões inline)
- CI verde/vermelho
- Tarefa concluída + link do PR

**Comandos:**
```
/status          lista tarefas ativas
/task <id>       detalhes completos
/approve <id>    aprovar etapa atual
/reject <id>     rejeitar com feedback
/pause           pausar todas as tarefas
/resume          retomar
```

---

## 8. Requisitos Não-Funcionais

| Requisito | Meta |
|---|---|
| Uptime | 99.9% |
| Latência por agente | < 60s (com timeout) |
| Tarefas concorrentes | Até 5 simultâneas no MVP |
| Persistência | Contexto salvo após cada etapa (nunca perde progresso) |
| Segurança | Princípio do menor privilégio, segredos via env vars, sem secrets em logs |
| Rastreabilidade | Cada ação logada com timestamp, task_id, agent_id |

---

## 9. Configuração (`.env`)

```env
# Anthropic
ANTHROPIC_API_KEY=sk-...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Web UI
WEB_PORT=8000
WEB_SECRET_KEY=...

# Banco de dados
DATABASE_URL=sqlite:///./monarch_ai.db

# Comportamento
MAX_AGENT_RETRIES=3
APPROVAL_TIMEOUT_MINUTES=60
CONFIDENCE_THRESHOLD=0.70
```

---

## 10. Fases de Implementação

### Fase 1 — Core (Semanas 1-2)
`TaskContext`, `BaseAgent`, `Orchestrator`, persistência SQLite, testes unitários dos componentes core.

### Fase 2 — Agentes Core (Semanas 3-5)
Descoberta, Priorização, Arquitetura, Planejamento, Advogado do Diabo — com todos os tools GitHub.

### Fase 3 — Execução (Semanas 6-8)
Implementador, Testes, Revisor, Segurança — fluxo completo end-to-end funcionando.

### Fase 4 — Interfaces (Semanas 9-10)
Web UI (FastAPI), Telegram Bot, pontos de aprovação humana integrados.

### Fase 5 — Suporte + Polimento (Semanas 11-12)
Documentação, Observabilidade, circuit breaker, testes end-to-end, ajustes de prompts.
