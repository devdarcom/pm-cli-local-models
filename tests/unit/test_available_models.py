import pytest

from app.session.manager import AVAILABLE_MODELS, create_session

TOOLS_API_MODELS = {"llama3.2:3b", "qwen2.5:3b"}
LEGACY_GEMMA_MODELS = {"gemma3:4b", "gemma:7b", "gemma:2b", "gemma:security"}


def test_available_models_contains_tools_api_models():
    assert TOOLS_API_MODELS.issubset(AVAILABLE_MODELS)


def test_available_models_does_not_contain_gemma_models():
    assert LEGACY_GEMMA_MODELS.isdisjoint(AVAILABLE_MODELS)


def test_create_session_accepts_tools_api_model():
    session = create_session(model="llama3.2:3b")
    assert session.model == "llama3.2:3b"


def test_create_session_rejects_gemma_model():
    with pytest.raises(ValueError):
        create_session(model="gemma3:4b")
