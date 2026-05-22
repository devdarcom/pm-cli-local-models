# Tools Module Interface

## Scope
`app/agent/tools.py`

## Public Contracts

- `read_file(path: str) -> dict[str, Any]`
- `write_file(path: str, content: str) -> dict[str, Any]`
- `list_directory(path: str) -> dict[str, Any]`
- `delete_file(path: str) -> dict[str, Any]`
- `search_in_files(directory: str, phrase: str) -> dict[str, Any]`

All tool outputs follow:

```python
{"ok": bool, "data": Any, "error": str | None}
```

## Invariants

- Tools return errors in contract form (no uncaught tool exceptions).
- File name resolution for `read_file` is recursive and project-oriented.
- Candidate lookup must ignore non-project directories (for example `.venv`).

## Change Rules

- Any new tool must adopt the same output contract.
- Any change to result schema requires test updates in `tests/unit/test_tools.py`.
