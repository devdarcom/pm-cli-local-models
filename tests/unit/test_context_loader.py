import pytest

from app.agent.nodes import load_project_context


def test_load_project_context_returns_content_when_file_exists(tmp_path):
    project_md = tmp_path / "PROJECT.md"
    project_md.write_text("# Mój projekt")

    content = load_project_context(project_dir=tmp_path)

    assert content == "# Mój projekt"
