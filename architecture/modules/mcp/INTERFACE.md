# MCP Module Interface

## Scope
`app/mcp/*` (planned)

## Public Contracts (target)

- MCP connection is represented by client instance bound to an agent context.
- `connect(url)` stores endpoint configuration for active agent.

## Invariants

- MCP client lifecycle is agent-scoped, not global-scoped.
- Multiple agents cannot share mutable MCP state by default.

## Change Rules

- Any MCP lifecycle change requires tests for:
  - per-agent isolation,
  - connect path,
  - multi-agent independence.
