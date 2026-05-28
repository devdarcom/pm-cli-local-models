from pathlib import Path

SKILLS_DIRECTORY = Path(".cursor/skills")


def list_skills() -> list[str]:
    if not SKILLS_DIRECTORY.is_dir():
        return []

    return sorted(
        skill_dir.name
        for skill_dir in SKILLS_DIRECTORY.iterdir()
        if skill_dir.is_dir()
    )
