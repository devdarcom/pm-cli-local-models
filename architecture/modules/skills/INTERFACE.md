# Skills Module Interface

## Scope
`app/skills/*` (planned)

## Public Contracts (target)

- `load_skill(name)` reads skill metadata/content.
- `list_skills()` returns available skill names.
- Skill config may define model override for task execution.

## Invariants

- Missing skill file is handled explicitly (`None` or structured error).
- Skill-level model override must not silently break base session behavior.

## Change Rules

- Any skill metadata schema change requires tests for:
  - explicit model in skill,
  - default model fallback,
  - missing skill file path.
