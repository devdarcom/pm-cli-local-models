import pytest
from pydantic import ValidationError

from app.agent.state import AgentState


def test_agent_state_has_required_pydantic_fields():
    state = AgentState(model_name="gemma3:4b", session_id="abc-123")

    assert hasattr(state, "messages")
    assert hasattr(state, "session_id")
    assert hasattr(state, "model_name")
    assert hasattr(state, "recursion_count")
    assert hasattr(state, "retry_count")
    assert hasattr(state, "last_error")
    assert hasattr(state, "error_node")
    assert hasattr(state, "error_type")
    assert hasattr(state, "summary")
    assert hasattr(state, "spawned_agents")


def test_agent_state_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        AgentState(model_name="gemma3:4b", session_id="abc-123", nieznane_pole="wartość")


def test_agent_state_recursion_count_raises_above_limit():
    with pytest.raises(ValidationError, match="recursion_count"):
        AgentState(model_name="gemma3:4b", session_id="abc-123", recursion_count=26)


def test_agent_state_default_values():
    state = AgentState(model_name="gemma3:4b", session_id="abc-123")

    assert state.messages == []
    assert state.recursion_count == 0
    assert state.retry_count == 0
    assert state.last_error is None
    assert state.error_node is None
    assert state.error_type is None
    assert state.summary is None
    assert state.spawned_agents == []
