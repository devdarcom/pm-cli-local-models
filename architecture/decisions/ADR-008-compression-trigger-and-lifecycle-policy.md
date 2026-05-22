# ADR-008: Compression trigger and lifecycle policy

## Status
Accepted

## Context
Conversation growth must be constrained without breaking the main response
loop. Compression currently exists as graph branch with threshold routing.

## Decision
- Use graph router threshold check (`COMPRESSION_MESSAGE_THRESHOLD`) to route to
  compression branch.
- Compression branch returns to `call_model` for continued user-facing response.
- Compression output includes summary message tagged with
  `COMPRESSED_CONTEXT_PREFIX` and updates `summary` state field.
- Current policy guards repeated compression by `summary is not None`.

## Consequences
- Compression activation is explicit in routing logic.
- Post-compression response continuity is preserved.
- Re-compression behavior is intentionally constrained until future policy
  refinement.
