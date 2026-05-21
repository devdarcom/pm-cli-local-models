---
name: code-spec
description: Implement a scenario from scenarios.md using TDD, then run code-review automatically. Use this skill whenever the user provides a scenario ID (like S-01, T-04, G-07, K-01, etc.) and wants it implemented. Trigger on phrases like "zakoduj scenariusz", "zaimplementuj S-02", "zacznij kodować T-03", "lecimy z S-02", "rób następny scenariusz", "kolejny scenariusz", or any message that contains a scenario ID from scenarios.md. Also trigger when the user just says "tak" or "lecimy" immediately after a scenario was mentioned. Always check scenarios.md first — never start coding a scenario that is already marked as done.
---

# Code Spec Skill

You are a **coding agent** implementing scenarios one at a time using TDD.
You write tests before implementation, keep code minimal, follow AGENTS.md strictly,
and hand off to the code-review skill automatically after each implementation.

## Step 0 — Check scenario status

Read `scenarios.md`. Find the row with the given scenario ID.

- If status is `done` → stop and inform the user: "Scenariusz <ID> jest już zaimplementowany (done). Podaj kolejny ID."
- If status is `todo` → proceed to Step 1.

If no scenario ID was given, ask the user for one before proceeding.

## Step 1 — Read context

Read these files before writing any code:

1. `opis-projektu.md` — understand the architecture and which module this scenario belongs to
2. `AGENTS.md` — your coding rulebook; follow all 10 rules without exception
3. `scenarios.md` — find the scenario row; note type (UNIT/INT) and description

From the scenario description, understand:
- What function/class must exist
- What behaviour it must exhibit
- Which module it belongs to (based on `opis-projektu.md` structure)

## Step 2 — Create branch

```bash
git checkout main
git pull origin main
git checkout -b scenario/<SCENARIO_ID>
```

Example: `git checkout -b scenario/S-02`

## Step 3 — Write the test FIRST

This is TDD. The test comes before the implementation.

**Test location rules:**
- `UNIT` scenario → `tests/unit/test_<module>.py`
- `INT` scenario → `tests/integration/test_<module>.py`

**Test naming:** The function name must describe the scenario behaviour clearly.
Good: `test_create_session_raises_value_error_for_unknown_model`
Bad: `test_s02` or `test_session_error`

**Test must be non-trivial:** It must fail if the implementation is missing or wrong.
Do not write assertions that always pass.

After writing the test, run it to confirm it **fails**:
```bash
.venv/bin/pytest <test_file> -v
```

If the test passes before implementation — it's a trivial test. Rewrite it.

## Step 4 — Write minimal implementation

Write the smallest amount of code that makes the test pass.
No gold-plating, no extra features, no "while I'm at it" additions.

Follow all 10 rules from AGENTS.md:
1. Meaningful names — no `d`, `r`, `tmp`, `data`
2. Single responsibility — one function, one job
3. No magic numbers/strings — use named constants
4. Specific error handling — no bare `except:`
5. Type hints on all public functions
6. DRY — no duplicated logic
7. Small functions — max ~20 lines
8. Comments explain why, not what
9. Use `@dataclass` or `TypedDict` for structured data
10. Every function affecting agent state must have a test

After writing the implementation, run the test to confirm it **passes**:
```bash
.venv/bin/pytest <test_file> -v
```

If it fails — fix the implementation. Do not move to Step 5 until the test passes.

## Step 5 — Commit and create PR

```bash
git add <implementation_file> <test_file>
git commit -m "feat(<module>): <description> — <SCENARIO_ID>"
git push origin scenario/<SCENARIO_ID>
```

Then create the PR:
```bash
gh pr create \
  --title "feat(<module>): <SCENARIO_ID> — <short scenario description>" \
  --body "## Scenariusz
**ID:** <ID>
**Typ:** UNIT / INT
**Opis:** <description from scenarios.md>

## Zmiany
- \`<implementation file>\` — <what was implemented>
- \`<test file>\` — test jednostkowy / integracyjny

## Test
\`\`\`
pytest <test_file> -v
# X passed
\`\`\`" \
  --base main
```

Note the PR number from the output.

## Step 6 — Invoke code-review

Now hand off to the code-review skill. Pass:
- Scenario ID
- PR number
- Attempt: 1

The code-review skill will produce a PASS or FAIL verdict.

### If PASS:
```bash
gh pr merge <PR_NUMBER> --squash --delete-branch
git checkout main
git pull origin main
```

Then update `scenarios.md`: change the scenario's status from `todo` to `done`.
Update the module's `Done` count and the `Łącznie` row in the summary table.

Commit the update:
```bash
git add scenarios.md
git commit -m "chore: mark <SCENARIO_ID> as done in scenarios.md"
git push origin main
```

Inform the user: "✅ Scenariusz <ID> zakończony i zmergowany. Łącznie done: X/84."

### If FAIL (Attempt 1):
Fix every blocker listed in the code-review report.
Run the test again to confirm it still passes after fixes:
```bash
.venv/bin/pytest <test_file> -v
```

Commit the fixes:
```bash
git add .
git commit -m "fix(<module>): address code-review blockers — <SCENARIO_ID>"
git push origin scenario/<SCENARIO_ID>
```

Invoke code-review again with Attempt: 2.

### If FAIL (Attempt 2):
Stop. Do not attempt further fixes.
Present the unresolved blockers to the user and wait for their decision.

## Rules for this skill

- Never skip the failing-test verification in Step 3. If you can't confirm the test fails, write in your response: "⚠️ Nie mogłem uruchomić testu — upewnij się że .venv jest aktywne."
- Never add code that isn't required by the scenario. Minimal is correct.
- Never merge without a PASS from code-review.
- Always update `scenarios.md` after a successful merge.
- Work on one scenario at a time. Do not start the next scenario until the current one is merged.
