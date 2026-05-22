# ADR-001: Agent state boundary and validation

## Status
Accepted

## Context
Agent flow needs a strict runtime state contract to avoid silent shape drift
between graph nodes.

## Decision
Use Pydantic `BaseModel` for `AgentState` with `extra="forbid"` and explicit
fields for retries, errors, recursion, summary, and messages reducer behavior.

## Consequences
- Unknown fields fail fast at state construction.
- Node interfaces remain explicit and reviewable.
- Future scenarios must update state schema deliberately, not implicitly.
