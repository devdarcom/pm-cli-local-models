from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.nodes import call_model
from app.agent.state import AgentState, RECURSION_LIMIT


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
    assert result["retry_count"] == 0
    assert result["error_type"] is None


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


def test_call_model_returns_recursion_error_when_limit_reached() -> None:
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Cześć")],
        recursion_count=RECURSION_LIMIT,
    )

    result = call_model(state)

    assert result["error_type"] == "recursion_limit"
    assert result["error_node"] == "call_model"
    assert "limit kroków" in result["last_error"]


def test_call_model_returns_model_error_on_exception() -> None:
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Cześć")],
    )

    with patch("app.agent.nodes.ChatOllama") as mock_chat:
        mock_chat.return_value.bind_tools.return_value = mock_chat.return_value
        mock_chat.return_value.invoke.side_effect = RuntimeError("boom")

        result = call_model(state)

    assert result["error_type"] == "model_error"
    assert result["error_node"] == "call_model"
    assert result["last_error"] == "boom"
