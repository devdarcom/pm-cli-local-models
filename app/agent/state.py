from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from langgraph.graph.message import add_messages

RECURSION_LIMIT = 25


class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: Annotated[list, add_messages] = []
    session_id: str
    model_name: str
    recursion_count: int = 0
    retry_count: int = 0
    last_error: Optional[str] = None
    error_node: Optional[str] = None
    error_type: Optional[str] = None
    summary: Optional[str] = None
    spawned_agents: list[str] = []

    @field_validator("recursion_count")
    @classmethod
    def check_recursion_limit(cls, v: int) -> int:
        if v > RECURSION_LIMIT:
            raise ValueError(f"recursion_count {v} przekroczył limit {RECURSION_LIMIT}")
        return v
