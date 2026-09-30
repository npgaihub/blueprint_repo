from collections.abc import AsyncIterator, Iterator

import pytest
from anthropic.types.beta import BetaMessageParam
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings, get_settings
from app.llm import get_llm
from app.main import app


class FakeLLM:
    """Stands in for LLMService so tests never call the real API."""

    def __init__(self) -> None:
        self.calls: list[list[BetaMessageParam]] = []
        self.error: Exception | None = None

    async def complete(self, messages: list[BetaMessageParam]) -> str:
        self.calls.append(messages)
        if self.error:
            raise self.error
        return "Hallo!"

    async def stream(self, messages: list[BetaMessageParam]) -> AsyncIterator[str]:
        self.calls.append(messages)
        for chunk in ["Hal", "lo!"]:
            yield chunk


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def client(fake_llm: FakeLLM) -> Iterator[TestClient]:
    app.dependency_overrides[get_llm] = lambda: fake_llm
    app.dependency_overrides[get_settings] = lambda: Settings(app_api_key=SecretStr("secret"))
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
