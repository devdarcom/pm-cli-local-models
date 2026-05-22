from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.graph import build_graph

SYSTEM_PROMPT_MOCK = "Jesteś agentem AI."
PROJECT_CONTEXT_MOCK = "# Projekt testowy"


def _make_mock_context_and_ollama():
    return (
        patch("app.agent.nodes.load_system_prompt", return_value=SYSTEM_PROMPT_MOCK),
        patch("app.agent.nodes.load_project_context", return_value=PROJECT_CONTEXT_MOCK),
        patch("app.agent.nodes.load_agents_md", return_value=None),
    )


def test_load_context_node_does_not_duplicate_system_message_on_second_invoke():
    context_patches = _make_mock_context_and_ollama()
    with context_patches[0], context_patches[1], context_patches[2], \
         patch("app.agent.nodes.ChatOllama") as MockChatOllama:
        MockChatOllama.return_value.bind_tools.return_value = MockChatOllama.return_value
        MockChatOllama.return_value.invoke.return_value = AIMessage(content="Odpowiedź 1.")

        graph = build_graph()

        result_turn1 = graph.invoke({
            "session_id": "test-session",
            "model_name": "gemma3:4b",
            "messages": [HumanMessage(content="Pierwsze pytanie")],
        })

        system_messages_after_turn1 = [
            m for m in result_turn1["messages"] if isinstance(m, SystemMessage)
        ]
        assert len(system_messages_after_turn1) == 1, (
            "Powinien być dokładnie jeden SystemMessage po pierwszym turnie"
        )

        # Simulate second turn: pass accumulated messages from turn 1
        accumulated_messages = result_turn1["messages"] + [HumanMessage(content="Drugie pytanie")]
        MockChatOllama.return_value.invoke.return_value = AIMessage(content="Odpowiedź 2.")

        result_turn2 = graph.invoke({
            "session_id": "test-session",
            "model_name": "gemma3:4b",
            "messages": accumulated_messages,
        })

    system_messages_after_turn2 = [
        m for m in result_turn2["messages"] if isinstance(m, SystemMessage)
    ]
    assert len(system_messages_after_turn2) == 1, (
        "load_context_node nie powinien duplikować SystemMessage przy kolejnym graph.invoke()"
    )
