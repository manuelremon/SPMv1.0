Objetivo: fijar decisiones (API pura, SPA, planner por interfaz, Postgres futuro).

Criterios

docs/adr/001-architecture.md creado.

Contrato de planner definido (puertos/funciones).


Crea docs/adr/001-architecture.md con:
- Contexto v1 (Flask+SQLite+Vite acoplado) y problemas (seguridad, acoplamiento, SQLite).
- Decisión: monorepo con backend_v2 (API REST), frontend_v2 (SPA), planner acoplado por interfaz, Postgres en prod.
- Alternativas descartadas y por qué (seguir SQLite, mantener server-side HTML).
- Consecuencias: mayor claridad, mejores tests/CI/CD, migración de datos.
- Roadmap por fases (esta guía).