from app.session.manager import Session, create_session


def test_create_session_returns_session_with_correct_model_and_empty_history():
    session = create_session(model="gemma3:4b")

    assert isinstance(session, Session)
    assert session.model == "gemma3:4b"
    assert session.history == []
