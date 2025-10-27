# 📈 Módulo Planificador - Diagrama de Flujo

## Arquitectura General del Módulo

```
┌──────────────────────────────────────────────────────────────┐
│                   APLICACIÓN SPM                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    FRONTEND (5173)                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  home.html                    planificador.html         │ │
│  │  ┌────────────────┐          ┌──────────────────┐      │ │
│  │  │ Menú Lateral   │          │ Dashboard        │      │ │
│  │  │ ┌────────────┐ │   Link   │ ┌──────────────┐│      │ │
│  │  │ │ Dashboard  │ │  ───────→│ │ Estadísticas ││      │ │
│  │  │ │ Solicitudes│ │          │ └──────────────┘│      │ │
│  │  │ │ Crear      │ │          │                │      │ │
│  │  │ │ Notif.     │ │          │ Tabla:        │      │ │
│  │  │ │ Planificac.│◄┤  if Rol  │ ┌──────────────┐│      │ │
│  │  │ │ (si rol OK)│ │          │ │ ID│Centro    ││      │ │
│  │  │ │ Preferencias│ │          │ │ Sector│Criti││      │ │
│  │  │ │ Ayuda      │ │          │ │ Items│Monto ││      │ │
│  │  │ └────────────┘ │          │ └──────────────┘│      │ │
│  │  └────────────────┘          │                │      │ │
│  │         ▲                    │ Panel Detalles:│      │ │
│  │         │                    │ ┌──────────────┐│      │ │
│  │         │ setupUserMenu()    │ │ Info General ││      │ │
│  │         │ - Obtener rol      │ │ Materiales   ││      │ │
│  │         │ - Mostrar section  │ │ Análisis     ││      │ │
│  │         │   si rol OK        │ └──────────────┘│      │ │
│  │         │                    │                │      │ │
│  │  planificador.js             │ planificador.js│      │ │
│  │  ┌────────────────────────┐  └──────────────────┘      │ │
│  │  │ checkAccess()          │                           │ │
│  │  │ └─ Valida rol          │                           │ │
│  │  │ └─ Si no OK→redirect   │                           │ │
│  │  │                        │                           │ │
│  │  │ loadSolicitudes()      │                           │ │
│  │  │ └─ GET /api/planner/   │                           │ │
│  │  │    solicitudes         │                           │ │
│  │  │                        │                           │ │
│  │  │ renderSolicitudes()    │                           │ │
│  │  │ └─ Genera filas tabla  │                           │ │
│  │  │                        │                           │ │
│  │  │ showDetail(id)         │                           │ │
│  │  │ └─ GET /api/planner/   │                           │ │
│  │  │    solicitudes/<id>    │                           │ │
│  │  └────────────────────────┘                           │ │
│  │                                                         │ │
│  │  utils/api.js: window.AuthAPI                         │ │
│  │  - me()        → obtener usuario actual               │ │
│  │  - logout()    → cerrar sesión                        │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↕ API Calls (JSON)                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    BACKEND (5000)                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  app.py                                               │ │
│  │  ├─ Flask app factory                                 │ │
│  │  ├─ Blueprint registration:                           │ │
│  │  │  - planner_bp (NEW!)                              │ │
│  │  │  - auth_bp                                         │ │
│  │  │  - solicitudes_bp                                  │ │
│  │  │  - materiales_bp                                   │ │
│  │  └─ etc.                                              │ │
│  │                                                         │ │
│  │  planner_routes.py (NEW!)                             │ │
│  │  ┌──────────────────────────────┐                    │ │
│  │  │ @auth_required               │                    │ │
│  │  │ @require_planner (custom)    │                    │ │
│  │  ├──────────────────────────────┤                    │ │
│  │  │                              │                    │ │
│  │  │ GET /api/planner/dashboard   │                    │ │
│  │  │ → count solicitudes por      │                    │ │
│  │  │   estado                     │                    │ │
│  │  │                              │                    │ │
│  │  │ GET /api/planner/solicitudes │                    │ │
│  │  │ → query paginada a BD        │                    │ │
│  │  │                              │                    │ │
│  │  │ GET /api/planner/            │                    │ │
│  │  │     solicitudes/<id>         │                    │ │
│  │  │ → detalles + materiales      │                    │ │
│  │  │                              │                    │ │
│  │  │ POST /api/planner/           │                    │ │
│  │  │      solicitudes/<id>/       │                    │ │
│  │  │      optimize                │                    │ │
│  │  │ → actualiza estado            │                    │ │
│  │  └──────────────────────────────┘                    │ │
│  │                                                         │ │
│  │  auth_routes.py (Existing)                             │ │
│  │  ├─ GET /api/auth/me                                  │ │
│  │  ├─ POST /api/auth/login                              │ │
│  │  └─ POST /api/auth/logout                             │ │
│  │                                                         │ │
│  │  solicitudes.py (Existing)                             │ │
│  │  ├─ GET /api/solicitudes                              │ │
│  │  └─ POST /api/solicitudes                             │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↕ SQL Queries                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            BASE DE DATOS (SQLite)                      │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  usuarios (existing)                                   │ │
│  │  ├─ id_spm (PK)                                       │ │
│  │  ├─ username                                          │ │
│  │  ├─ rol ← VALIDADO AQUÍ                               │ │
│  │  ├─ nombre                                            │ │
│  │  └─ ...                                               │ │
│  │                                                         │ │
│  │  solicitudes (existing)                                │ │
│  │  ├─ id (PK)                                           │ │
│  │  ├─ centro                                            │ │
│  │  ├─ sector                                            │ │
│  │  ├─ criticidad                                        │ │
│  │  ├─ estado                                            │ │
│  │  ├─ created_at                                        │ │
│  │  └─ ...                                               │ │
│  │                                                         │ │
│  │  solicitudes_items (existing)                          │ │
│  │  ├─ id (PK)                                           │ │
│  │  ├─ solicitud_id (FK)                                 │ │
│  │  ├─ item_code                                         │ │
│  │  ├─ cantidad                                          │ │
│  │  ├─ precio_unitario                                   │ │
│  │  └─ ...                                               │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Flujo de Autenticación y Autorización

```
┌─────────────────────────────────────────┐
│  1. Usuario inicia sesión en home.html  │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  2. setupUserMenu() se ejecuta          │
│     - window.AuthAPI.me() obtiene user  │
│     - Recibe: {id, username, rol, ...}  │
└──────────────────┬──────────────────────┘
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
     ┌─────────┐       ┌──────────┐
     │ Rol OK? │       │ Rol Bad? │
     │ Mostrar │       │ Ocultar  │
     │ link    │       │ sección  │
     └────┬────┘       └──────────┘
          ↓
