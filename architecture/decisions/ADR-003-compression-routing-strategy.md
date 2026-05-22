# ADR-003: Compression as explicit graph branch

## Status
Accepted

## Context
Context growth must be handled without breaking primary user response flow.

## Decision
Compression is a dedicated graph node/branch:
- router can choose `compress`,
- compression runs with a dedicated lightweight model,
- flow returns to `call_model` and continues to normal completion.

## Consequences
- Compression behavior is testable as routing logic.
- User response continuity is preserved after compression.
- Threshold policy can evolve without changing core tool/error branches.
