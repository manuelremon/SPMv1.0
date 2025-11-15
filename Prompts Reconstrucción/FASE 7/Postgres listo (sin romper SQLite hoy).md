Objetivo: preparar migración y que dev/prod usen motores distintos.

Criterios

infra/docker-compose.dev.yml: backend_v2 + frontend_v2 + postgres.

backend_v2/core/db.py soporta sqlite:// y postgresql+psycopg://.

Scripts export/import (v1→v2).



Prepara Postgres para v2:

1) core/db.py: soportar ambas URLs (SQLite y Postgres) con SQLAlchemy 2.x.
2) infra/docker-compose.dev.yml: 
   - backend_v2 (8000), frontend_v2 (3000), postgres (5432), healthchecks.
3) Scripts:
   - scripts/migration/export_sqlite_v1.py: exporta entidades clave a CSV/JSON.
   - scripts/migration/import_postgres_v2.py: importa a Postgres con validaciones.

Devuelve:
- archivos completos,
- variables en .env.example (POSTGRES_*),
- pasos para levantar compose y probar /health.
