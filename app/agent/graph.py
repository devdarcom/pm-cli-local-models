from typing import Literal

from app.agent.state import AgentState

ROUTE_TOOL_NODE = "tool_node"
ROUTE_DONE = "done"


def route_after_model(state: AgentState) -> Literal["tool_node", "done"]:
    last_message = state.messages[-1]
    if getattr(last_message, "tool_calls", None):
        return ROUTE_TOOL_NODE
    return ROUTE_DONE
