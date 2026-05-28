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


def test_run_chat_loop_resets_history_without_changing_session_for_reset_command(
    monkeypatch,
):
    user_inputs = iter(["pierwsza", "\\reset", "druga", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    session_ids: list[str] = []
    model_names: list[str] = []
    message_lengths: list[int] = []

    class ResetTrackingGraph:
        def invoke(self, payload: dict) -> dict:
            session_ids.append(payload["session_id"])
            model_names.append(payload["model_name"])
            message_lengths.append(len(payload["messages"]))
            return {"messages": payload["messages"] + [AIMessage(content="OK")]}

    monkeypatch.setattr(
        main_module,
        "create_session",
        lambda model: (_ for _ in ()).throw(AssertionError("create_session should not be called")),
    )

    session = SimpleNamespace(model="llama3.2:3b", session_id="s1")

    run_chat_loop(ResetTrackingGraph(), session)

    assert session_ids == ["s1", "s1"]
    assert model_names == ["llama3.2:3b", "llama3.2:3b"]
    assert message_lengths == [1, 1]


def test_run_chat_loop_runs_compression_for_compress_command(monkeypatch):
    user_inputs = iter(["pierwsza", "druga", "\\compress", "trzecia", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    graph_invoke_count = 0
    compress_call_count = 0
    session_ids_in_compress: list[str] = []
    model_names_in_compress: list[str] = []

    class CompressionTrackingGraph:
        def invoke(self, payload: dict) -> dict:
            nonlocal graph_invoke_count
            graph_invoke_count += 1
            return {"messages": payload["messages"] + [AIMessage(content="OK")]}

    def fake_compress_node(state):
        nonlocal compress_call_count
        compress_call_count += 1
        session_ids_in_compress.append(state.session_id)
        model_names_in_compress.append(state.model_name)
        compressed_messages = [
            state.messages[0],
            AIMessage(content="[Skompresowany kontekst] podsumowanie"),
        ]
        return {"messages": compressed_messages, "summary": "podsumowanie"}

    monkeypatch.setattr(main_module, "compress_node", fake_compress_node)

    session = SimpleNamespace(model="llama3.2:3b", session_id="s1")

    run_chat_loop(CompressionTrackingGraph(), session)

    assert compress_call_count == 1
    assert session_ids_in_compress == ["s1"]
    assert model_names_in_compress == ["llama3.2:3b"]
    assert graph_invoke_count == 3


def test_run_chat_loop_updates_session_model_for_model_command(monkeypatch):
    user_inputs = iter(["pierwsza", "\\model llama3.2:3b", "druga", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(user_inputs))

    session_ids: list[str] = []
    model_names: list[str] = []
    message_lengths: list[int] = []

    class ModelTrackingGraph:
        def invoke(self, payload: dict) -> dict:
            session_ids.append(payload["session_id"])
            model_names.append(payload["model_name"])
            message_lengths.append(len(payload["messages"]))
            return {"messages": payload["messages"] + [AIMessage(content="OK")]}

    session = SimpleNamespace(model="qwen2.5:3b", session_id="s1")

    run_chat_loop(ModelTrackingGraph(), session)

    assert session.model == "llama3.2:3b"
    assert session_ids == ["s1", "s1"]
    assert model_names == ["qwen2.5:3b", "llama3.2:3b"]
    assert message_lengths == [1, 3]
