from unittest.mock import patch

import pytest

SYSTEM_PROMPT_MOCK = "Jesteś agentem AI."
PROJECT_CONTEXT_MOCK = "# Projekt testowy"


@pytest.fixture
def mock_ollama_and_context():
    """Patches context loaders and ChatOllama; wires bind_tools to return the same mock."""
    with patch("app.agent.nodes.load_system_prompt", return_value=SYSTEM_PROMPT_MOCK), \
         patch("app.agent.nodes.load_project_context", return_value=PROJECT_CONTEXT_MOCK), \
         patch("app.agent.nodes.load_agents_md", return_value=None), \
         patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.bind_tools.return_value = MockChatOllama.return_value
        yield MockChatOllama
