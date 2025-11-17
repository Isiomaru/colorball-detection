# Repository Guidelines

## Project Structure & Module Organization
- `src/` holds the Python backend: `camera/`, `logic/`, `keymanager/`, and `server/` are the distinct threads/services that coordinate capture, scoring, keyboard input, and FastAPI/WebSocket delivery. `src/main.py` wires the subsystems together.
- `frontend/` contains the static UI (`index.html`, `app.js`, `style.css`) that connects to `server` via `/ws` and renders the 3x3 board.
- `config/` keeps JSON/YAML tuning files (`setting.json`, `map_data.json`, `score.json`, `colors.yaml`) so adjust camera indices, maps, and color thresholds without touching code.
- `README.md` documents usage; keep it synchronized with major architecture changes.

## Build, Test, and Development Commands
- `uv venv` (or `python -m venv .venv`) creates the Python virtual environment.
- `uv pip sync` installs pinned dependencies from `uv.lock`; fallback to `uv pip install -r requirements.txt` when the lock file is stale.
- `python -m src.main` starts the full stack (camera capture, logic, FastAPI server, WebSocket, browser UI). Verify http://localhost:8000 to confirm everything launches.
- Use `uv pip` for additional tooling installs so `uv.lock` stays authoritative.

## Coding Style & Naming Conventions
- Python code follows PEP 8: 4-space indentation, lowercase modules, descriptive class/function names, and short docstrings for complex logic. Run `python -m src.main` from repository root to exercise changes before committing.
- Front-end files maintain plain HTML/CSS/vanilla JS style; keep DOM IDs (`canvas`, `chart`) consistent with the existing scripts and avoid bundlers.
- Configuration files use snake_case keys (`camera_resolution`, `map_data`) and live in `config/`; mirror those names when referencing them from code.

## Testing Guidelines
- No automated test suite exists yet. Exercise the end-to-end flow by running `python -m src.main` and manually interacting with the browser UI (start/reset buttons, scoring animations).
- When adding logic, create targeted unit tests under a new `tests/` directory and document the naming convention (`test_<module>.py`). Aim to cover detector threshold updates and scoring calculations first.

## Commit & Pull Request Guidelines
- Keep commits concise and action-oriented (e.g., `server: add websocket health check`). The current history favors `<scope>: description`, but the imperative form is acceptable as long as the intent is clear.
- Pull requests should describe the purpose, highlight affected areas (`src/logic`, `frontend/app.js`, etc.), and mention manual verification steps (camera, WebSocket). Attach screenshots or recordings if UI changes appear.
