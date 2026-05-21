from pathlib import Path


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"BŁĄD: Plik nie istnieje: {path}"
    except PermissionError:
        return f"BŁĄD: Brak uprawnień do odczytu: {path}"
