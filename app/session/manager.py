from dataclasses import dataclass, field
import uuid

import ollama

AVAILABLE_MODELS = {"llama3.2:3b", "qwen2.5:3b"}


@dataclass
class Session:
    model: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))


def _validate_model(model: str) -> None:
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"nieznany model: '{model}'. Dostępne: {sorted(AVAILABLE_MODELS)}")


def create_session(model: str) -> Session:
    _validate_model(model)
    return Session(model=model)


def set_model(session: Session, model: str) -> None:
    _validate_model(model)
    session.model = model


def available_models() -> list[str]:
    response = ollama.list()
    return [m.model for m in response.models if m.model is not None]


def reset_session(session: Session) -> None:
    # Historia konwersacji przechowywana jest w AgentState.messages (LangGraph),
    # nie w Session — reset sesji nie wymaga już czyszczenia lokalnej listy.
    pass
