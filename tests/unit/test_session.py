import pytest

from app.session.manager import Session, create_session, reset_session, set_model


def test_create_session_returns_session_with_correct_model():
    session = create_session(model="llama3.2:3b")

    assert isinstance(session, Session)
    assert session.model == "llama3.2:3b"


def test_create_session_raises_value_error_for_unknown_model():
    with pytest.raises(ValueError, match="nieznany model"):
        create_session(model="nieznany-model-xyz")


def test_reset_session_preserves_model():
    session = create_session(model="llama3.2:3b")

    reset_session(session)

    assert session.model == "llama3.2:3b"


def test_each_session_has_unique_session_id():
    session_a = create_session(model="llama3.2:3b")
    session_b = create_session(model="llama3.2:3b")

    assert session_a.session_id != session_b.session_id


def test_set_model_updates_model_when_model_is_available():
    session = create_session(model="llama3.2:3b")

    set_model(session, "qwen2.5:3b")

    assert session.model == "qwen2.5:3b"


def test_set_model_raises_value_error_for_unavailable_model():
    session = create_session(model="llama3.2:3b")

    with pytest.raises(ValueError, match="nieznany model"):
        set_model(session, "nieznany-model-xyz")
