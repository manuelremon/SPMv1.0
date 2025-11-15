Migración de módulo: auth

1) Localiza en v1 archivos y dependencias del módulo auth.
   - Rutas de autenticación (login, logout, me, refresh).
   - Servicios de autenticación (validación de usuario, hashing, emisión de tokens).
   - Decoradores/middleware relacionados (auth_required, roles, etc.).
   - Cualquier esquema Pydantic o modelo que represente al usuario.

2) Diseña modelos (SQLAlchemy) y schemas (Pydantic) para v2 en backend_v2:
   - models/user.py
   - schemas/user_schema.py

3) Implementa services/auth_service.py en backend_v2 con la lógica de negocio:
   - authenticate_user(username, password)
   - get_user_by_id / get_user_by_username
   - funciones auxiliares para roles/permisos básicos.

4) Implementa routes/auth_routes.py (o reutiliza routes/auth.py pero refactorizado) con:
   - POST /auth/login
   - POST /auth/logout
   - GET /auth/me
   - (Opcional) POST /auth/refresh si aplica

5) Añade tests unitarios y de integración en backend_v2/tests para auth:
   - login OK y KO
   - /auth/me con token válido, sin token, token inválido o expirado.

6) Genera diffs completos de cada archivo nuevo/modificado y respeta la estructura ya creada de backend_v2.

No toques aún la lógica de solicitudes ni planner; solo auth.


