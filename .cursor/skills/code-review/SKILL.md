---
name: code-review
description: Review Python code for a specific scenario after it's been coded and a PR created. Use this skill whenever a scenario from scenarios.md has been implemented and a PR exists that needs review before merging. Trigger when the user or coding agent says things like "zrób code review", "review PR", "sprawdź kod dla scenariusza", "zakończyłem scenariusz", "czy mogę zmergować", or when a PR number and scenario ID are both present. Always block the merge if any AGENTS.md rule is violated or the test is missing/failing. This skill is intentionally run as a fresh agent with no knowledge of the coding agent's reasoning — this is by design.
---

# Code Review Skill

You are a **fresh-eyes code reviewer**. You have no knowledge of decisions made by the coding agent.
Your job is to objectively verify that the code meets the project's standards and that the scenario
has been correctly implemented. You are the last gate before merge.

## What you need to run

You need three pieces of information:
1. **Scenario ID** — e.g. `S-01`, `T-04`, `G-07` (from `scenarios.md`)
2. **PR number** — e.g. `#12`
3. **Attempt number** — `1` or `2` (default: `1` if not provided)

If scenario ID or PR number is missing, ask for it before proceeding.
Attempt number is provided automatically by the retry loop — assume `1` if not stated.

## Step 1 — Load context

Read these files in order. They give you full architectural awareness:

1. Read `opis-projektu.md` — system architecture, tech stack, module structure
2. Read `AGENTS.md` — clean code rules with good/bad Python examples (your checklist)
3. Read `scenarios.md` — find the specific scenario by ID, note its type (UNIT/INT) and description

Look up the scenario row. Note:
- The scenario description (what behaviour is expected)
- The type: `UNIT` or `INT`

## Step 2 — Get the PR diff

Run:
```bash
gh pr diff <PR_NUMBER>
```

Also get PR metadata:
```bash
gh pr view <PR_NUMBER>
```

Read the full diff carefully. Identify:
- Which files were added or modified
- Where the test lives
- Where the implementation lives

## Step 3 — Check the test

Answer these questions:

**a) Does a test exist?**
There must be at least one test that directly maps to the scenario description.
- `UNIT` scenarios → test in `tests/unit/`
- `INT` scenarios → test in `tests/integration/`

**b) Does the test name match the scenario?**
The test function name should make the scenario's intent obvious.

**c) Does the test actually fail before the implementation and pass after?**
You can't run it live, but you can reason about it from the diff:
- If the test and implementation were added in the same commit, verify the test would fail
  on an empty implementation (i.e. it's not trivially always-passing)
- A test that always passes regardless of the implementation is not a real test

## Step 3b — Check architecture compliance

Verify that the changed files respect the module boundaries defined in `opis-projektu.md`.

Answer these questions for every file in the diff:

**a) Is the file in the correct module?**
Cross-check the file path against the directory structure from `opis-projektu.md`:
- `app/agent/tools.py` — only file I/O tools (read, write, list, delete, search). No graph logic, no LangGraph imports.
- `app/agent/nodes.py` — LangGraph node functions and `AGENT_TOOLS` list. No direct Textual/TUI imports.
- `app/agent/graph.py` — graph topology only (`StateGraph`, edges, `build_graph()`). No business logic.
- `app/agent/state.py` — `AgentState` Pydantic model only. No node logic, no tools.
- `app/session/` — session creation, reset, model management. No LangGraph graph imports.
- `app/tui/` — Textual UI, at-mention helpers. No direct `ChatOllama` calls.
- `app/skills/` — skill loading utilities. No graph construction.
- `app/mcp/` — MCP client only. No session or graph logic.

**b) Do imports respect the dependency hierarchy?**
Allowed import direction (top → bottom, never reverse):
```
graph.py → nodes.py → tools.py
graph.py → state.py
nodes.py → state.py
tui/ → session/
tui/ → agent/graph.py (invoke only)
```
A **reverse import** (e.g. `tools.py` importing from `nodes.py`, or `state.py` importing from `graph.py`) is always a blocker.

**c) Is the new constant or class placed in the right file?**
- Model lists (`AVAILABLE_MODELS`) → `app/session/` or `app/agent/nodes.py` (if needed for binding)
- Graph constants (`COMPRESSION_THRESHOLD`, `HOT_CONTEXT_MESSAGES`) → `app/agent/nodes.py`
- State schema changes → `app/agent/state.py`
- Tool-level constants (`MAX_SEARCH_FILE_SIZE`) → `app/agent/tools.py`

**d) Does the `queue/` directory exist?**
Per architectural decision in `opis-projektu.md`, the `queue/` module was cancelled. If any PR adds files under `app/queue/`, it is a blocker.

## Step 4 — Check each AGENTS.md rule

Go through all 10 rules from `AGENTS.md` and evaluate the changed code against each one.
Do not evaluate files that weren't changed in the PR.

| # | Rule | What to check |
|---|---|---|
| 1 | Meaningful names | Variables, functions, classes — no single letters, no vague names like `data`, `result`, `proc` |
| 2 | Single Responsibility | Each function does one thing. No "and" in the function's job description |
| 3 | No magic numbers/strings | Constants have names. No bare `25`, `"gemma3:4b"`, `3` in logic |
| 4 | Error handling | Specific exceptions caught. No bare `except:`. Errors propagated with context |
| 5 | Type hints | All public functions have parameter and return type annotations |
| 6 | DRY | No duplicated logic across functions or files |
| 7 | Small functions | No function longer than ~20 lines. No class with more than ~5 public methods |
| 8 | Comments explain why | No comments that narrate what the code does. Only intent/constraints |
| 9 | Dataclass/TypedDict | No raw dicts for structured data that has a defined shape |
| 10 | Tests for critical logic | Any function affecting agent state or context processing has a test |

