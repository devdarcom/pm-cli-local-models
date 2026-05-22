# Current State

Multimodel PM is a Python CLI agent project based on LangGraph and Ollama.
The current implementation covers core execution flow, file tools, error
handling, recursion limits, and initial context compression routing.

## What Works Now

- Agent graph loads system and project context before model execution.
- Runtime state is validated by Pydantic (`extra="forbid"`), including
  recursion and retry metadata.
- File tools are implemented with a unified output contract:
  `{"ok": bool, "data": ..., "error": ...}`.
- Graph handles:
  - tool calling loop,
  - retry/escalation path for model errors,
  - compression routing and continuation after compression.
- CLI chat loop persists conversation messages between turns.

## Compression Status

- Compression model is dedicated (`gemma3:4b`) and decoupled from session
  model.
- Router can direct flow to compression on threshold.
- Compression summary is injected back and flow continues to user response.
- Full hot/cold strategy from PRD is only partially implemented.

## Tests Coverage Snapshot

- Strong coverage in:
  - `app/agent/state.py`,
  - `app/agent/tools.py`,
  - `app/agent/graph.py` and core nodes.
- Unit and integration graph tests are stable and actively maintained.
- E2E layer is defined in scenarios but not implemented yet.

## Main Gaps (High Priority)

- Missing TUI/backslash command parser.
- Model switching flow is still todo.
- Skill loading subsystem is still todo.
- MCP client lifecycle per agent is still todo.
- Multi-agent manager and spawn flow are still todo.
- Destructive action confirmation flow is still todo.
- At-mention UX and file attachment flow are still todo.

## Operating Principle

Development is scenario-driven (TDD + PR + code review loop). Every scenario
should keep architecture boundaries explicit and avoid adding broad context to
coding agents when a task-specific context is enough.
