from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes import AGENT_TOOLS, call_model, load_context_node
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
    graph.add_node("load_context", load_context_node)
    graph.add_node("call_model", call_model)
    graph.add_node(ROUTE_TOOL_NODE, ToolNode(AGENT_TOOLS))
    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "call_model")
    graph.add_conditional_edges(
        "call_model",
        route_after_model,
        {ROUTE_DONE: END, ROUTE_TOOL_NODE: ROUTE_TOOL_NODE},
    )
    graph.add_edge(ROUTE_TOOL_NODE, "call_model")
    return graph.compile()
