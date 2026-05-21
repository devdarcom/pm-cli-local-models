import pytest

from app.agent.nodes import load_project_context, load_system_prompt, build_prompt, load_agents_md


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


def test_build_prompt_combines_all_three_contexts():
    system_prompt = "Jesteś pomocnym asystentem."
    agents_context = "# Zasady clean code"
    project_context = "# Mój projekt"

    messages = build_prompt(
        system_prompt=system_prompt,
        agents_context=agents_context,
        project_context=project_context,
    )

    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert system_prompt in messages[0]["content"]
    assert agents_context in messages[0]["content"]
    assert project_context in messages[0]["content"]


def test_build_prompt_skips_project_context_when_none():
    system_prompt = "Jesteś pomocnym asystentem."

    messages = build_prompt(system_prompt=system_prompt, project_context=None)

    assert len(messages) == 1
    assert messages[0]["content"] == system_prompt


def test_build_prompt_skips_agents_context_when_none():
    system_prompt = "Jesteś pomocnym asystentem."

    messages = build_prompt(system_prompt=system_prompt, agents_context=None)

    assert len(messages) == 1
    assert messages[0]["content"] == system_prompt


def test_build_prompt_agents_context_appears_before_project_context():
    system_prompt = "Jesteś pomocnym asystentem."
    agents_context = "# Zasady"
    project_context = "# Projekt"

    messages = build_prompt(
        system_prompt=system_prompt,
        agents_context=agents_context,
        project_context=project_context,
    )

    content = messages[0]["content"]
    assert content.index(agents_context) < content.index(project_context)


def test_load_agents_md_returns_none_when_file_missing(tmp_path):
    content = load_agents_md(agents_dir=tmp_path)

    assert content is None


def test_load_agents_md_returns_content_when_file_exists(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Zasady clean code")

    content = load_agents_md(agents_dir=tmp_path)

    assert content == "# Zasady clean code"
