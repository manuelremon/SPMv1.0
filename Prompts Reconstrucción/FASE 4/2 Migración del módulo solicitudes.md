Migración de módulo: solicitudes

1) Localiza en v1 archivos y dependencias del módulo solicitudes:
   - Rutas para crear, listar, actualizar, cancelar, aprobar/rechazar solicitudes.
   - Servicios o helpers que implementen estados de solicitud y validaciones.
   - Modelos y schemas relacionados a solicitudes y sus items.
   - Cualquier export (Excel/PDF) que dependa de solicitudes.

2) Diseña modelos (SQLAlchemy) y schemas (Pydantic) para v2 en backend_v2:
   - models/solicitud.py (incluye estados, timestamps, relaciones con usuario).
   - schemas/solicitud_schema.py (payloads de entrada/salida).

3) Implementa services/solicitud_service.py:
   - crear_borrador, actualizar_borrador, finalizar_solicitud,
     aprobar/rechazar, cancelar, listar por filtros, export helper.

4) Implementa routes/solicitud_routes.py:
   - siguiendo las rutas de v1, pero limpias:
     - GET /solicitudes
     - GET /solicitudes/<id>
     - POST /solicitudes
     - PATCH /solicitudes/<id>/draft
     - POST /solicitudes/<id>/decidir
     - etc.
   - Aplica el decorador @auth_required de backend_v2.core.security.

5) Añade tests en backend_v2/tests/test_solicitudes_*.py:
   - tests unitarios sobre el service.
   - tests de integración sobre las rutas con una DB SQLite en memoria.

6) Proporciona diffs completos y deja claro si hay diferencias de comportamiento respecto de v1.
