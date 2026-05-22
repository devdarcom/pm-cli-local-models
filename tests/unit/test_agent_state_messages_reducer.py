from typing import get_args, get_type_hints

from langgraph.graph.message import add_messages

from app.agent.state import AgentState


def test_messages_field_uses_add_messages_reducer() -> None:
    hints = get_type_hints(AgentState, include_extras=True)
    messages_annotation = hints["messages"]

    assert hasattr(messages_annotation, "__metadata__"), (
        "messages musi być Annotated — brakuje __metadata__"
    )
    args = get_args(messages_annotation)
    assert args[0] is list, "Pierwszy argument Annotated musi być list"
    assert args[1] is add_messages, (
        "Drugi argument Annotated musi być add_messages (reducer LangGraph)"
    )
