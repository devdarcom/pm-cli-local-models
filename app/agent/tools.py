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


def delete_file(path: str) -> str:
    """Usuń plik z systemu plików."""
    try:
        Path(path).unlink()
        return f"✓ Usunięto plik: {path}"
    except FileNotFoundError:
        return f"BŁĄD: Plik nie istnieje: {path}"
    except PermissionError:
        return f"BŁĄD: Brak uprawnień do usunięcia: {path}"


def write_file(path: str, content: str) -> str:
    """Zapisz treść do pliku. Nadpisuje jeśli istnieje. Katalog nadrzędny musi istnieć."""
    try:
        Path(path).write_text(content, encoding="utf-8")
        return f"✓ Zapisano plik: {path}"
    except FileNotFoundError:
        return f"BŁĄD: Katalog nie istnieje: {path}"
    except PermissionError:
        return f"BŁĄD: Brak uprawnień do zapisu: {path}"
