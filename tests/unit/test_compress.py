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


def test_compress_history_reduces_messages_to_system_and_summary() -> None:
    messages = [
        {"role": "user", "content": "Start rozmowy"},
        {"role": "system", "content": "Jesteś agentem."},
        {"role": "assistant", "content": "Krok 1"},
        {"role": "user", "content": "Krok 2"},
    ]

    result = compress_history(messages, summary="Skrót")

    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "Jesteś agentem."


def test_compress_history_summary_contains_required_tag() -> None:
    messages = [
        {"role": "system", "content": "Jesteś agentem."},
        {"role": "user", "content": "Długi kontekst rozmowy"},
    ]

    result = compress_history(messages, summary="Podsumowanie")

    assert result[1]["role"] == "assistant"
    assert result[1]["content"].startswith("[Skompresowany kontekst] ")
