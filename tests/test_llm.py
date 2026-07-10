import pytest

from civisynth.config import Settings
from civisynth.llm import get_provider
from civisynth.llm.mock import MockProvider


def test_default_provider_is_mock():
    provider = get_provider(Settings())
    assert isinstance(provider, MockProvider)


def test_mock_is_deterministic():
    llm = MockProvider()
    prompt = "[SUMMARIZE] First point. Second point. Third point. Fourth point."
    assert llm.complete(prompt) == llm.complete(prompt)
    assert "First point." in llm.complete(prompt)


def test_mock_claims_extraction_keeps_factual_sentences():
    llm = MockProvider()
    out = llm.complete("[CLAIMS] Turnout was 66 percent. Amazing! The bill will pass.")
    assert "66 percent" in out


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        get_provider(Settings(llm_provider="nonsense"))


def test_real_providers_require_keys():
    with pytest.raises(RuntimeError):
        get_provider(Settings(llm_provider="anthropic"))
    with pytest.raises(RuntimeError):
        get_provider(Settings(llm_provider="openai"))
