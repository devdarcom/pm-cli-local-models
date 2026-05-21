from dataclasses import dataclass, field


@dataclass
class AgentState:
    model: str
    messages: list[dict[str, str]] = field(default_factory=list)
    context_loaded: bool = False
    done: bool = False
    error_count: int = 0
