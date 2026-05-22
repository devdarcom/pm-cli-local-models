# ADR-009: Skill orchestration via subagents

## Status
Accepted

## Context
Nested skill execution in parent flow can blur responsibility boundaries and
make orchestration hard to trace.

## Decision
- Parent workflow skills orchestrate specialized work by spawning subagents.
- For architecture alignment in code-spec flow:
  - parent skill delegates alignment to a dedicated subagent,
  - subagent uses `architecture-alignment` skill,
  - parent consumes structured alignment outcome (`confidence`, `red flags`,
    implementation constraints).

## Consequences
- Clear separation between orchestration and specialized analysis.
- Easier traceability of who produced alignment context.
- Better control over hard-gate behavior before coding.
