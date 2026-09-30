"""Thin wrapper around the Anthropic SDK. All model calls go through `LLMService`."""

from collections.abc import AsyncIterator
from functools import lru_cache
from importlib.resources import files
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types.beta import BetaMessageParam

from app.config import Settings, get_settings

SYSTEM_PROMPT = files("app.prompts").joinpath("system.md").read_text(encoding="utf-8")


class RefusalError(Exception):
    """The model (and its fallback) declined the request."""


class LLMService:
    def __init__(self, client: AsyncAnthropic, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def _params(self, messages: list[BetaMessageParam]) -> dict[str, Any]:
        return {
            "model": self._settings.llm_model,
            "max_tokens": self._settings.llm_max_tokens,
            # Stable system prompt first + cache breakpoint -> repeated calls hit the prompt cache.
            "system": [
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            "messages": messages,
            "output_config": {"effort": self._settings.llm_effort},
            # On a safety refusal, the API re-runs the request on a suitable fallback model.
            "betas": ["server-side-fallback-2026-07-01"],
            "fallbacks": "default",
        }

    async def complete(self, messages: list[BetaMessageParam]) -> str:
        # Streaming under the hood avoids HTTP timeouts on long answers.
        async with self._client.beta.messages.stream(**self._params(messages)) as stream:
            response = await stream.get_final_message()
        if response.stop_reason == "refusal":
            raise RefusalError
        return "".join(block.text for block in response.content if block.type == "text")

    async def stream(self, messages: list[BetaMessageParam]) -> AsyncIterator[str]:
        async with self._client.beta.messages.stream(**self._params(messages)) as stream:
            async for text in stream.text_stream:
                yield text


@lru_cache
def get_llm() -> LLMService:
    # Credentials come from ANTHROPIC_API_KEY (or an `ant auth login` profile locally).
    return LLMService(AsyncAnthropic(), get_settings())
