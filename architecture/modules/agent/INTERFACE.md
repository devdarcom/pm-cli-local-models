# Agent Module Interface

## Scope
`app/agent/graph.py`, `app/agent/nodes.py`, `app/agent/state.py`

## Public Contracts

- `AgentState` is the canonical graph state shape.
- `build_graph()` returns a compiled LangGraph state graph.
- `route_after_model(state)` returns one of known route symbols:
  `tool_node`, `done`, `error_handler`, `escalate_to_user`, `compress`.

## Invariants

- Unknown state fields are forbidden.
- Model errors route through retry/escalation path.
- Compression branch must re-enter main model path before completion.

## Change Rules

- Any new route symbol requires:
  - update to router type hints,
  - update to conditional edges mapping,
  - unit test for router branch.
- Any change in state fields requires matching tests in state/router/node layers.
