# ADR-004: Error recovery and escalation policy

## Status
Accepted

## Context
The agent must handle model failures predictably and avoid infinite loops while
still attempting recovery.

## Decision
- Use explicit state tags for failure handling:
  - `error_type`,
  - `error_node`,
  - `last_error`,
  - `retry_count`.
- Retry model failures with bounded attempts (`MAX_MODEL_RETRIES`).
- Escalate to user when retries are exhausted.
- Enforce hard recursion limit (`RECURSION_LIMIT`) and stop model calls when
  reached.

## Consequences
- Failure paths are deterministic and testable.
- User gets explicit escalation instead of silent failure.
- Loop risk is bounded by retry and recursion guards.
