from app.agent.state import AgentState


def test_agent_state_has_required_fields():
    state = AgentState(model="gemma3:4b")

    assert hasattr(state, "messages")
    assert hasattr(state, "model")
    assert hasattr(state, "context_loaded")
    assert hasattr(state, "done")
    assert hasattr(state, "error_count")


def test_agent_state_context_loaded_defaults_to_false():
    state = AgentState(model="gemma3:4b")

    assert state.context_loaded is False


def test_agent_state_done_defaults_to_false():
    state = AgentState(model="gemma3:4b")

    assert state.done is False
