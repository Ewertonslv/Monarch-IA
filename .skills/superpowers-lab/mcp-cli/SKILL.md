---
name: mcp-cli
description: "Query MCP servers on-demand via CLI without pre-loading them into context. Use when you need to access an MCP tool temporarily without permanently integrating it."
---

# MCP CLI — On-Demand MCP Server Usage

Access MCP server capabilities without permanent integration or context window overhead.

## Installation

```bash
cd /tmp && git clone --depth 1 https://github.com/f/mcptools.git
cd mcptools && CGO_ENABLED=0 go build -o ~/.local/bin/mcp ./cmd/mcptools
```

## Discovery & Usage Pattern

1. Identify tools: `mcp tools <server-command>`
2. Check resources: `mcp resources <server-command>`
3. Invoke: `mcp call <tool_name> --params '<json>' <server-command>`

## Example

```bash
mcp call read_file --params '{"path": "/tmp/example.txt"}' \
  npx -y @modelcontextprotocol/server-filesystem /tmp
```

## Session Aliases (for repeated use)

```bash
mcp alias add fs npx -y @modelcontextprotocol/server-filesystem /home/user
mcp call read_file --params '{"path": "README.md"}' fs
mcp alias remove fs
```

## When to Use for Monarch AI

- Testing new MCP integrations before wiring them into agents
- Accessing GitHub MCP server temporarily during development
- Debugging tool connectivity issues
