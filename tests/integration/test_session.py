from unittest.mock import MagicMock, patch

from app.session.manager import available_models


def test_available_models_returns_list_from_ollama():
    mock_model_a = MagicMock()
    mock_model_a.model = "llama3.2:3b"
    mock_model_b = MagicMock()
    mock_model_b.model = "qwen2.5:3b"

    mock_response = MagicMock()
    mock_response.models = [mock_model_a, mock_model_b]

    with patch("app.session.manager.ollama.list", return_value=mock_response):
        result = available_models()

    assert result == ["llama3.2:3b", "qwen2.5:3b"]
