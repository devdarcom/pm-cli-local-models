from pathlib import Path
from typing import Optional

PROJECT_CONTEXT_FILENAME = "PROJECT.md"
AGENTS_MD_FILENAME = "AGENTS.md"
CONTEXT_SEPARATOR = "\n\n"


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


def load_agents_md(agents_dir: Path = Path(".")) -> Optional[str]:
    agents_md = agents_dir / AGENTS_MD_FILENAME
    try:
        return agents_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {agents_md}") from e


def build_prompt(
    system_prompt: str,
    project_context: Optional[str] = None,
    agents_context: Optional[str] = None,
) -> list:
    content = system_prompt
    if agents_context:
        content += CONTEXT_SEPARATOR + agents_context
    if project_context:
        content += CONTEXT_SEPARATOR + project_context
    return [{"role": "system", "content": content}]
