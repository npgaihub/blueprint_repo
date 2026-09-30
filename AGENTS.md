# AGENTS.md

Anweisungen für KI-Coding-Agenten (Claude Code, Codex, Cursor, …) in diesem Repo.
`CLAUDE.md` importiert diese Datei – Änderungen nur hier vornehmen.

## Projekt

KI-Labs-Blueprint: FastAPI-Service, der Claude über das offizielle Anthropic Python SDK anspricht
und auf Vercel deployt wird. Python 3.12, Paketmanager **uv**.

## Befehle

- Setup: `uv sync` und `uv run pre-commit install`
- Dev-Server: `uv run uvicorn app.main:app --reload`
- Tests: `uv run pytest`
- Lint/Format: `uv run ruff check --fix . && uv run ruff format .`
- Typen: `uv run mypy`
- Evals (kostet echte API-Tokens, nur auf Nachfrage): `uv run python evals/run.py`

Vor jedem Commit müssen Lint, Format, mypy und Tests grün sein – genau das prüft die CI.

## Struktur

- `src/app/main.py` – HTTP-Routen, Request/Response-Modelle, API-Key-Check
- `src/app/llm.py` – `LLMService`: **alle** Modellaufrufe laufen hier durch
- `src/app/config.py` – Settings aus Env-Variablen (pydantic-settings)
- `src/app/prompts/` – System-Prompts als Markdown-Dateien, nicht als Strings im Code
- `api/index.py` – Vercel-Entrypoint (nur Import, keine Logik)
- `tests/` – pytest; `FakeLLM` in `conftest.py` ersetzt echte API-Calls
- `evals/` – Eval-Fälle (`cases.jsonl`) und Runner gegen das echte Modell

## Konventionen

- Abhängigkeiten nur mit `uv add` / `uv add --dev`, nie `pip install`; `uv.lock` mitcommitten.
- Tests rufen nie die echte Anthropic-API auf – `get_llm` per `dependency_overrides` ersetzen.
- Neue Env-Variablen: in `Settings`, in `.env.example` und im README dokumentieren.
- Keine Secrets, Kundendaten oder personenbezogenen Daten in Code, Prompts, Tests oder Logs.
- Code-Kommentare und Bezeichner auf Englisch, Doku auf Deutsch.

## LLM-Konventionen

- Offizielles `anthropic` SDK verwenden, keine Raw-HTTP-Calls oder OpenAI-kompatiblen Shims.
- Standardmodell `claude-opus-5-5` (über `LLM_MODEL` änderbar). Modell-IDs exakt so schreiben,
  ohne Datums-Suffix.
- Denktiefe über `output_config.effort` steuern; bei Opus 5.5 lässt sich Thinking nicht abschalten,
  `budget_tokens` und `temperature` werden abgelehnt.
- Immer `stop_reason` prüfen, bevor `content` gelesen wird (`"refusal"` → `RefusalError`).
- Prompt-Caching: System-Prompt stabil halten (keine Zeitstempel/IDs darin), variable Inhalte
  gehören in `messages`.
- Prompt- oder Modelländerungen gegen die Evals prüfen und im PR erwähnen.
