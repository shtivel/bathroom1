# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

**Bathroom Grader** — rate and discover gas station bathrooms around Israel. Backend is a FastAPI +
PostgreSQL service (`src/bathroom_grader/`); client side hasn't been started yet.

## Environment

- Python 3.11 (CPython), managed via the in-repo virtualenv at `.venv/`.
- Dependencies declared in `pyproject.toml` (`[project.dependencies]` / `[project.optional-dependencies].dev`).
- PostgreSQL (via Homebrew, `postgresql@14`), database name `bathroom_grader`.

## Commands

```bash
# Activate the virtualenv
source .venv/bin/activate

# Install/update dependencies (including dev deps: pytest, httpx)
pip install -e ".[dev]"

# Make sure Postgres is running, and the dev DB exists (one-time)
brew services start postgresql@14
createdb bathroom_grader

# Run the API locally (reloads on code changes)
uvicorn bathroom_grader.main:app --reload
# -> API at http://localhost:8000, interactive docs at http://localhost:8000/docs

# Run tests (uses an isolated in-memory SQLite DB, never touches the real Postgres DB)
pytest

# Lint
ruff check src/ tests/          # report issues
ruff check --fix src/ tests/    # auto-fix

# Format
ruff format src/ tests/          # apply formatting
ruff format --check src/ tests/  # check only (CI)
```

Linting and formatting use **Ruff** (configured in `pyproject.toml`). Testing uses **pytest**.

**All changes must pass Ruff before being considered complete.** Ruff has two separate jobs, and BOTH must be run:

1. **Linter** — `ruff check src/ tests/` (catches bugs, unused imports, etc.). Use `ruff check --fix src/ tests/` to auto-fix.
2. **Formatter** — run `ruff format src/ tests/` to apply formatting (whitespace, spacing, indentation), then confirm with `ruff format --check src/ tests/`.

Note: the formatter, not the linter, is what enforces whitespace/spacing style. Neither tool touches whitespace *inside* string literals — that is intentional data. Resolve every reported issue: no new lint errors and no formatting diffs.

New code should also come with tests in `tests/` — run `pytest` before considering a change complete.

## Layout

- `src/starter.py` — leftover scaffold entry point, not part of the real app.
- `src/bathroom_grader/` — the FastAPI backend.
  - `main.py` — FastAPI app, route registration, `/health` endpoint.
  - `config.py` — settings (e.g. `DATABASE_URL`), loaded via `pydantic-settings`.
  - `database.py` — SQLAlchemy/SQLModel engine + `get_session` dependency.
  - `models.py` — SQLModel table models: `GasStation`, `Review`, and the `BathroomType` enum
    (women/men/unisex_or_family/accessible/other — reviews are tagged by which bathroom they're
    about, so ratings for different bathrooms at one station don't blend together).
  - `schemas.py` — Pydantic request/response shapes (`*Create` for input, `*Read`/`*WithStats` for
    output) — kept separate from the table models in `models.py` on purpose, since what a client
    sends often isn't the same shape as what we send back.
  - `routers/stations.py`, `routers/reviews.py` — the actual API endpoints.
- `tests/` — pytest suite; `conftest.py` overrides the DB dependency with an isolated in-memory
  SQLite DB per test, so running tests never touches the real Postgres DB.

## Known gaps / next steps

- Tables are created on startup directly from the models (`SQLModel.metadata.create_all`) — fine
  for now, but should move to **Alembic migrations** once the schema needs tracked, incremental changes.
- No client/frontend yet.
