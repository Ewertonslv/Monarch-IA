---
name: using-tmux-for-interactive-commands
description: "Control interactive CLI tools (vim, git rebase -i, REPLs, pytest watch) through tmux sessions. Use when a command requires a real terminal and can't be piped via stdin."
---

# Using tmux for Interactive Commands

Interactive CLI tools need a real terminal — use tmux `send-keys` + `capture-pane` to control them programmatically.

## When to Use

**Use tmux for:**
- Text editors run programmatically (vim, nano)
- Interactive REPLs (Python, Node)
- `git rebase -i`
- Full-screen terminal apps
- pytest in watch mode

**Don't use tmux for:**
- Simple non-interactive commands
- Commands accepting stdin redirection

## Core Pattern

```bash
# Create detached session
tmux new-session -d -s monarch_session <command>

# Wait for init
sleep 0.5

# Send input
tmux send-keys -t monarch_session 'input here' Enter

# Capture output
tmux capture-pane -t monarch_session -p

# Cleanup
tmux kill-session -t monarch_session
```

## Special Keys

Use tmux key names: `Enter`, `Escape`, `C-c`, arrow keys — NOT escape sequences.

## Common Mistakes

- Not waiting after session creation
- Forgetting to send `Enter` as separate argument
- Not cleaning up orphaned sessions

## When to Use for Monarch AI

- Agente de Testes rodando pytest em modo watch
- Agente Implementador fazendo git rebase interativo
- Debugging em REPL Python durante desenvolvimento dos agentes
