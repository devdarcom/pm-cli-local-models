from dataclasses import dataclass, field
import uuid

AVAILABLE_MODELS = {"gemma3:4b", "gemma:7b", "gemma:2b", "gemma:security"}


@dataclass
class Session:
    model: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))


def create_session(model: str) -> Session:
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"nieznany model: '{model}'. Dostępne: {sorted(AVAILABLE_MODELS)}")
    return Session(model=model)


def reset_session(session: Session) -> None:
    # Historia konwersacji przechowywana jest w AgentState.messages (LangGraph),
    # nie w Session — reset sesji nie wymaga już czyszczenia lokalnej listy.
    pass