┌─────────────────────────────────────────┐
│  3. Usuario hace clic en Planificación  │
│     href="/planificador.html"           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  4. planificador.html carga             │
│     - Ejecuta planificador.js           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  5. waitForAuthAPI()                    │
│     - Espera a window.AuthAPI (max 5s)  │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  6. checkAccess()                       │
│     - window.AuthAPI.me() nuevamente    │
│     - Valida: rol en rolesPermitidos?   │
└──────────────────┬──────────────────────┘
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
     ┌─────────┐       ┌──────────────┐
     │ Rol OK? │       │ Rol NO OK?   │
     │ Continu│       │ - Toast error│
     │ con     │       │ - Redirect a │
     │ carga   │       │   /home.html │
     │ datos   │       │   (2 seg)    │
     └────┬────┘       └──────────────┘
          ↓
┌─────────────────────────────────────────┐
│  7. loadSolicitudes()                   │
│     GET /api/planner/solicitudes        │
│     credentials: 'include'              │
└──────────────────┬──────────────────────┘
                   ↓
        ┌──────────────────────┐
        │    BACKEND API       │
        ├──────────────────────┤
        │ @auth_required       │
        │ - Valida JWT/session │
        │ @require_planner     │
        │ - Valida rol         │
        └──────────────────────┘
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
     ┌─────────┐       ┌──────────┐
     │ Auth OK?│       │ 401/403? │
     │ + Rol OK│       │ Rechaza  │
     │ Query BD│       │          │
     └────┬────┘       └──────────┘
          ↓
┌─────────────────────────────────────────┐
│  SELECT solicitudes WHERE ...           │
│  LIMIT 10 OFFSET 0                      │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  8. renderSolicitudes()                 │
│     - Genera filas de tabla HTML        │
│     - Muestra estadísticas              │
│     - Muestra botones de acciones       │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  ✅ Usuario ve dashboard del            │
│     planificador con solicitudes        │
└─────────────────────────────────────────┘
```

---

## Flujo de Carga de Detalles

```
Usuario hace clic en fila
        ↓
