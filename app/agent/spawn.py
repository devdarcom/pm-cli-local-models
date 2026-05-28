from dataclasses import dataclass


@dataclass
class SessionContext:
    session_id: str
    model_name: str


def start_spawn_flow(session: SessionContext) -> None:
    input("Opis zadania sub-agenta: ").strip()
