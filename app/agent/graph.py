from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import call_model
from app.agent.state import AgentState

ROUTE_TOOL_NODE = "tool_node"
ROUTE_DONE = "done"


def route_after_model(state: AgentState) -> Literal["tool_node", "done"]:
    last_message = state.messages[-1]
    if getattr(last_message, "tool_calls", None):
        return ROUTE_TOOL_NODE
    return ROUTE_DONE


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("call_model", call_model)
    graph.add_edge(START, "call_model")
    graph.add_edge("call_model", END)
    return graph.compile()
