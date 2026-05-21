from pathlib import Path
from typing import Optional

PROJECT_CONTEXT_FILENAME = "PROJECT.md"


def load_project_context(project_dir: Path = Path(".")) -> Optional[str]:
    project_md = project_dir / PROJECT_CONTEXT_FILENAME
    try:
        return project_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {project_md}") from e


def load_system_prompt(prompt_path: Path) -> str:
    try:
        return prompt_path.read_text(encoding="utf-8")
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {prompt_path}") from e
