# Repository Guidelines

## Project Scope
エージェントは常に日本語で丁寧に回答してください。詳細な実装方針は `PLAN.md` を参照してください。
This project builds a CLI that pulls YouTube transcripts (or transcribes audio when none exist), summarizes them, and writes Obsidian-ready Markdown notes. 

## Project Structure & Module Organization
- `src/youtube2obsidian/`: CLI entrypoint plus modules for transcript fetch (YouTube + `yt-dlp` fallback), transcription (Whisper/faster-whisper), summarization, formatting, and Obsidian writer.
- `scripts/`: developer utilities such as sample runs, cache cleanup, or folder-watcher helpers.
- `tests/`: pytest suites for each module and CLI integration smoke tests.
- `data/cache/` (gitignored): downloaded audio, Whisper models, or temporary transcripts; keep vault paths out of git.
- `.env.example`: documents required environment variables (API keys, vault hints); never commit real secrets.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -e ".[dev]"` — installs core deps and lint/test tooling once `pyproject.toml` is in place.
- `python -m youtube2obsidian.cli https://youtu.be/<id> --vault ~/Obsidian/Vault --model openai:gpt-4o` — run the full pipeline locally.
- `pytest -q` — run unit and integration suites.
- `ruff check .` / `ruff format .` — lint and format; format before commits.
- `mypy src` — optional but encouraged on public interfaces.

## Coding Style & Naming Conventions
- Target Python 3.11+, PEP 8 aligned; snake_case for functions/vars, PascalCase for classes, kebab-case for CLI flags.
- Require type hints and docstrings on public functions; prefer `TypedDict`/`dataclass` for structured payloads.
- Use `logging` for diagnostics; avoid bare `print`.
- Keep modules single-purpose (fetch, transcribe, summarize, write) to ease testing and maintenance.

## Testing Guidelines
- Use pytest with files named `test_*.py`; mirror module paths (e.g., `tests/test_summary.py` for `summary.py`).
- Stub network/LLM calls; use cached sample transcripts/audio for deterministic tests.
- Add an integration test that exercises the CLI on a short fixture video/transcript.

## Commit & Pull Request Guidelines
- History is new; follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`, `ci:`).
- Keep PRs small with a clear summary, linked issue, and notes on model/API usage or cost-impacting changes.
- Run lint and tests before opening; include output when changing pipelines.
- Never commit secrets, local vault content, or large audio artifacts; prefer `.gitignore` entries for caches and vault paths.
