# ADR-006: Context loading and prompt boundary

## Status
Accepted

## Context
The agent needs project/runtime context in model prompts, but developer/process
documents should not be injected into model instructions.

## Decision
- Always load required system prompt file before model execution.
- Optionally load `PROJECT.md` as project context.
- Do not inject `AGENTS.md` into model prompt; treat it as developer guidance
  only.
- Ensure system message presence is checked to avoid duplicate context
  injection per graph invocation.

## Consequences
- Prompt construction is explicit and controlled.
- Developer rules remain out of runtime model instruction payload.
- Repeated invokes avoid context duplication side effects.
