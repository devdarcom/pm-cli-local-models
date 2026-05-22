from langchain_core.messages import HumanMessage

from app.agent.nodes import error_handler_node, escalate_to_user_node
from app.agent.state import AgentState


def test_error_handler_increments_retry_count_and_appends_feedback():
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Zrób coś")],
        retry_count=1,
        last_error="timeout",
        error_node="call_model",
        error_type="model_error",
    )

    result = error_handler_node(state)

    assert result["retry_count"] == 2
    assert result["error_type"] is None
    assert result["error_node"] is None
    assert len(result["messages"]) == 1
    assert "timeout" in result["messages"][0].content


def test_escalate_to_user_resets_error_state():
    state = AgentState(
        session_id="test-session",
        model_name="gemma3:4b",
        messages=[HumanMessage(content="Zrób coś")],
        retry_count=3,
        last_error="boom",
        error_node="call_model",
        error_type="model_error",
    )

    result = escalate_to_user_node(state)

    assert result["retry_count"] == 0
    assert result["last_error"] is None
    assert result["error_node"] is None
    assert result["error_type"] is None
    assert "Nie udało się wykonać zadania" in result["messages"][0].content
