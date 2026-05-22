# TUI Module Interface

## Scope
`app/tui/*` (planned)

## Public Contracts (target)

- Command parsing for backslash commands:
  - `\new`, `\reset`, `\compress`, `\model`, `\spawn`,
  - `\mcp`, `\skills`, `\stop`, `\help`.
- At-mention support for project files (`@file` flow).

## Invariants

- Invalid command args return explicit, user-readable errors.
- At-mention suggestions must respect exclusion rules (`.git`, `.venv`,
  `__pycache__`, ignored paths).

## Change Rules

- New command contracts require parser tests first.
- At-mention behavior changes require both unit and integration coverage.
