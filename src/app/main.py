import logging
import secrets
from typing import Annotated, Literal

import anthropic
from anthropic.types.beta import BetaMessageParam
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.llm import LLMService, RefusalError, get_llm

logger = logging.getLogger(__name__)

app = FastAPI(title="KI Labs Blueprint")


@app.exception_handler(anthropic.APIError)
async def llm_error(_: Request, exc: anthropic.APIError) -> JSONResponse:
    logger.exception("LLM request failed", exc_info=exc)
    return JSONResponse({"detail": "LLM request failed"}, status_code=status.HTTP_502_BAD_GATEWAY)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)

    def to_params(self) -> list[BetaMessageParam]:
        return [{"role": m.role, "content": m.content} for m in self.messages]


class ChatResponse(BaseModel):
    answer: str


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str, Header()] = "",
) -> None:
    expected = settings.app_api_key.get_secret_value()
    if expected and not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")


Llm = Annotated[LLMService, Depends(get_llm)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", dependencies=[Depends(require_api_key)])
async def chat(request: ChatRequest, llm: Llm) -> ChatResponse:
    try:
        answer = await llm.complete(request.to_params())
    except RefusalError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Request declined") from None
    return ChatResponse(answer=answer)


@app.post("/chat/stream", dependencies=[Depends(require_api_key)])
async def chat_stream(request: ChatRequest, llm: Llm) -> StreamingResponse:
    return StreamingResponse(
        llm.stream(request.to_params()), media_type="text/plain; charset=utf-8"
    )
