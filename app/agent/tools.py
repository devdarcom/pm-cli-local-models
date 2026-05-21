from pathlib import Path


def read_file(path: str) -> str:
    """Odczytaj zawartość pliku tekstowego i zwróć ją jako string."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"BŁĄD: Plik nie istnieje: {path}"
    except PermissionError:
        return f"BŁĄD: Brak uprawnień do odczytu: {path}"


def list_directory(path: str) -> list[str]:
    """Zwróć listę nazw plików i katalogów w podanym katalogu."""
    try:
        return [entry.name for entry in Path(path).iterdir()]
    except FileNotFoundError:
        return [f"BŁĄD: Katalog nie istnieje: {path}"]
    except PermissionError:
        return [f"BŁĄD: Brak uprawnień do odczytu: {path}"]
