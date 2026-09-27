# AGENTS.md

## Project overview

This repository is a Flask-based requirements engineering app with AI-assisted requirement generation, project management, localization, and a lightweight dashboard feature module.

- Main application entry: [main.py](main.py)
- App factory and startup wiring: [app/**init**.py](app/__init__.py)
- Core models and persistence: [app/models.py](app/models.py)
- Route handlers: [app/routes.py](app/routes.py)
- Authentication flows: [app/auth.py](app/auth.py)
- AI generation logic: [app/agent.py](app/agent.py) and [app/services/ai_client.py](app/services/ai_client.py)
- Build/test docs: [README.md](README.md)
- Feature-module README: [app/features/README.md](app/features/README.md)

## Architecture and conventions

- Use the Flask app factory pattern via `create_app()` in [app/**init**.py](app/__init__.py). Do not rework the app into a separate bootstrap pattern unless required.
- Database is SQLite under the app instance folder (`instance/db.db`). Schema changes should use Alembic migrations under [migrations/](migrations/) and manual migration scripts under [archive/](archive/) only when needed.
- Templates live under [app/templates/](app/templates/) and static assets under [app/static/](app/static/). Keep Bootstrap 5 styling and HTML structure consistent with existing pages.
- Localization is handled through Flask-Babel; supported locales are defined in [app/**init**.py](app/__init__.py).
- AI behavior is configured via [config.py](config.py) and environment variables such as `OPENAI_API_KEY`, `OPENAI_MODEL`, `SYSTEM_PROMPT`, and `SYSTEM_PROMPT_PATH`.
- Do not hardcode secrets or API keys in source files.

## Working rules for agents

- Prefer the smallest change that solves the issue. Avoid broad refactors or unrelated cleanup in the same patch.
- When touching data models, also check whether a migration or schema update is needed.
- For UI work, follow the existing Bootstrap layout and template conventions rather than introducing a different frontend pattern.
- For feature-module development, keep the isolated submodule conventions in [app/features/README.md](app/features/README.md) in mind; the mock server in [app/features/run_test.py](app/features/run_test.py) exists to emulate the real app.
- Use the repository’s existing test structure and keep changes compatible with the current app factory setup.

## Verification and test commands

Run the smallest relevant command first:

- Smoke-check with pytest: `pytest tests/test_quick.py`
- Run a focused test file: `pytest tests/test_ai_agent.py`
- Run integration checks when AI behavior is involved: `pytest tests/test_integration.py`
- For a simple local app boot test: `python main.py`

Keep validation targeted; do not claim a fix is complete without running the relevant tests or boot check.

## Project-specific notes

- The app loads environment variables from a `.env` file in local development. For VS Code terminal setup, this is supported with the setting `python.terminal.useEnvFile`.
- The project includes both migration scripts and generated Alembic revisions. Prefer the Alembic pattern for normal schema evolution.
- The feature module under [app/features/](app/features/) is intentionally isolated and should respect the module contract described in [app/features/README.md](app/features/README.md).

## Helpful references

- [README.md](README.md)
- [app/features/README.md](app/features/README.md)
- [tests/test_ai_agent.py](tests/test_ai_agent.py)
- [tests/test_integration.py](tests/test_integration.py)
- [config.py](config.py)