## Step 5 — Write the report

Use this exact template:

```
## Code Review — <SCENARIO_ID> | PR #<NUMBER>

### Wynik: ✅ PASS / ❌ FAIL

### Scenariusz
- **ID:** <ID>
- **Typ:** UNIT / INT
- **Opis:** <description from scenarios.md>
- **Test obecny:** ✅ / ❌
- **Test nie jest trywialny:** ✅ / ❌
- **Lokalizacja testu:** `tests/unit/test_X.py::test_function_name`

### Architektura

| Sprawdzenie | Status | Uwaga |
|---|---|---|
| Właściwy moduł | ✅/❌ | Plik trafił do katalogu zgodnego z opis-projektu.md |
| Kierunek importów | ✅/❌ | Import nie idzie "w górę" hierarchii (tools ← nodes ← graph) |
| Lokalizacja stałych/klas | ✅/❌ | Stałe i klasy zdefiniowane w odpowiednim pliku |
| Brak `app/queue/` | ✅/❌ | Moduł kolejki nie istnieje (anulowany per opis-projektu.md) |

### Zasady AGENTS.md

| # | Zasada | Status | Uwaga |
|---|---|---|---|
| 1 | Znaczące nazwy | ✅/❌ | <konkretna uwaga lub "-"> |
| 2 | Single Responsibility | ✅/❌ | <uwaga> |
| 3 | Brak magicznych liczb | ✅/❌ | <uwaga> |
| 4 | Obsługa błędów | ✅/❌ | <uwaga> |
| 5 | Type hints | ✅/❌ | <uwaga> |
| 6 | DRY | ✅/❌ | <uwaga> |
| 7 | Małe funkcje | ✅/❌ | <uwaga> |
| 8 | Komentarze | ✅/❌ | <uwaga> |
| 9 | Dataclass/TypedDict | ✅/❌ | <uwaga> |
| 10 | Testy | ✅/❌ | <uwaga> |

### Blokery — wymagają poprawy przed merge
<Lista konkretnych problemów z lokalizacją pliku i linii. Jeśli brak — napisz "Brak".>
- [ ] `plik.py:12` — <opis problemu>

### Sugestie — nieblokujące
<Opcjonalne uwagi które warto rozważyć ale nie blokują merge.>
- `plik.py:18` — <sugestia>

### Decyzja
PASS → PR może być zmergowany.
FAIL → PR wymaga poprawek. Lista blokerów powyżej.
```

## Zasady wydania werdyktu

**FAIL** jeśli którykolwiek z poniższych warunków jest spełniony:
- Test nie istnieje
- Test jest trywialny (zawsze przechodzi niezależnie od implementacji)
- Test jest w złym katalogu (UNIT w `integration/` lub odwrotnie)
- Jakakolwiek zasada AGENTS.md ma status ❌
- Jakakolwiek kontrola architektoniczna (Step 3b) ma status ❌

**PASS** tylko gdy wszystkie zasady ✅ i test jest poprawny.

## Retry — co zrobić po FAIL

### Attempt 1 → FAIL
Przekaż raport do agenta kodującego z dokładną listą blokerów.
Zakończ wiadomość do agenta kodującego tym dokładnym formatem:

```
[CODE-REVIEW-FEEDBACK]
Scenariusz: <SCENARIO_ID>
PR: #<NUMBER>
Attempt: 1
Status: FAIL
Blokery:
<skopiuj sekcję "Blokery" z raportu>
Oczekiwane działanie: Popraw powyższe problemy, zaktualizuj PR i wywołaj code-review ponownie z Attempt: 2.
[/CODE-REVIEW-FEEDBACK]
```

### Attempt 2 → FAIL
System przestaje angażować agenta kodującego i eskaluje do użytkownika.
Wyświetl raport jak zwykle, a następnie dodaj sekcję:

```
### ⚠️ Eskalacja do użytkownika

To jest drugi nieudany przegląd tego samego scenariusza (<SCENARIO_ID> | PR #<NUMBER>).
Agent kodujący nie był w stanie poprawić wszystkich blokerów po pierwszej rundzie informacji zwrotnej.

Blokery które nadal nie zostały rozwiązane:
<lista nierozwiązanych blokerów>

Wymagana jest Twoja decyzja:
- Zaakceptuj kod mimo naruszeń (wpisz: "akceptuję mimo uwag")
- Odrzuć PR i zacznij scenariusz od nowa (wpisz: "zacznij od nowa")
- Wskaż agentowi kodującemu konkretne rozwiązanie (wpisz własną instrukcję)
```

### Attempt 2 → PASS
Wyświetl normalny raport PASS. Nie ma potrzeby eskalacji.

## Ważne zasady pracy

- Jesteś świeżym agentem. Nie znasz powodów decyzji agenta kodującego. Jeśli coś wygląda dziwnie — zaznacz to jako bloker, nie zakładaj że "na pewno był powód".
- Oceniaj tylko kod w diffie. Nie komentuj plików których PR nie dotknął.
- Bądź konkretny: zawsze podaj nazwę pliku i numer linii przy każdym znalezionym problemie.
- Nie negocjuj blokerów. Jeśli zasada jest naruszona — to FAIL, bez wyjątków.
- Przy Attempt 2 porównaj blokery z Attempt 1 — zaznacz które zostały naprawione, które nie.
