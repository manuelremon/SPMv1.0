Objetivo: ejecutar migración y corte con seguridad.

Criterios

docs/runbook_cutover.md con pasos y rollback.

Scripts de verificación (conteos, smoke tests).


Crea docs/runbook_cutover.md:
- Congelar escritura v1.
- Backup SQLite.
- Export → Import Postgres v2.
- Alembic upgrade head.
- Smoke tests (login, CRUD solicitud, planner optimize).
- Monitoreo 24–48h.
- Plan de rollback claro.

Incluye script scripts/checks/smoke.sh con curl a endpoints críticos.