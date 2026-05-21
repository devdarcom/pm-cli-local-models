from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

RECURSION_LIMIT = 25


class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list = []
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
