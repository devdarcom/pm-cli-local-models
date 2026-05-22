# ADR-007: Queue delegation to Ollama and local queue deprecation

## Status
Accepted

## Context
A local application queue layer was considered, but Ollama already provides
built-in request queueing behavior configured by environment variables.

## Decision
- Delegate request queueing to Ollama runtime configuration.
- Keep `app/queue/` out of active architecture (deprecated path).
- Treat queue module artifacts as non-operational until explicitly reintroduced
  by a new ADR.

## Consequences
- Avoid duplicate queue orchestration logic in application code.
- Reduce maintenance surface for concurrency management.
- Any future app-level prioritization/backpressure must be introduced as a
  deliberate architectural change.
