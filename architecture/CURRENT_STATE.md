# Current State

Multimodel PM is a Python CLI agent project based on LangGraph and Ollama.
The current implementation covers core execution flow, file tools, error
handling, recursion limits, and initial context compression routing.

## What Works Now

- Agent graph loads system and project context before model execution.
- Prompt boundary is explicit: `AGENTS.md` is not injected into model context.
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
- Re-compression is currently constrained after summary state is set.
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
- Skill orchestration keeps responsibilities split: parent workflow orchestrates,
  specialized analysis can run in a spawned subagent.

## Architecture Decisions Snapshot

- ADR-001: Agent state boundary and validation.
- ADR-002: Unified tool output contract.
- ADR-003: Compression as explicit graph branch.
- ADR-004: Error recovery and escalation policy.
- ADR-005: Model selection and capability policy.
- ADR-006: Context loading and prompt boundary.
- ADR-007: Queue delegation to Ollama (local queue deprecated).
- ADR-008: Compression trigger and lifecycle policy.
- ADR-009: Skill orchestration via subagents.
