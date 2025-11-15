Objetivo: cerrar huecos señalados en el informe.

Criterios

CSRF aplicado a mutaciones (POST/PUT/PATCH/DELETE) con token en header.

JWT con expiración y rotación si aplicara.

CORS limitado a FRONTEND_ORIGIN.

Rate limit en rutas sensibles (auth/solicitudes mutadoras).


Endurece seguridad en backend_v2:

1) CSRF:
   - Genera token firmado por request (itsdangerous).
   - Cookie HttpOnly con ID de sesión; header X-CSRF-Token con token.
   - Verifica en mutaciones; excluye /auth/login y /health.

2) JWT:
   - HS256, TTL desde entorno; clock skew tolerante; error handling claro.
   - Decorator @auth_required en todas las rutas que lo requieran.

3) CORS:
   - Solo FRONTEND_ORIGIN desde entorno; métodos/headers mínimos; credenciales true.

4) Rate limiting:
   - rate limiter sencillo en memoria (token bucket) por IP/usuario para /auth/* y mutaciones de solicitudes.

Devuelve:
- Código nuevo y modificaciones.
- .env.example actualizado.
- Tests de seguridad (CSRF error, JWT expirado).
