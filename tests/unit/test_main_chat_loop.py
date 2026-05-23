from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

import main as main_module
from main import run_chat_loop


class FakeGraph:
    def __init__(self) -> None:
        self.calls: list[list] = []

    def invoke(self, payload: dict) -> dict:
        messages = payload["messages"]
        self.calls.append(messages)
        return {"messages": messages + [AIMessage(content="OK")]}


def test_run_chat_loop_accumulates_conversation_history(monkeypatch):
    user_inputs = iter(["pierwsza", "druga", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    graph = FakeGraph()
    session = SimpleNamespace(model="llama3.2:3b", session_id="s1")

    run_chat_loop(graph, session)

    assert len(graph.calls) == 2
    assert len(graph.calls[0]) == 1
    assert isinstance(graph.calls[0][0], HumanMessage)
    assert graph.calls[0][0].content == "pierwsza"

    assert len(graph.calls[1]) == 3
    assert isinstance(graph.calls[1][0], HumanMessage)
    assert isinstance(graph.calls[1][1], AIMessage)
    assert isinstance(graph.calls[1][2], HumanMessage)
    assert graph.calls[1][2].content == "druga"


def test_run_chat_loop_starts_new_session_and_clears_history_for_new_command(monkeypatch):
    user_inputs = iter(["pierwsza", "\\new", "druga", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    session_ids: list[str] = []
    message_lengths: list[int] = []

    class SessionTrackingGraph:
        def invoke(self, payload: dict) -> dict:
            session_ids.append(payload["session_id"])
            message_lengths.append(len(payload["messages"]))
            return {"messages": payload["messages"] + [AIMessage(content="OK")]}

    initial_session = SimpleNamespace(model="llama3.2:3b", session_id="s1")
    replacement_session = SimpleNamespace(model="llama3.2:3b", session_id="s2")
    monkeypatch.setattr(
        main_module,
        "create_session",
        lambda model: replacement_session,
    )

    run_chat_loop(SessionTrackingGraph(), initial_session)

    assert session_ids == ["s1", "s2"]
    assert message_lengths == [1, 1]
