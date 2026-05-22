from app.agent.nodes import compress_history


def test_compress_history_preserves_system_message() -> None:
    messages = [
        {"role": "system", "content": "Jesteś agentem."},
        {"role": "user", "content": "Napisz kod."},
        {"role": "assistant", "content": "Oto kod..."},
    ]

    result = compress_history(messages, summary="Użytkownik prosił o kod.")

    assert result[0]["role"] == "system"
    assert result[0]["content"] == "Jesteś agentem."
