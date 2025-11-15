Migración de módulo: planner

1) Localiza en v1 toda la superficie del módulo planificador/planner:
   - Rutas: planner_routes.py, planificador.py, endpoints /api/planner/*, /api/queue, etc.
   - Módulo src/planner/ (algoritmos, decision_tree, optimization, scoring, etc).
   - Servicios que consumen esos algoritmos.

2) Define en backend_v2 un adapter claro en services/planner_adapter.py que:
   - expone funciones de alto nivel:
     - get_planner_dashboard(user)
     - get_planner_queue(filtros)
     - optimize_solicitud(solicitud_id)
   - por dentro llama a los módulos de src/planner/ (no dupliques lógica).

3) Implementa routes/planner_routes.py en backend_v2:
   - GET /planner/dashboard
   - GET /planner/solicitudes
   - GET /planner/solicitudes/<id>
   - POST /planner/solicitudes/<id>/optimize
   - protege con @auth_required y, si aplica, control de rol (role planner).

4) Añade tests en backend_v2/tests/test_planner_*.py:
   - tests de integración sobre endpoints.
   - tests unitarios del adapter con mocks de los algoritmos.

5) Genera diffs y documenta cualquier cambio de interfaz respecto de v1.
