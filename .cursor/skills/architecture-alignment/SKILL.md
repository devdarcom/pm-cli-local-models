---
name: architecture-alignment
description: Build minimal architecture context before scenario implementation. Use before code-spec to identify touched modules, relevant ADRs, contract constraints, and architecture red flags for the current task.
disable-model-invocation: true
---
# Architecture Alignment Skill

## Goal
Before implementation, build a small architecture context for the current task.
Keep context focused and actionable for coding.

## Input
- `scenario_id` (for example: `T-13`, `B-01`)
- scenario description from `scenarios.md`
- `architecture/CURRENT_STATE.md` (always)
- `architecture/CHANGE_LOG.md` (always)

## Workflow
1. Identify affected modules (maximum 3).
2. Load `architecture/modules/<module>/INTERFACE.md` only for affected modules.
3. Load relevant ADR files from `architecture/decisions/`.
4. Validate if the task:
   - changes a public contract,
   - requires a new module,
   - conflicts with ADR decisions.
5. Produce `TASK_CONTEXT.md` (task-specific summary) using:
   - @references/TASK_CONTEXT_OUTPUT.md

## Default Scope
Do not read implementation code by default.
Use contracts and decisions first.

## Fallback
If docs are insufficient or contradictory:
- mark `confidence` as `low`,
- read up to 2 implementation files,
- record these files in `Assumptions & Gaps`.

## Output: TASK_CONTEXT.md
Load output structure from:
- @references/TASK_CONTEXT_OUTPUT.md

## Quality Rules
- Keep output under 600 words.
- Include only context relevant for the task.
- If data is missing, state it explicitly. Do not guess.
