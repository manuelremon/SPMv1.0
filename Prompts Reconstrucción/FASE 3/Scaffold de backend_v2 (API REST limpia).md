Objetivo: levantar esqueleto funcional con health, auth básico, estructura modular.

Criterios

backend_v2 con app factory.

Endpoints /health, /ready.

JWT manager, CORS, rate limit esqueleto.

Tests de humo pytest verdes.


Crear carpeta backend_v2 con:
- app.py: create_app(config); registra blueprints; CORS.
- core/config.py: clases Config (Dev/Test/Prod) con lectura de entorno; JWT, DB_URL.
- core/db.py: SQLAlchemy Session/engine (aunque v1 use SQLite, prepara para Postgres).
- core/jwt_manager.py: issue/verify con HS256; TTL configurable; cookies HttpOnly.
- core/security.py: CSRF helper (token firmado) y rate-limiter placeholder.
- routes/health.py: GET /health y /ready.
- routes/auth.py: POST /auth/login, GET /auth/me (stub), decorator @auth_required.
- services/auth_service.py: authenticate_user(username, password) (stub).
- tests/test_health.py: prueba de /health.
- pyproject.toml con deps: flask, itsdangerous, python-dotenv, pydantic, sqlalchemy, pytest, flask-cors.

Entregables:
- Contenido completo de cada archivo.
- Comandos para ejecutar tests (pytest -q) y dev server (flask --app app run).