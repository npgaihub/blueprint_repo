# KI Labs Blueprint

Vorlage für neue KI-Labs-Projekte: ein FastAPI-Service, der Claude über das offizielle
Anthropic SDK nutzt – mit Tests, Evals, CI und Deployment auf Vercel.

Neues Projekt starten: Repo als Template nutzen (GitHub → *Use this template*), dann die
Punkte unter [Anpassen](#anpassen) durchgehen.

## Was drin ist

| Bereich | Tooling |
| --- | --- |
| API | FastAPI, `POST /chat`, `POST /chat/stream`, `GET /health` |
| LLM | `anthropic` SDK, Claude Opus 5.5, Prompt-Caching, automatischer Refusal-Fallback |
| Python-Tooling | uv, ruff (Lint + Format), mypy (strict), pytest |
| Qualität | pre-commit, GitHub Actions CI, Dependabot |
| Evals | `evals/cases.jsonl` + Runner gegen das echte Modell |
| Deployment | Vercel (Preview pro PR, Production bei Merge auf `main`) |
| KI-Agenten | `AGENTS.md` / `CLAUDE.md`, `.claude/settings.json` |

## Schnellstart

Voraussetzung: [uv](https://docs.astral.sh/uv/) (installiert bei Bedarf auch Python 3.12).

```bash
uv sync
uv run pre-commit install
cp .env.example .env   # ANTHROPIC_API_KEY eintragen
uv run uvicorn app.main:app --reload
```

Testen:

```bash
curl -N localhost:8000/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages": [{"role": "user", "content": "Hallo!"}]}'
```

Ist `APP_API_KEY` gesetzt, muss jeder Request den Header `X-API-Key: <wert>` mitschicken.
Interaktive API-Doku: <http://localhost:8000/docs>.

## Entwicklung

```bash
uv run pytest                 # Tests (ohne echte API-Calls)
uv run ruff check --fix .     # Lint
uv run ruff format .          # Format
uv run mypy                   # Typen
uv run python evals/run.py    # Evals – kostet echte API-Tokens
```

Abhängigkeiten immer mit `uv add <paket>` (bzw. `uv add --dev`) hinzufügen und `uv.lock`
mitcommitten.

### Struktur

```
src/app/
  main.py          HTTP-Routen + API-Key-Check
  llm.py           LLMService – alle Claude-Aufrufe
  config.py        Settings aus Env-Variablen
  prompts/         System-Prompts als Markdown
api/index.py       Vercel-Entrypoint
tests/             pytest (FakeLLM statt echter API)
evals/             Eval-Fälle + Runner
```

## Konfiguration

| Variable | Default | Beschreibung |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | – | API-Key für Claude (Pflicht) |
| `APP_API_KEY` | leer | Shared Secret für `X-API-Key`; leer = keine Auth (nur lokal!) |
| `LLM_MODEL` | `claude-opus-5-5` | Modell-ID |
| `LLM_EFFORT` | `medium` | `low` / `medium` / `high` / `xhigh` / `max` |
| `LLM_MAX_TOKENS` | `16000` | Maximale Antwortlänge |

## Deployment auf Vercel

Einmalig pro Projekt:

1. Vercel-Projekt anlegen: `npx vercel link` im Repo (legt `.vercel/project.json` an, wird nicht
   committet). Daraus `orgId` und `projectId` ablesen.
2. In Vercel unter *Settings → Environment Variables* `ANTHROPIC_API_KEY` und `APP_API_KEY` für
   Preview und Production setzen.
3. In Vercel unter *Settings → Git* die automatischen Deployments deaktivieren – das übernimmt
   GitHub Actions, damit nur deployt wird, wenn die CI grün ist.
4. In GitHub unter *Settings → Secrets and variables → Actions* anlegen:
   `VERCEL_TOKEN` (Vercel → Account Settings → Tokens), `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.

Danach erzeugt jeder PR ein Preview-Deployment (URL in der Job-Summary), jeder Merge auf `main`
ein Production-Deployment. Ohne `APP_API_KEY` ist der Endpoint öffentlich und verbraucht
API-Guthaben – deshalb in Vercel immer setzen.

## Arbeiten mit KI-Agenten

`AGENTS.md` enthält Befehle, Struktur und Konventionen für Coding-Agenten; `CLAUDE.md` importiert
sie für Claude Code. `.claude/settings.json` erlaubt die üblichen Prüfbefehle ohne Nachfrage,
fragt vor Evals und Vercel-Befehlen nach und sperrt das Lesen von `.env`.

Grundregel: KI-generierter Code wird von einem Menschen gelesen und verstanden, bevor er
gemergt wird (siehe PR-Template).

## Anpassen

- [ ] `name` / `description` in `pyproject.toml`
- [ ] System-Prompt in `src/app/prompts/system.md`
- [ ] Routen und Modelle in `src/app/main.py`
- [ ] Eval-Fälle in `evals/cases.jsonl` für den eigenen Use Case
- [ ] Vercel-Setup (siehe oben)
- [ ] Diese README
