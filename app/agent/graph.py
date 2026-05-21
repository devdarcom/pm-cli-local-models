from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes import AGENT_TOOLS, call_model, load_context_node
from app.agent.state import AgentState

LOAD_CONTEXT_NODE = "load_context"
CALL_MODEL_NODE = "call_model"
ROUTE_TOOL_NODE = "tool_node"
ROUTE_DONE = "done"


def route_after_model(state: AgentState) -> Literal["tool_node", "done"]:
    last_message = state.messages[-1]
    if getattr(last_message, "tool_calls", None):
        return ROUTE_TOOL_NODE
    return ROUTE_DONE


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node(LOAD_CONTEXT_NODE, load_context_node)
    graph.add_node(CALL_MODEL_NODE, call_model)
    graph.add_node(ROUTE_TOOL_NODE, ToolNode(AGENT_TOOLS))
    graph.add_edge(START, LOAD_CONTEXT_NODE)
    graph.add_edge(LOAD_CONTEXT_NODE, CALL_MODEL_NODE)
    graph.add_conditional_edges(
        CALL_MODEL_NODE,
        route_after_model,
        {ROUTE_DONE: END, ROUTE_TOOL_NODE: ROUTE_TOOL_NODE},
    )
    graph.add_edge(ROUTE_TOOL_NODE, CALL_MODEL_NODE)
    return graph.compile()
