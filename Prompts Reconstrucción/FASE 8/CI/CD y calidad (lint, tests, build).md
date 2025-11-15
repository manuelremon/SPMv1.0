Objetivo: PRs bloqueadas si falla lint/test; build reproducible.

Criterios

.github/workflows/ci.yml: jobs backend (pytest+cov) y frontend (jest/vitest).

Badges en README.

Pre-commit/husky.



Genera .github/workflows/ci.yml con:
- Job backend: setup-python, pip/poetry, pytest con coverage, upload artifacts.
- Job frontend: setup-node, npm ci, lint, test, build.
- Cache de dependencias y matrices mínimas (py311, node20).

Crea backend_v2/.pre-commit-config.yaml (black, isort, ruff).
Crea frontend_v2 husky + lint-staged.

Devuelve archivos y scripts de instalación de hooks.
