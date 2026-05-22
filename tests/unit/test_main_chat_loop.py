from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

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
