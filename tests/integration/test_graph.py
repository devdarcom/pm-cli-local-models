from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import build_graph


def test_graph_accepts_user_message_and_returns_response():
    user_message = HumanMessage(content="Cześć, co potrafisz?")
    mock_response = AIMessage(content="Jestem agentem AI.")

    with patch("app.agent.nodes.ChatOllama") as MockChatOllama:
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
