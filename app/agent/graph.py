from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes import (
    AGENT_TOOLS,
    COMPRESSION_MESSAGE_THRESHOLD,
    MAX_MODEL_RETRIES,
    call_model,
    compress_node,
    error_handler_node,
    escalate_to_user_node,
    load_context_node,
)
from app.agent.state import AgentState

LOAD_CONTEXT_NODE = "load_context"
CALL_MODEL_NODE = "call_model"
ROUTE_TOOL_NODE = "tool_node"
COMPRESS_NODE = "compress"
ERROR_HANDLER_NODE = "error_handler"
ESCALATE_NODE = "escalate_to_user"
ROUTE_DONE = "done"


def _should_route_to_compression(state: AgentState) -> bool:
    if state.summary is not None:
        return False
    return len(state.messages) > COMPRESSION_MESSAGE_THRESHOLD


def route_after_model(
    state: AgentState,
) -> Literal["tool_node", "done", "error_handler", "escalate_to_user", "compress_node"]:
    if state.error_type == "recursion_limit":
        return ESCALATE_NODE
    if state.error_type == "model_error":
        if state.retry_count >= MAX_MODEL_RETRIES:
            return ESCALATE_NODE
        return ERROR_HANDLER_NODE

    if not state.messages:
        return ROUTE_DONE

    if _should_route_to_compression(state):
        return COMPRESS_NODE

    last_message = state.messages[-1]
    if getattr(last_message, "tool_calls", None):
        return ROUTE_TOOL_NODE
    return ROUTE_DONE


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node(LOAD_CONTEXT_NODE, load_context_node)
    graph.add_node(CALL_MODEL_NODE, call_model)
    graph.add_node(COMPRESS_NODE, compress_node)
    graph.add_node(ROUTE_TOOL_NODE, ToolNode(AGENT_TOOLS))
    graph.add_node(ERROR_HANDLER_NODE, error_handler_node)
    graph.add_node(ESCALATE_NODE, escalate_to_user_node)
    graph.add_edge(START, LOAD_CONTEXT_NODE)
    graph.add_edge(LOAD_CONTEXT_NODE, CALL_MODEL_NODE)
    graph.add_conditional_edges(
        CALL_MODEL_NODE,
        route_after_model,
        {
            ROUTE_DONE: END,
            ROUTE_TOOL_NODE: ROUTE_TOOL_NODE,
            COMPRESS_NODE: COMPRESS_NODE,
            ERROR_HANDLER_NODE: ERROR_HANDLER_NODE,
            ESCALATE_NODE: ESCALATE_NODE,
        },
    )
    graph.add_edge(COMPRESS_NODE, CALL_MODEL_NODE)
    graph.add_edge(ERROR_HANDLER_NODE, CALL_MODEL_NODE)
    graph.add_edge(ESCALATE_NODE, END)
    graph.add_edge(ROUTE_TOOL_NODE, CALL_MODEL_NODE)
    return graph.compile()
