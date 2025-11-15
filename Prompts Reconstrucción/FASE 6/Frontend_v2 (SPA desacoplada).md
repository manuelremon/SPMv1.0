Objetivo: SPA con rutas, guard de auth, cliente API con credenciales.

Criterios

frontend_v2 con Vite y routing.

API client con fetch y credentials:'include'.

Páginas: Login, Dashboard, Solicitudes.

Tests básicos (Jest/Vitest).


Crear frontend_v2 con Vite (JS o TS) y:
- src/services/api.js: baseURL desde env, fetch con credentials: "include", manejo 401/CSRF.
- src/store/session.js: estado de sesión, acciones login/logout/me.
- src/pages/{Login.jsx,Dashboard.jsx,Solicitudes.jsx}
- src/router.js: rutas privadas con guard.
- .env.example con VITE_API_BASE.

Añade scripts en package.json: dev/build/preview/test.
Incluye tests mínimos para api.js y guard.
