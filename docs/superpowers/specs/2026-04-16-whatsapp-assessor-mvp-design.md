# WhatsApp Assessor MVP - Design

Data: 2026-04-16

## Objetivo

Transformar o `whatsapp-notion-bot` em um assessor pessoal via WhatsApp, similar ao MeuAssessor, com registro de gastos, receitas, compromissos, consultas em linguagem natural e painel de acompanhamento.

## Arquitetura

```
webhook → intent classifier → handlers → resposta
                          ↓
                    SQLite (substitui Notion)
                          ↓
                    painel (endpoints)
```

## Componentes

### 1. IntentClassifier

Substitui o `ExpenseClassifier` atual. Detecta 6 intents:
- `expense` - gastos financeiros
- `income` - receitas
- `commitment` - compromissos e afazeres
- `query` - perguntas sobre saldo, totais, compromissos
- `reminder` - configuração de lembretes
- `support` - solicitar suporte humano

### 2. Handlers

| Handler | Input | Output |
|---------|-------|--------|
| `ExpenseHandler` | "gastei 45 no mercado" | Registra gasto + confirmação |
| `IncomeHandler` | "recebi 2000 de salário" | Registra receita + confirmação |
| `CommitmentHandler` | "reunião amanhã 14h" | Registra compromisso + confirmação |
| `QueryHandler` | "quanto gastei hoje?" | Responde com totais/período |
| `SupportHandler` | "quero falar com suporte" | Transfere para atendente |

### 3. Persistence

SQLite local (substitui Notion para performance e scale):
- `users` - cadastro de usuários com email/senha
- `transactions` - gastos e receitas
- `commitments` - compromissos e afazeres
- `recurring` - transações recorrentes

### 4. Painel

Endpoints FastAPI:
- `GET /panel/transactions` - lista transações
- `GET /panel/commitments` - lista compromissos  
- `GET /panel/summary` - totais por período
- `POST /panel/login` - autenticação

## Fluxo

1. Mensagem entra no webhook
2. IntentClassifier classifica a intent
3. Handler apropriado processa → salva no SQLite
4. Resposta adequada enviada pelo WhatsApp

## Escopo MVP

**Fase 1** (este PR):
- Intent classifier com 6 intents
- Handlers: expense, income, commitment, query
- SQLite para persistência
- Respostas em linguagem natural

**Fase 2** (próximo PR):
- Onboarding (email/senha via WhatsApp)
- Lembretes ativos
- Painel web

**Fase 3**:
- Conta compartilhada
- Google Calendar
- Transações recorrentes
- Monetização

## Stack

- FastAPI (já existe)
- SQLite via SQLAlchemy (substitui Notion)
- Anthropic SDK (já existe)
- Z-API (já existe)

## Referências

- https://www.meuassessor.com/
- docs/whatsapp-assessor-product.md