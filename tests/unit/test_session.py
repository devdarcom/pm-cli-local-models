import pytest

from app.session.manager import Session, create_session, reset_session


def test_create_session_returns_session_with_correct_model_and_empty_history():
    session = create_session(model="gemma3:4b")

    assert isinstance(session, Session)
    assert session.model == "gemma3:4b"
    assert session.history == []


def test_create_session_raises_value_error_for_unknown_model():
    with pytest.raises(ValueError, match="nieznany model"):
        create_session(model="nieznany-model-xyz")


def test_reset_session_clears_history_and_preserves_model():
    session = create_session(model="gemma3:4b")
    session.history = [{"role": "user", "content": "cześć"}]

    reset_session(session)

    assert session.history == []
    assert session.model == "gemma3:4b"


def test_each_session_has_unique_session_id():
    session_a = create_session(model="gemma3:4b")
    session_b = create_session(model="gemma3:4b")

    assert session_a.session_id != session_b.session_id
