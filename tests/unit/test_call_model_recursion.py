from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.nodes import call_model
from app.agent.state import AgentState


def test_call_model_increments_recursion_count() -> None:
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Cześć")],
        recursion_count=2,
    )

    with patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.bind_tools.return_value = MockChatOllama.return_value
        MockChatOllama.return_value.invoke.return_value = AIMessage(content="OK")

        result = call_model(state)

    assert result["recursion_count"] == 3


def test_call_model_increments_recursion_count_from_zero() -> None:
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Cześć")],
        recursion_count=0,
    )

    with patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.bind_tools.return_value = MockChatOllama.return_value
        MockChatOllama.return_value.invoke.return_value = AIMessage(content="OK")

        result = call_model(state)

    assert result["recursion_count"] == 1
