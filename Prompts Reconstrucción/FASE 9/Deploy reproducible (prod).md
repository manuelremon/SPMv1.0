Objetivo: levantar stack de prod contenedorizado.

Criterios

Dockerfile backend (gunicorn) y frontend (nginx).

infra/docker-compose.prod.yml.

infra/nginx.conf (SPA + proxy /api).

Healthchecks y logs.


Crea:
- backend_v2/Dockerfile (python:3.12-slim + gunicorn 0.0.0.0:8000).
- frontend_v2/Dockerfile (multi-stage vite build + nginx).
- infra/docker-compose.prod.yml (nginx reverse-proxy, backend, frontend, postgres).
- infra/nginx.conf (serve SPA; proxy_pass /api a backend; cache estáticos; gzip; health).

Incluye variables mínimas y README de despliegue.
