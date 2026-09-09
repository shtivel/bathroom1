w# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

This is a freshly scaffolded PyCharm project with effectively no code yet. As real code is added, expand this file with build/test/run commands and architecture notes.

## Environment

- Python 3.11 (CPython), managed via the in-repo virtualenv at `.venv/`.
- No third-party dependencies are installed yet, and there is no `requirements.txt`/`pyproject.toml`. Add one when introducing dependencies.
- Not a git repository yet.

## Commands

```bash
# Activate the virtualenv
source .venv/bin/activate

# Run the entry script
python src/starter.py

# Lint
ruff check src/          # report issues
ruff check --fix src/    # auto-fix

# Format
ruff format src/         # apply formatting
ruff format --check src/ # check only (CI)
```

Linting and formatting use **Ruff** (configured in `pyproject.toml`). There is no test or build setup configured yet.

**All changes must pass Ruff before being considered complete.** Ruff has two separate jobs, and BOTH must be run:

1. **Linter** — `ruff check src/` (catches bugs, unused imports, etc.). Use `ruff check --fix src/` to auto-fix.
2. **Formatter** — run `ruff format src/` to apply formatting (whitespace, spacing, indentation), then confirm with `ruff format --check src/`.

Note: the formatter, not the linter, is what enforces whitespace/spacing style. Neither tool touches whitespace *inside* string literals — that is intentional data. Resolve every reported issue: no new lint errors and no formatting diffs.

## Layout

- `src/` — application source. Currently only `starter.py`.
