from dataclasses import dataclass, field
import uuid


@dataclass
class Session:
    model: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    history: list[dict[str, str]] = field(default_factory=list)


def create_session(model: str) -> Session:
    return Session(model=model)
