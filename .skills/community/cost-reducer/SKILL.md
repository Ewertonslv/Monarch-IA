# Cost Reducer

Reduz o consumo de tokens em toda sessao. Estas regras se aplicam AUTOMATICAMENTE
em todas as tarefas — nao precisa invocar esta skill explicitamente.

---

## Smart Model Dispatch — SEMPRE APLICAR

Roteie para o modelo mais barato que resolve a tarefa:

### Opus — $$$

- Arquitetura de novos agentes
- Planejamento de pipeline multi-agente
- Decisoes de design criticas
- Bugs complexos que precisam de reasoning profundo

### Sonnet — $$

- Implementar agentes novos
- Modificar o orchestrator
- Integracoes com APIs externas
- Features com multiplos arquivos

### Haiku — $ (mecanico, nao raciocina)

- Gerar tests unitarios
- Criar README / boilerplate
- Corrigir lint e formatacao
- Templates HTML/CSS/CLI
- Arquivos de config simples
- Migrar ou refatorar codigo ja existente
- Operacoes em batch (mudar nome de 10 arquivos, etc.)

### ZERO API — CLI natural

Tudo em `apps/*/cli.py` executa LOCAL sem API:
- `python -m interfaces.cli "shortlist de achadinhos"`
- `python -m interfaces.cli "experimento solo leveling sobre X"`
- Qualquer comando CLI dos apps implementados

---

## Contexto Automatico — Sempre < 150 linhas

| Arquivo | Carrega sempre? |
|---|---|
| `CLAUDE.md` (raiz) | Sim |
| `.claude/CLAUDE.md` | Sim |
| Skills | So quando invocadas |

### O que evitar no contexto

- **Duplicacao** — a mesma info em README + CLAUDE.md = redundante
- **Historico de sessoes** — lugar errado, vai pro checkpoint.md
- **Listas de arquivos** — use globs (`apps/*/`)
- **Exemplos de codigo** — comentario no arquivo real

---

## Auditoria de Contexto

```bash
# Contar linhas
(Get-Content CLAUDE.md).Count
(Get-Content .claude/CLAUDE.md).Count

# Meta: < 150 linhas total
```

Se passou de 150, audite duplicacoes.

---

## Regra #1: CLI Natural antes de API

Antes de gastar API, verifique se a tarefa pode ser feita com:

```bash
python -m interfaces.cli "tarefa"     # CLI natural
python -m apps.<nome_do_app> <cmd>   # App especifico
```

---

## Regra #2: Haiku para o trabalho mecanico

Se a tarefa e "gerar X", "criar Y", "adicionar Z" em um padrao
repetitivo — e Haiku. Nao desperdice Sonnet.

## Regra #3: Tasks paralelas = Sonnet

Se a tarefa pode ser dividida em 2+ partes independentes,
rodo em paralelo (Task tool). Custo total < soma sequencial.
