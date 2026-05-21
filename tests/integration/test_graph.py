from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.graph import build_graph

SYSTEM_PROMPT_MOCK = "Jesteś agentem AI."
PROJECT_CONTEXT_MOCK = "# Projekt testowy"


def test_graph_accepts_user_message_and_returns_response():
    user_message = HumanMessage(content="Cześć, co potrafisz?")
    mock_response = AIMessage(content="Jestem agentem AI.")

    with patch("app.agent.nodes.load_system_prompt", return_value=SYSTEM_PROMPT_MOCK), \
         patch("app.agent.nodes.load_project_context", return_value=PROJECT_CONTEXT_MOCK), \
         patch("app.agent.nodes.load_agents_md", return_value=None), \
         patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.invoke.return_value = mock_response

        graph = build_graph()
        result = graph.invoke({
            "session_id": "test-session",
            "model_name": "gemma3:4b",
            "messages": [user_message],
        })

    last_message = result["messages"][-1]
    assert isinstance(last_message, AIMessage)
    assert last_message.content == "Jestem agentem AI."


def test_graph_loads_context_as_system_message_before_model_call():
    user_message = HumanMessage(content="Zrób coś")
    mock_response = AIMessage(content="OK")

    with patch("app.agent.nodes.load_system_prompt", return_value=SYSTEM_PROMPT_MOCK), \
         patch("app.agent.nodes.load_project_context", return_value=PROJECT_CONTEXT_MOCK), \
         patch("app.agent.nodes.load_agents_md", return_value=None), \
         patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.invoke.return_value = mock_response

        graph = build_graph()
        graph.invoke({
            "session_id": "test-session",
            "model_name": "gemma3:4b",
            "messages": [user_message],
        })

    messages_passed_to_model = MockChatOllama.return_value.invoke.call_args[0][0]
    assert isinstance(messages_passed_to_model[0], SystemMessage)
    assert SYSTEM_PROMPT_MOCK in messages_passed_to_model[0].content
