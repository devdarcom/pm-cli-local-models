from app.session.manager import Session, create_session


def test_session_does_not_have_history_field() -> None:
    session = create_session(model="llama3.2:3b")
    assert not hasattr(session, "history"), (
        "Session.history istnieje — powinno być usunięte jako dead code"
    )


def test_session_fields_are_only_model_and_session_id() -> None:
    session = create_session(model="llama3.2:3b")
    field_names = {f.name for f in Session.__dataclass_fields__.values()}
    assert field_names == {"model", "session_id"}, (
        f"Session ma nieoczekiwane pola: {field_names - {'model', 'session_id'}}"
    )
