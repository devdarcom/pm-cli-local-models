# ADR-002: Unified tool output contract

## Status
Accepted

## Context
Graph/tool interoperability and test stability require consistent tool outputs,
especially on failure paths.

## Decision
All file tools return:

```python
{"ok": bool, "data": Any, "error": str | None}
```

Tools should return descriptive errors as data, not raise uncaught exceptions.

## Consequences
- Router and model can process tool results consistently.
- Integration tests can assert one predictable shape.
- New tools must follow the same contract from day one.
