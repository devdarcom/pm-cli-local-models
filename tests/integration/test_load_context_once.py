from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.graph import build_graph


def test_load_context_node_does_not_duplicate_system_message_on_second_invoke(
    mock_ollama_and_context,
):
    mock_ollama_and_context.return_value.invoke.return_value = AIMessage(content="Odpowiedź 1.")
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
    mock_ollama_and_context.return_value.invoke.return_value = AIMessage(content="Odpowiedź 2.")

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
