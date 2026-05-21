import pytest

from app.agent.nodes import load_project_context, load_system_prompt


def test_load_project_context_returns_content_when_file_exists(tmp_path):
    project_md = tmp_path / "PROJECT.md"
    project_md.write_text("# Mój projekt")

    content = load_project_context(project_dir=tmp_path)

    assert content == "# Mój projekt"


def test_load_project_context_returns_none_when_file_missing(tmp_path):
    content = load_project_context(project_dir=tmp_path)

    assert content is None


def test_load_system_prompt_returns_file_content(tmp_path):
    prompt_file = tmp_path / "system_prompt.md"
    prompt_file.write_text("Jesteś pomocnym asystentem.")

    content = load_system_prompt(prompt_path=prompt_file)

    assert content == "Jesteś pomocnym asystentem."
