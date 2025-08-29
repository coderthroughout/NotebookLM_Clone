# Contributing

Thanks for your interest in contributing! This repository contains:
- Frontend (React + Vite) under `Frontend/`
- Backend research modules (Python) under `research/`

## Getting Started
- Frontend: `cd Frontend && npm install && npm run dev`
- Backend: `python -m pip install -r requirements.txt`

## Branching & PRs
- Use feature branches: `feat/<area>-<short-desc>` or `fix/<issue>`
- Open PRs against `main` with a concise description and screenshots/logs

## Code Style
- TypeScript/React: 2-space indent, meaningful names, no unused imports
- Python: Pydantic models for contracts; add type hints; 2-space or 4-space consistent
- Keep functions small; avoid deep nesting; add brief docstrings for non-trivial logic

## Tests
- Add unit tests for utilities (URL normalization, scoring, extraction)
- Include smoke test instructions if adding CLI flags or flows

## Security & Keys
- Do not commit real API keys or secrets
- Use `.env` and `.env.example`

## Commit Messages
- Use imperative tense: "Add SerpAPI provider", "Fix extraction bug"

## Issue Reporting
- Include steps to reproduce, logs, environment (OS, Python/Node versions)

Thanks again for contributing!
