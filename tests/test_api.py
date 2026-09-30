import anthropic
import httpx2
from fastapi.testclient import TestClient

from app.llm import RefusalError
from tests.conftest import FakeLLM

AUTH = {"X-API-Key": "secret"}
BODY = {"messages": [{"role": "user", "content": "Hi"}]}


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_requires_api_key(client: TestClient) -> None:
    assert client.post("/chat", json=BODY).status_code == 401
    assert client.post("/chat", json=BODY, headers={"X-API-Key": "wrong"}).status_code == 401


def test_chat(client: TestClient, fake_llm: FakeLLM) -> None:
    response = client.post("/chat", json=BODY, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"answer": "Hallo!"}
    assert fake_llm.calls == [[{"role": "user", "content": "Hi"}]]


def test_chat_stream(client: TestClient) -> None:
    response = client.post("/chat/stream", json=BODY, headers=AUTH)

    assert response.status_code == 200
    assert response.text == "Hallo!"


def test_chat_rejects_empty_messages(client: TestClient) -> None:
    assert client.post("/chat", json={"messages": []}, headers=AUTH).status_code == 422


def test_chat_refusal(client: TestClient, fake_llm: FakeLLM) -> None:
    fake_llm.error = RefusalError()

    assert client.post("/chat", json=BODY, headers=AUTH).status_code == 422


def test_chat_upstream_error(client: TestClient, fake_llm: FakeLLM) -> None:
    fake_llm.error = anthropic.APIConnectionError(request=httpx2.Request("POST", "https://x"))

    response = client.post("/chat", json=BODY, headers=AUTH)

    assert response.status_code == 502
    assert response.json() == {"detail": "LLM request failed"}