showDetail(solicitudId)
        ↓
GET /api/planner/solicitudes/{id}
        ↓
Backend:
- @auth_required (JWT/session)
- @require_planner (rol validation)
- Query: SELECT solicitudes WHERE id=?
- Query: SELECT solicitudes_items WHERE solicitud_id=?
        ↓
Response JSON con:
- Datos generales (centro, sector, etc)
- Array de materiales
- Total calculado
        ↓
Frontend:
- renderSolicitudDetail()
- populateDetailPanel()
- mostrar panel lateral
        ↓
Usuario puede:
- Ver detalles completos
- Ver materiales asociados
- Hacer clic en "Optimizar"
```

---

## Estructura de Directorios

```
src/
├── backend/
│   ├── app.py
│   ├── core/
│   │   └── db.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── solicitudes.py
│   │   ├── materiales.py
│   │   └── planner_routes.py ✨ NUEVO
│   └── services/
│       └── auth/
│           └── auth.py
│
├── frontend/
│   ├── index.html
│   ├── home.html 🔄 MODIFICADO
│   ├── mi-cuenta.html
│   ├── crear-solicitud.html
│   ├── planificador.html ✨ NUEVO
│   ├── app.js
│   ├── planificador.js ✨ NUEVO
│   └── utils/
│       └── api.js
│
└── tests/
    ├── unit/
    ├── integration/
    └── test_planner_integration.py ✨ NUEVO
```

---

## Ciclo de Vida del Módulo Planificador

```
┌─────────────────────────────────────────┐
│ 1. CARGA INICIAL (cuando se abre)       │
├─────────────────────────────────────────┤
│ - Verificar autenticación               │
│ - Cargar datos del usuario              │
│ - Obtener estadísticas                  │
│ - Cargar lista de solicitudes           │
│ - Renderizar UI                         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. INTERACCIÓN DEL USUARIO               │
├─────────────────────────────────────────┤
│ - Clic en fila → showDetail()            │
│ - Clic en "Actualizar" → loadSolicitudes()
│ - Clic en "Siguiente" → página +1       │
│ - Clic en "Optimizar" → POST /optimize  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. VALIDACIÓN Y AUTORIZACIÓN             │
├─────────────────────────────────────────┤
│ - Cada acción verifica:                 │
│   ✓ Usuario autenticado?                │
│   ✓ Rol correcto?                       │
│   ✓ Parámetros válidos?                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 4. PROCESAMIENTO EN BACKEND              │
├─────────────────────────────────────────┤
│ - Validar entrada                       │
│ - Consultar BD                          │
│ - Serializar respuesta                  │
│ - Enviar JSON                           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 5. RENDERIZACIÓN EN FRONTEND             │
├─────────────────────────────────────────┤
│ - Actualizar estado local               │
│ - Re-renderizar componentes             │
│ - Mostrar mensajes (toast)              │
│ - Actualizar UI                         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 6. FEEDBACK AL USUARIO                   │
├─────────────────────────────────────────┤
│ - Toast: "✓ Éxito" o "✗ Error"         │
│ - Tabla actualizada                     │
│ - Panel cerrado o actualizado           │
└─────────────────────────────────────────┘
```

---

## Matriz de Permisos

```
┌────────────────────┬──────────┬──────────────┬──────────┐
│ Acción             │ Usuario  │ Planificador │ Admin    │
│                    │ Normal   │              │          │
├────────────────────┼──────────┼──────────────┼──────────┤
│ Ver link menu      │ ✗        │ ✓            │ ✓        │
│ Abrir página       │ ✗        │ ✓            │ ✓        │
│ Ver estadísticas   │ ✗        │ ✓            │ ✓        │
│ Listar solicitudes │ ✗        │ ✓            │ ✓        │
│ Ver detalles       │ ✗        │ ✓            │ ✓        │
│ Optimizar          │ ✗        │ ✓            │ ✓        │
│ Acceso a /api/...  │ ✗        │ ✓            │ ✓        │
└────────────────────┴──────────┴──────────────┴──────────┘
```

---

*Diagramas generados el 26 de octubre de 2025*
*Módulo Planificador v1.0.0*
