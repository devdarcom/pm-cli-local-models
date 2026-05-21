import pytest
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
