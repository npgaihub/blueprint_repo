from app.config import Settings
from app.llm import SYSTEM_PROMPT, LLMService


def test_params_cache_system_prompt_and_use_settings() -> None:
    llm = LLMService(client=None, settings=Settings(llm_model="claude-sonnet-5-5"))  # type: ignore[arg-type]

    params = llm._params([{"role": "user", "content": "Hi"}])

    assert params["model"] == "claude-sonnet-5-5"
    assert params["system"][0]["text"] == SYSTEM_PROMPT
    assert params["system"][0]["cache_control"] == {"type": "ephemeral"}
