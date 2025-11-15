Objetivo: mover funcionalidades con paridad funcional y tests.
Comienza con: auth (login, me, logout) → luego solicitudes (CRUD, estados) → luego planner (adapter).

Primero:
auth
Es el corazón del sistema: login, me, roles, JWT.
Todo lo demás depende de que esto esté limpio.

Después:
solicitudes
Es el flujo principal de negocio.
Ya tendremos auth v2, entonces todo lo que use /auth/me se puede adaptar.

Luego:
planner
Integra el módulo src/planner/ con el backend_v2.
Ahí usarás bien los algoritmos.


Más adelante los módulos: notificaciones, admin, presupuestos, etc.