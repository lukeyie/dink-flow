# dink-flow

Lightweight bot to auto-register for DinkUp events near Songshan (松山). It polls the DinkUp API for upcoming events and attempts registrations according to configurable priorities.

## Features
- Polls events for target dates and filters by location keywords (e.g., 松).
- Selects divisions according to `DIVISION_PRIORITY` (configurable). Current default: `fun` only.
- Supports fallback: if a preferred division is explicitly rejected, optionally attempt a fallback division (e.g., `competitive` -> `fun`).
- Safe test mode: tests mock network calls to avoid real POSTs.
- Test layering: `unit` tests (fast, isolated) and `integration` tests (multi-threaded, full behavior).

## Quickstart
Prerequisites: Python 3.11, pipenv (optional)

Install dependencies (pipenv):

```bash
python -m pip install pipenv
pipenv sync
pipenv run playwright install chromium
```

Run the bot locally (interactive auth):

```bash
pipenv run python save_session.py  # opens browser to save auth.json
pipenv run python dinkup_bot.py
```

Run tests:

```bash
# unit tests (fast)
python run_tests.py unit

# all tests
python -m unittest discover -v
```

## File Layout
- `dinkup_bot.py` — main bot logic
- `save_session.py` — interactive helper to capture Playwright storage state
- `tests/` — unit and integration tests
  - `tests/test_select_fun_simple.py` — unit: selection logic
  - `tests/test_fallback_behavior.py` — unit: fallback behavior
  - `tests/test_dinkup_bot.py` — end-to-end behavior (mocked network)
- `run_tests.py` — helper to run layered tests

## Project Structure & Module Organization

This repository is a Python 3.11 DinkUp registration bot with two root-level scripts:

- `dinkup_bot.py` loads authentication, waits until noon, fetches events six days ahead, filters locations and available `fun` divisions, and submits registrations.
- `save_session.py` opens an interactive Chrome session and saves login state to `auth.json`.
- `.github/workflows/schedule-run.yml` schedules execution; `dry-run.yml` provides manual execution.
- `Pipfile` and `Pipfile.lock` define and lock Requests and Playwright dependencies.

There are currently no dedicated source-package, test, or asset directories.

## Coding Style
- Language: Python 3.11
- Indentation: 4 spaces
- Naming: `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants
- Keep functions small and single-responsibility; extract helpers for repeated test setup
- Tests: prefer small, fast unit tests using mocks; put integration tests that exercise concurrency and time-based logic separately

## Coding Style & Naming Conventions (detailed)

- Use four-space indentation.
- Use `snake_case` for functions and variables, and `UPPER_SNAKE_CASE` for configuration constants.
- Preserve UTF-8 Chinese comments and log messages where present.
- Keep request timeouts explicit and retry counts bounded; avoid hidden long sleeps in code paths used by tests.
- No formatter or linter is configured in the repo; if you add one, update the README accordingly.
- When changing dependencies, update `Pipfile.lock` alongside `Pipfile`.

## Testing Strategy / CI
- Run `unit` tests on each PR/job (fast). Keep them strictly mocked and isolated.
- Avoid sending real POST requests in CI — keep `AUTH_JSON_CONTENT` secret-only and tests must mock `requests.Session`.

## Build, Test, and Development Commands (detailed)

Run commands from the repository root with Python 3.11 installed:

- `python -m pip install pipenv` — install the environment manager.
- `pipenv sync` — install locked dependencies.
- `pipenv run playwright install chromium` — install the bot's browser; Linux runners use `--with-deps` for system dependencies.
- `pipenv run python save_session.py` — capture authentication interactively; requires Google Chrome installed locally.
- `pipenv run python dinkup_bot.py` — execute the live registration flow.
- `pipenv run python -m py_compile dinkup_bot.py save_session.py` — check syntax without executing either script.

There is no build step.

## Testing Guidelines (detailed)

- No automated test coverage threshold is configured. Run the syntax check before submitting changes.
- For new tests, follow the `tests/test_*.py` pattern and mock HTTP requests, browser authentication, and clock delays.
- Cover location filtering, division availability, retries, and registration payloads.
- Note: `dry-run.yml` in workflows may submit real registrations despite its name — do not use it as a standalone test suite.

## Commit & Pull Request Guidelines

- Use conventional short prefixes such as `feat:`, `fix:`, or concise summaries in commit messages.
- PR descriptions should explain behavior changes, validation performed, related issues, and any scheduling or registration impact.

## Security & Configuration

- Never commit authentication cookies or session contents. `auth.json` is ignored; CI uses the `AUTH_JSON_CONTENT` secret, which takes precedence over the local file.
- Workflows set `TZ=Asia/Taipei`; local execution uses the system clock. GitHub cron expressions use UTC.

## Fallback Behavior
- `select_registrations()` may attach a `fallback` field when a competitive selection has an available fun division.
- `register_once()` will attempt the primary division first; if explicitly rejected and `can_fallback_after_rejection()` returns True, it will attempt the fallback once.
- To disable fallback entirely, set `DIVISION_PRIORITY` to avoid `competitive` being chosen, or remove fallback handling from `register_once()`.

## Contributing
- Run unit tests before creating a PR: `python run_tests.py unit`.
- For behavior changes that affect selection policy, add or update unit tests under `tests/` and update integration expectations.

## Security
- Never commit `auth.json`. Use `AUTH_JSON_CONTENT` secrets in CI.

## Next Steps
- (Optional) Add a GitHub Actions workflow to run `unit` on PRs and `integration` nightly.
- (Optional) Add `pre-commit` hooks for formatting and linting.

---
If you'd prefer an `AGENTS.md`-style document instead, I can produce that format instead of `README.md`—tell me which you'd like.
