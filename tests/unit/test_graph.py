from langchain_core.messages import AIMessage

from app.agent.graph import route_after_model
from app.agent.state import AgentState


def test_router_returns_tool_node_when_response_has_tool_call():
    state = AgentState(
        session_id="s1",
        model_name="gemma3:4b",
        messages=[
            AIMessage(
                content="",
                tool_calls=[{"name": "read_file", "args": {"path": "foo.py"}, "id": "call_1", "type": "tool_call"}],
            )
        ],
    )

    result = route_after_model(state)

    assert result == "tool_node"


def test_router_returns_done_when_response_has_no_tool_call():
    state = AgentState(
        session_id="s1",
        model_name="gemma3:4b",
        messages=[AIMessage(content="Oto moja odpowiedź.")],
    )

    result = route_after_model(state)

    assert result == "done"


def test_router_routes_to_error_handler_on_model_error_with_remaining_retries():
    state = AgentState(
        session_id="s1",
        model_name="gemma3:4b",
        messages=[AIMessage(content="")],
        error_type="model_error",
        retry_count=1,
    )

    result = route_after_model(state)

    assert result == "error_handler"


def test_router_routes_to_escalation_when_retries_exhausted():
    state = AgentState(
        session_id="s1",
        model_name="gemma3:4b",
        messages=[AIMessage(content="")],
        error_type="model_error",
        retry_count=3,
    )

    result = route_after_model(state)

    assert result == "escalate_to_user"
