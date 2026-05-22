from pathlib import Path
from typing import Any

MAX_SEARCH_FILE_SIZE = 1_000_000
FILENAME_SEARCH_EXCLUDED_DIRS = {".venv", ".git", "__pycache__"}


def _success_result(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data, "error": None}


def _error_result(message: str, data: Any = None) -> dict[str, Any]:
    return {"ok": False, "data": data, "error": message}


def _resolve_filename_candidates(filename: str) -> list[Path]:
    candidates: list[Path] = []
    for path in Path(".").rglob(filename):
        if not path.is_file():
            continue
        if any(directory in FILENAME_SEARCH_EXCLUDED_DIRS for directory in path.parts):
            continue
        candidates.append(path)
    return sorted(candidates)


def read_file(path: str) -> dict[str, Any]:
    """Odczytaj zawartość pliku tekstowego."""
    target_path = Path(path)
    try:
        return _success_result(target_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        # If user provided only a filename, try resolving it in project tree.
        if target_path.name == path:
            candidates = _resolve_filename_candidates(path)
            if len(candidates) == 1:
                resolved_path = candidates[0]
                try:
                    return _success_result(resolved_path.read_text(encoding="utf-8"))
                except PermissionError:
                    return _error_result(f"BŁĄD: Brak uprawnień do odczytu: {resolved_path}")
            if len(candidates) > 1:
                candidate_paths = [str(candidate) for candidate in candidates[:5]]
                return _error_result(
                    (
                        f"BŁĄD: Znaleziono wiele plików o nazwie: {path}. "
                        "Podaj dokładną ścieżkę."
                    ),
                    {"candidates": candidate_paths},
                )

        return _error_result(f"BŁĄD: Plik nie istnieje: {path}")
    except PermissionError:
        return _error_result(f"BŁĄD: Brak uprawnień do odczytu: {path}")


def list_directory(path: str) -> dict[str, Any]:
    """Zwróć listę nazw plików i katalogów w podanym katalogu."""
    try:
        entries = sorted(entry.name for entry in Path(path).iterdir())
        return _success_result(entries)
    except FileNotFoundError:
        return _error_result(f"BŁĄD: Katalog nie istnieje: {path}")
    except PermissionError:
        return _error_result(f"BŁĄD: Brak uprawnień do odczytu: {path}")


def search_in_files(directory: str, phrase: str) -> dict[str, Any]:
    """Rekurencyjnie wyszukaj frazę w plikach tekstowych."""
    root = Path(directory)
    try:
        matches: list[str] = []
        skipped_files: list[str] = []
        for entry in root.rglob("*"):
            if not entry.is_file():
                continue
            try:
                if entry.stat().st_size > MAX_SEARCH_FILE_SIZE:
                    skipped_files.append(str(entry.relative_to(root)))
                    continue
                content = entry.read_text(encoding="utf-8", errors="ignore")
                if phrase in content:
                    matches.append(str(entry.relative_to(root)))
            except (PermissionError, OSError):
                # Błędy pojedynczych plików nie przerywają całego skanu.
                skipped_files.append(str(entry.relative_to(root)))
        return _success_result({"matches": matches, "skipped_files": skipped_files})
    except FileNotFoundError:
        return _error_result(f"BŁĄD: Katalog nie istnieje: {directory}")
    except PermissionError:
        return _error_result(f"BŁĄD: Brak uprawnień do odczytu: {directory}")


def delete_file(path: str) -> dict[str, Any]:
    """Usuń plik z systemu plików."""
    try:
        Path(path).unlink()
        return _success_result(f"✓ Usunięto plik: {path}")
    except FileNotFoundError:
        return _error_result(f"BŁĄD: Plik nie istnieje: {path}")
    except PermissionError:
        return _error_result(f"BŁĄD: Brak uprawnień do usunięcia: {path}")


def write_file(path: str, content: str) -> dict[str, Any]:
    """Zapisz treść do pliku. Nadpisuje jeśli istnieje. Katalog nadrzędny musi istnieć."""
    try:
        Path(path).write_text(content, encoding="utf-8")
        return _success_result(f"✓ Zapisano plik: {path}")
    except FileNotFoundError:
        return _error_result(f"BŁĄD: Katalog nie istnieje: {path}")
    except PermissionError:
        return _error_result(f"BŁĄD: Brak uprawnień do zapisu: {path}")
