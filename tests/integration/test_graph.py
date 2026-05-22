from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

import app.agent.graph as graph_module
from app.agent.graph import build_graph
from tests.integration.conftest import SYSTEM_PROMPT_MOCK


def test_graph_accepts_user_message_and_returns_response(mock_ollama_and_context):
    mock_ollama_and_context.return_value.invoke.return_value = AIMessage(content="Jestem agentem AI.")

    graph = build_graph()
    result = graph.invoke({
        "session_id": "test-session",
        "model_name": "gemma3:4b",
        "messages": [HumanMessage(content="Cześć, co potrafisz?")],
    })

    last_message = result["messages"][-1]
    assert isinstance(last_message, AIMessage)
    assert last_message.content == "Jestem agentem AI."


def test_graph_loads_context_as_system_message_before_model_call(mock_ollama_and_context):
    mock_ollama_and_context.return_value.invoke.return_value = AIMessage(content="OK")

    graph = build_graph()
    graph.invoke({
        "session_id": "test-session",
        "model_name": "gemma3:4b",
        "messages": [HumanMessage(content="Zrób coś")],
    })

    messages_passed_to_model = mock_ollama_and_context.return_value.invoke.call_args[0][0]
    assert isinstance(messages_passed_to_model[0], SystemMessage)
    assert SYSTEM_PROMPT_MOCK in messages_passed_to_model[0].content


def test_graph_ends_when_model_response_has_no_tool_call(mock_ollama_and_context):
    mock_ollama_and_context.return_value.invoke.return_value = AIMessage(content="4")

    with patch.object(graph_module, "route_after_model", wraps=graph_module.route_after_model) as spy_router:
        graph = build_graph()
        result = graph.invoke({
            "session_id": "test-session",
            "model_name": "gemma3:4b",
            "messages": [HumanMessage(content="Jakie jest 2+2?")],
        })

    spy_router.assert_called_once()
    assert isinstance(result["messages"][-1], AIMessage)


def test_graph_calls_tool_node_when_model_returns_tool_call(mock_ollama_and_context):
    tool_call_response = AIMessage(
        content="",
        tool_calls=[{
            "name": "read_file",
            "args": {"path": "/nonexistent/path.txt"},
            "id": "call_1",
            "type": "tool_call",
        }],
    )
    mock_ollama_and_context.return_value.invoke.side_effect = [
        tool_call_response,
        AIMessage(content="Gotowe."),
    ]

    graph = build_graph()
    result = graph.invoke({
        "session_id": "test-session",
        "model_name": "gemma3:4b",
        "messages": [HumanMessage(content="Przeczytaj plik main.py")],
    })

    assert any(isinstance(m, ToolMessage) for m in result["messages"])


def test_graph_returns_to_call_model_after_tool_execution(mock_ollama_and_context):
    first_response = AIMessage(
        content="",
        tool_calls=[{
            "name": "read_file",
            "args": {"path": "/nonexistent/path.txt"},
            "id": "call_1",
            "type": "tool_call",
        }],
    )
    final_response = AIMessage(content="Plik nie istnieje.")

    mock_ollama_and_context.return_value.invoke.side_effect = [first_response, final_response]

    graph = build_graph()
    result = graph.invoke({
        "session_id": "test-session",
        "model_name": "gemma3:4b",
        "messages": [HumanMessage(content="Przeczytaj plik")],
    })

    assert mock_ollama_and_context.return_value.invoke.call_count == 2
    assert result["messages"][-1].content == "Plik nie istnieje."
