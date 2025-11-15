# INFORME DE AUDITORÍA - SPMv1.0

**Fecha:** 2025-01-27  
**Repositorio:** https://github.com/manuelremon/SPMv1.0.git  
**Branch Principal:** `main`

---

## 1. ESTRUCTURA DEL PROYECTO

### 1.1. Árbol Lógico (2 niveles)

```
SPMv1.0/
├── config/                    # Configuración de contenedores
│   ├── devcontainer.json
│   └── render.yaml
├── database/                  # Base de datos y migraciones
│   ├── audit/
│   ├── fixes/
│   ├── migrations/
│   └── schemas/
├── docs/                      # Documentación completa
│   ├── guides/
│   ├── history/
│   ├── infrastructure/
│   ├── planning/
│   ├── reference/
│   ├── reports/
│   ├── system/
│   └── testing/
├── gemini2.5-agent-starter/   # Agente IA (subproyecto)
│   ├── agent/
│   ├── scripts/
│   ├── targets/
│   └── tests/
├── infrastructure/            # Infraestructura (Terraform)
│   └── terraform/
├── scripts/                   # Scripts de utilidad
│   ├── db/
│   ├── dev/
│   ├── migrations/
│   ├── repair/
│   ├── tests/
│   ├── utilities/
│   └── utils/
├── src/                       # Código fuente principal
│   ├── agent/                 # Agente IA
│   ├── ai_assistant/          # Asistente IA (desactivado)
│   ├── backend/               # Backend Flask
│   │   ├── core/              # Configuración, DB, init
│   │   ├── data/              # Datos CSV y assets
│   │   ├── middleware/        # Auth helpers, CSRF, decorators, ratelimit
│   │   ├── models/            # Schemas, roles, catalog_schema
│   │   ├── routes/            # Blueprints de rutas
│   │   ├── services/          # Servicios (auth, dashboard, AI, etc.)
│   │   ├── static/            # HTML estático
│   │   └── uploads/           # Archivos subidos
│   ├── frontend/              # Frontend (HTML/JS)
│   │   ├── assets/            # Imágenes, logos, favicon
│   │   ├── components/        # Componentes reutilizables
│   │   ├── pages/             # Páginas organizadas
│   │   ├── shared/            # Navbar compartido
│   │   ├── ui/                # UI components
│   │   └── utils/             # Utilidades (api_client.js, api.js)
│   └── planner/               # Módulo de planificación
│       ├── algorithms/        # Algoritmos de optimización
│       ├── decision_tree/     # Árbol de decisiones
│       ├── events/            # Eventos
│       ├── filters/           # Filtros
│       ├── models/            # Modelos de datos
│       ├── optimization/      # Optimización
│       ├── rules/             # Reglas de negocio
│       └── scoring/           # Scoring
├── tests/                     # Tests (90+ archivos)
│   ├── e2e/
│   └── manual/
├── .env*                      # Variables de entorno (no encontrado)
├── Dockerfile                 # Dockerfile para producción
├── docker-compose.yml         # Docker Compose
├── jest.config.js             # Configuración Jest
├── package.json               # Dependencias frontend
├── package-lock.json
├── pyproject.toml             # Configuración Python (Black, Ruff, Pytest)
├── requirements.txt           # Dependencias Python
├── requirements-dev.txt       # Dependencias desarrollo
├── run_backend.py             # Script de inicio backend
├── start_server.py            # Script de inicio servidor
├── vite.config.js             # Configuración Vite
├── vite.config.simple.js      # Configuración Vite alternativa
└── wsgi.py                    # WSGI para producción
```

### 1.2. Carpetas Clave

- **`src/backend/`**: Backend Flask con aplicación factory pattern
- **`src/frontend/`**: Frontend HTML/JS vanilla con Vite
- **`src/planner/`**: Módulo de planificación con algoritmos de optimización
- **`src/backend/routes/`**: Blueprints de rutas API
- **`src/backend/core/`**: Configuración, DB, inicialización
- **`src/backend/services/`**: Servicios de negocio (auth, dashboard, AI)
- **`src/backend/middleware/`**: Middleware (auth, CSRF, decorators)

---

## 2. DEPENDENCIAS POR STACK

### 2.1. Backend (Python)

**Framework Principal:**
- `Flask==3.1.2` - Framework web
- `flask-cors==6.0.1` - CORS support
- `gunicorn==23.0.0` - Servidor WSGI

**Autenticación y Seguridad:**
- `PyJWT==2.10.1` - JWT tokens
- `bcrypt==5.0.0` - Hash de contraseñas
- `python-dotenv==1.1.1` - Variables de entorno

**Base de Datos:**
- `SQLAlchemy==2.0.44` - ORM (no se usa directamente, se usa SQLite nativo)

**Validación y Schemas:**
- `pydantic==2.12.3` - Validación de datos
- `pydantic_core==2.41.4` - Core de Pydantic

**Utilidades:**
- `pandas==2.3.3` - Procesamiento de datos
- `numpy==2.3.4` - Operaciones numéricas
- `openpyxl==3.1.5` - Excel export
- `reportlab==4.4.4` - PDF export
- `scikit-learn==1.7.2` - Machine learning (para AI assistant)
- `scipy==1.16.2` - Ciencia de datos

**Otros:**
- `Werkzeug==3.1.3` - Utilidades WSGI
- `Jinja2==3.1.6` - Templates (no se usa mucho en SPA)
- `requests==2.32.5` - HTTP client

### 2.2. Frontend (JavaScript)

**Build Tool:**
- `vite==5.0.0` - Build tool y dev server

**Testing:**
- `jest==29.7.0` - Framework de testing
- `jest-environment-jsdom==30.2.0` - Entorno DOM para Jest
- `@testing-library/dom==9.3.0` - Utilidades de testing

**Dependencias:**
- `@anthropic-ai/sdk==0.68.0` - SDK de Anthropic (Claude)
- `jsdom==27.0.1` - DOM para Node.js

**Babel:**
- `@babel/preset-env==7.23.0` - Preset Babel

### 2.3. Herramientas de Desarrollo

**Python:**
- `black` (pyproject.toml) - Formateo de código
- `ruff` (pyproject.toml) - Linter
- `pytest` (pyproject.toml) - Testing framework

**Node.js:**
- `jest` - Testing framework

---

## 3. SCRIPTS DE BUILD/TEST

### 3.1. Frontend (package.json)

```json
{
  "dev": "vite",                    // Servidor de desarrollo
  "build": "vite build",            // Build de producción
  "preview": "vite preview",        // Preview de build
  "test": "jest",                   // Ejecutar tests
  "test:watch": "jest --watch",     // Tests en modo watch
  "lint": "echo 'Linting configured in project'",
  "format": "echo 'Formatting configured in project'"
}
```

### 3.2. Backend

**Scripts de inicio:**
- `run_backend.py` - Inicio del backend
- `start_server.py` - Inicio del servidor
- `wsgi.py` - WSGI para producción (Gunicorn)

**Scripts de desarrollo:**
- `scripts/dev/start_server.py` - Servidor de desarrollo
- `scripts/dev/run_backend.py` - Backend de desarrollo
- `scripts/dev/simple-server.py` - Servidor simple

**Scripts de base de datos:**
- `scripts/db/init_db.py` - Inicialización de DB
- `scripts/db/create_test_data.py` - Datos de prueba
- `scripts/db/list_tables.py` - Listar tablas

**Scripts de testing:**
- `scripts/tests/run_validations.py` - Validaciones
- Tests en `tests/` (90+ archivos)

### 3.3. Docker

```dockerfile
# Dockerfile
- Base: python:3.12-slim
- Comando: gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 wsgi:app
- Healthcheck: curl http://localhost:5000/api/health
```

---

## 4. ENDPOINTS REST

### 4.1. Autenticación (`/api/auth`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| POST | `/api/auth/login` | No | `auth_routes.login()` | Login de usuario |
| POST | `/api/auth/logout` | No | `auth_routes.logout()` | Logout de usuario |
| POST | `/api/auth/refresh` | No | `auth_routes.refresh()` | Refresh token (no implementado) |
| POST | `/api/auth/register` | No | `auth_routes.register()` | Registro de usuario |
| GET | `/api/auth/me` | Sí | `auth_routes.me_v2()` | Obtener usuario actual |
| GET | `/api/auth/usuarios/me` | Sí | `auth_routes.me_legacy()` | Obtener usuario actual (legacy) |
| PATCH | `/api/auth/me/fields` | Sí | `auth_routes.update_me_fields()` | Actualizar campos de perfil |
| POST | `/api/auth/me/change-requests` | Sí | `auth_routes.create_change_request()` | Solicitar cambios de perfil |
| POST | `/api/auth/me/telefono` | Sí | `auth_routes.update_phone()` | Actualizar teléfono |
| POST | `/api/auth/me/mail` | Sí | `auth_routes.update_mail()` | Actualizar email |
| POST | `/api/auth/me/centros/solicitud` | Sí | `auth_routes.request_additional_centers()` | Solicitar acceso a centros |
| GET | `/api/auth/dashboard/stats` | Sí | `auth_routes.get_dashboard_stats()` | Estadísticas del dashboard |
| GET | `/api/auth/mi-acceso` | Sí | `auth_routes.get_user_access()` | Obtener acceso del usuario |

### 4.2. Solicitudes (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/solicitudes` | Sí | `solicitudes.listar_solicitudes()` | Listar solicitudes del usuario |
| GET | `/api/solicitudes/<id>` | Sí | `solicitudes.obtener_solicitud()` | Obtener solicitud por ID |
| POST | `/api/solicitudes` | Sí | `solicitudes.crear_solicitud()` | Crear nueva solicitud |
| PUT | `/api/solicitudes/<id>` | Sí | `solicitudes.finalizar_solicitud()` | Finalizar solicitud (draft → pending) |
| POST | `/api/solicitudes/drafts` | Sí | `solicitudes.crear_borrador()` | Crear borrador |
| PATCH | `/api/solicitudes/<id>/draft` | Sí | `solicitudes.actualizar_borrador()` | Actualizar borrador |
| POST | `/api/solicitudes/<id>/decidir` | Sí | `solicitudes.decidir_solicitud()` | Aprobar/rechazar solicitud |
| PATCH | `/api/solicitudes/<id>/cancel` | Sí | `solicitudes.cancelar_solicitud()` | Cancelar solicitud |
| POST | `/api/solicitudes/<id>/decidir_cancelacion` | Sí | `solicitudes.decidir_cancelacion()` | Decidir sobre cancelación |
| GET | `/api/solicitudes/export/excel` | Sí | `solicitudes.export_solicitudes_excel()` | Exportar a Excel |
| GET | `/api/solicitudes/export/pdf` | Sí | `solicitudes.export_solicitudes_pdf()` | Exportar a PDF |

### 4.3. Archivos de Solicitudes (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| POST | `/api/solicitudes/<id>/archivos` | Sí | `solicitudes_archivos.upload()` | Subir archivo a solicitud |
| GET | `/api/solicitudes/<id>/archivos/<fname>` | Sí | `solicitudes_archivos.download()` | Descargar archivo |

### 4.4. Materiales (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/materiales` | No | `materiales.search_materiales()` | Buscar materiales |

### 4.5. Catálogos (`/api/catalogos`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/catalogos` | Sí | `catalogos.obtener_catalogos()` | Obtener todos los catálogos |
| GET | `/api/catalogos/<resource>` | Sí | `catalogos.obtener_catalogo()` | Obtener catálogo específico |

### 4.6. Almacenes (`/api/almacenes`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/almacenes` | Sí | `catalogos.obtener_almacenes()` | Obtener almacenes |

### 4.7. Planificación (`/api/planner`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/planner/dashboard` | Sí (planner) | `planner_routes.get_dashboard()` | Dashboard de planificación |
| GET | `/api/planner/solicitudes` | Sí (planner) | `planner_routes.get_solicitudes()` | Listar solicitudes para planificación |
| GET | `/api/planner/solicitudes/<id>` | Sí (planner) | `planner_routes.get_solicitud_detail()` | Detalle de solicitud |
| POST | `/api/planner/solicitudes/<id>/optimize` | Sí (planner) | `planner_routes.optimize_solicitud()` | Optimizar solicitud |

### 4.8. Planificador Legacy (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/queue` | Sí | `planificador.get_queue()` | Cola de solicitudes |
| PATCH | `/api/solicitudes/<id>/tomar` | Sí | `planificador.tomar_solicitud()` | Tomar solicitud |
| PATCH | `/api/solicitudes/<id>/liberar` | Sí | `planificador.liberar_solicitud()` | Liberar solicitud |
| GET | `/api/solicitudes/<id>/tratamiento` | Sí | `planificador.get_tratamiento()` | Obtener tratamiento |
| PATCH | `/api/solicitudes/<id>/tratamiento/items` | Sí | `planificador.update_items()` | Actualizar items |
| POST | `/api/solicitudes/<id>/finalizar` | Sí | `planificador.finalizar()` | Finalizar tratamiento |
| POST | `/api/solicitudes/<id>/rechazar` | Sí | `planificador.rechazar()` | Rechazar solicitud |
| GET | `/api/estadisticas` | Sí | `planificador.get_estadisticas()` | Estadísticas |

### 4.9. Notificaciones (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/notificaciones` | Sí | `notificaciones.listar_notificaciones()` | Listar notificaciones |
| GET | `/api/notificaciones/<id>` | Sí | `notificaciones.obtener_notificacion()` | Obtener notificación |
| POST | `/api/notificaciones/marcar` | Sí | `notificaciones.marcar_leida()` | Marcar como leída |

### 4.10. Presupuestos (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| POST | `/api/presupuestos/incorporaciones` | Sí | `presupuestos.crear_incorporacion()` | Crear incorporación de presupuesto |
| POST | `/api/presupuestos/incorporaciones/<id>/resolver` | Sí | `presupuestos.resolver_incorporacion()` | Resolver incorporación |

### 4.11. Admin (`/api/admin`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| PUT | `/api/admin/usuarios/<id>` | Sí (admin) | `admin.update_usuario()` | Actualizar usuario |
| PUT | `/api/admin/materiales/<codigo>` | Sí (admin) | `admin.update_material()` | Actualizar material |
| POST | `/api/admin/config/<resource>` | Sí (admin) | `admin.create_config()` | Crear configuración |
| PUT | `/api/admin/config/<resource>/<id>` | Sí (admin) | `admin.update_config()` | Actualizar configuración |
| POST | `/api/admin/user/profile-request` | Sí (admin) | `admin.create_profile_request()` | Crear solicitud de perfil |
| POST | `/api/admin/profile-requests/<id>` | Sí (admin) | `admin.resolve_profile_request()` | Resolver solicitud de perfil |

### 4.12. Usuarios (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| PATCH | `/api/usuarios/me/fields` | Sí | `usuarios.update_me_fields()` | Actualizar campos de usuario |
| POST | `/api/usuarios/me/change-requests` | Sí | `usuarios.create_change_request()` | Crear solicitud de cambio |

### 4.13. Preferencias (`/api`)

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/preferences` | Sí | `preferences.get_preferences()` | Obtener preferencias |
| PUT | `/api/preferences` | Sí | `preferences.update_preferences()` | Actualizar preferencias |

### 4.14. Health y Utilidades

| Método | Ruta | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| GET | `/api/health` | No | `app.health()` | Health check |
| GET | `/healthz` | No | `app.healthz()` | Health check (Kubernetes) |
| POST | `/api/client-logs` | No | `app.client_logs()` | Logs del cliente |
| PUT | `/api/users/me` | Sí | `app.update_me()` | Actualizar usuario (legacy) |

### 4.15. Rutas Frontend (HTML)

| Ruta | Handler | Descripción |
|------|---------|-------------|
| `/` | `app.page_index()` | Login |
| `/home` | `app.page_home()` | Home |
| `/dashboard.html` | `app.page_dashboard()` | Dashboard |
| `/solicitudes.html` | `app.page_solicitudes()` | Solicitudes |
| `/nueva-solicitud.html` | `app.page_nueva_solicitud()` | Nueva solicitud |
| `/agregar-materiales.html` | `app.page_agregar_materiales()` | Agregar materiales |
| `/notificaciones.html` | `app.page_notificaciones()` | Notificaciones |
| `/preferencias.html` | `app.page_preferencias()` | Preferencias |
| `/usuarios.html` | `app.page_usuarios()` | Usuarios |
| `/materiales.html` | `app.page_materiales()` | Materiales |
| `/centros.html` | `app.page_centros()` | Centros |
| `/almacenes.html` | `app.page_almacenes()` | Almacenes |
| `/reportes.html` | `app.page_reportes()` | Reportes |
| `/planificacion.html` | `app.page_planificacion()` | Planificación |
| `/ayuda.html` | `app.page_ayuda()` | Ayuda |

---

## 5. FLUJOS DE NEGOCIO

### 5.1. Autenticación

**Archivos Implicados:**
- `src/backend/routes/auth_routes.py` - Rutas de autenticación
- `src/backend/services/auth/auth.py` - Lógica de autenticación
- `src/backend/services/auth/jwt_utils.py` - Utilidades JWT
- `src/backend/middleware/decorators.py` - Decoradores de autenticación
- `src/backend/middleware/auth_helpers.py` - Helpers de autenticación
- `src/frontend/components/auth/auth_guard.js` - Guard de autenticación frontend
- `src/frontend/components/auth/auth_roles.js` - Roles de autenticación frontend
- `src/frontend/utils/api_client.js` - Cliente API para login

**Flujo:**
1. Usuario envía credenciales a `/api/auth/login`
2. Backend valida credenciales con `authenticate_user()`
3. Se genera JWT token con `issue_token()`
4. Token se almacena en cookie `spm_token`
5. Frontend verifica autenticación con `auth_guard.js`
6. Middleware `@auth_required` valida token en cada request
7. Usuario puede hacer logout en `/api/auth/logout`

**Configuración:**
- JWT algoritmo: HS256
- TTL por defecto: 3600 segundos (1 hora)
- Cookie: `spm_token`, HttpOnly, SameSite=Lax
- Secret key: `SPM_SECRET_KEY` (variable de entorno)

### 5.2. Aprobación de Solicitudes

**Archivos Implicados:**
- `src/backend/routes/solicitudes.py` - Rutas de solicitudes
- `src/backend/models/roles.py` - Roles y permisos
- `src/backend/services/auth/auth.py` - Autenticación

**Flujo:**
1. Usuario crea solicitud en estado `draft`
2. Usuario finaliza solicitud → estado `pendiente_de_aprobacion`
3. Sistema asigna aprobador basado en monto:
   - `jefe`: USD 0.01 - 20,000
   - `gerente1`: USD 20,000.01 - 100,000
   - `gerente2`: USD 100,000.01+
4. Aprobador recibe notificación
5. Aprobador decide en `/api/solicitudes/<id>/decidir`:
   - `aprobar` → estado `aprobada` o `en_tratamiento` (si hay planificador)
   - `rechazar` → estado `rechazada`
6. Sistema asigna planificador automáticamente si se aprueba
7. Notificaciones se envían a usuario y planificador

**Validaciones:**
- Materiales deben existir en catálogo
- Monto total debe ser válido (> 0)
- Aprobador debe estar activo
- Usuario solicitante debe estar activo
- Presupuesto disponible

### 5.3. Planificación

**Archivos Implicados:**
- `src/backend/routes/planner_routes.py` - Rutas de planificación
- `src/backend/routes/planificador.py` - Rutas legacy de planificador
- `src/planner/` - Módulo de planificación
- `src/planner/algorithms/` - Algoritmos de optimización
- `src/planner/decision_tree/` - Árbol de decisiones
- `src/planner/optimization/` - Optimización

**Flujo:**
1. Solicitud aprobada se asigna a planificador
2. Planificador ve solicitud en cola (`/api/planner/solicitudes`)
3. Planificador puede tomar solicitud (`/api/solicitudes/<id>/tomar`)
4. Planificador procesa solicitud:
   - Ver tratamiento (`/api/solicitudes/<id>/tratamiento`)
   - Actualizar items (`/api/solicitudes/<id>/tratamiento/items`)
   - Finalizar (`/api/solicitudes/<id>/finalizar`)
   - Rechazar (`/api/solicitudes/<id>/rechazar`)
5. Algoritmos de optimización se aplican:
   - `expedite_probability.py` - Probabilidad de expedición
   - `transfer_tdabc.py` - Transferencia TDABC
   - `ctp_johnson.py` - CTP Johnson
   - `substitutes_graph.py` - Grafo de sustitutos
   - `disassembly_knapsack.py` - Mochila de desensamblaje
   - `release_marginal_cost.py` - Costo marginal de liberación
   - `purchase_multicriterion.py` - Compra multicriterio
   - `reserve_dynamic.py` - Reserva dinámica
6. Decision tree evalúa rutas de procesamiento
7. Solicitud finalizada → estado `finalizada`

### 5.4. Reportes

**Archivos Implicados:**
- `src/backend/routes/solicitudes.py` - Exportación de solicitudes
- `src/backend/services/dashboard/stats.py` - Estadísticas del dashboard

**Flujo:**
1. Usuario solicita reporte:
   - Excel: `/api/solicitudes/export/excel`
   - PDF: `/api/solicitudes/export/pdf`
2. Sistema obtiene solicitudes del usuario
3. Sistema genera archivo (Excel o PDF)
4. Archivo se descarga al cliente

**Estadísticas:**
- Dashboard stats: `/api/auth/dashboard/stats`
- Estadísticas de planificación: `/api/estadisticas`
- Estadísticas de solicitudes: `/api/solicitudes/stats`

### 5.5. Notificaciones

**Archivos Implicados:**
- `src/backend/routes/notificaciones.py` - Rutas de notificaciones
- `src/backend/services/` - Servicios de notificaciones

**Flujo:**
1. Sistema crea notificación en eventos:
   - Solicitud creada → notificación a aprobador
   - Solicitud aprobada → notificación a usuario y planificador
   - Solicitud rechazada → notificación a usuario
   - Solicitud cancelada → notificación a aprobador/planificador
   - Solicitud finalizada → notificación a usuario
2. Usuario ve notificaciones en `/api/notificaciones`
3. Usuario marca como leída en `/api/notificaciones/marcar`

---

## 6. DEUDA TÉCNICA Y RIESGOS

### 6.1. Seguridad

**Riesgos Identificados:**

1. **Secret Key en Desarrollo:**
   - `Dockerfile` tiene `SPM_SECRET_KEY=dev-key-12345` hardcodeado
   - **Riesgo:** Alto - Exposición de secret key en producción
   - **Recomendación:** Usar variables de entorno siempre

2. **AUTH_BYPASS en Desarrollo:**
   - `app.py` tiene bypass de autenticación con `AUTH_BYPASS=1`
   - **Riesgo:** Medio - Puede activarse accidentalmente en producción
   - **Recomendación:** Validar que solo funcione en localhost

3. **CORS Configuración:**
   - CORS solo permite origen del frontend
   - **Riesgo:** Bajo - Configuración correcta, pero revisar en producción

4. **SQL Injection:**
   - Uso de f-strings en algunas consultas SQL
   - **Riesgo:** Medio - Posible SQL injection si no se sanitiza
   - **Recomendación:** Usar siempre parámetros preparados

5. **JWT Secret Key:**
   - Secret key se genera aleatoriamente en desarrollo si no existe
   - **Riesgo:** Medio - Puede cambiar en cada reinicio
   - **Recomendación:** Usar secret key fija en producción

6. **CSRF Protection:**
   - CSRF token implementado pero no verificado en todas las rutas
   - **Riesgo:** Medio - Posible CSRF attack
   - **Recomendación:** Verificar CSRF en todas las rutas POST/PUT/DELETE

### 6.2. Acoplamiento

**Problemas Identificados:**

1. **Frontend y Backend Acoplados:**
   - Backend sirve HTML estático directamente
   - **Riesgo:** Medio - Dificulta separación de frontend/backend
   - **Recomendación:** Separar frontend y backend completamente

2. **Dependencias Circulares:**
   - Posibles dependencias circulares entre módulos
   - **Riesgo:** Bajo - Revisar imports

3. **Código Legacy:**
   - Múltiples rutas legacy (`/api/auth/usuarios/me`, `/api/users/me`)
   - **Riesgo:** Bajo - Mantenimiento complicado
   - **Recomendación:** Deprecar rutas legacy

### 6.3. Falta de Tests

**Cobertura de Tests:**
- 90+ archivos de test en `tests/`
- Tests manuales en `tests/manual/`
- Tests E2E en `tests/e2e/`
- **Riesgo:** Medio - Cobertura desconocida
- **Recomendación:** Ejecutar tests y medir cobertura

**Tests Faltantes:**
- Tests unitarios para servicios
- Tests de integración para flujos completos
- Tests de seguridad (SQL injection, XSS, CSRF)
- Tests de performance

### 6.4. Configuraciones Hardcodeadas

**Configuraciones Identificadas:**
- `FRONTEND_ORIGIN` tiene valor por defecto: `http://localhost:5173`
- `DB_PATH` tiene valor por defecto: `src/backend/data/spm.db`
- `LOG_PATH` tiene valor por defecto: `src/backend/logs/app.log`
- `OLLAMA_ENDPOINT` tiene valor por defecto: `http://127.0.0.1:11434`
- `MAX_CONTENT_LENGTH` tiene valor por defecto: `16MB`
- **Riesgo:** Bajo - Valores por defecto razonables, pero revisar en producción

### 6.5. Base de Datos

**Problemas Identificados:**
- SQLite como base de datos (no escalable)
- **Riesgo:** Medio - No soporta alta concurrencia
- **Recomendación:** Migrar a PostgreSQL para producción

**Migraciones:**
- Migraciones en `database/migrations/`
- **Riesgo:** Bajo - Migraciones implementadas

### 6.6. Código Desactivado

**Código Comentado:**
- `form_intelligence_routes.py` - Desactivado (AI Assistant removido)
- `form_intelligence_routes_v2.py` - Desactivado (AI Assistant removido)
- `export_bp` - Comentado (TODO: Crear módulo)
- `files_bp` - Comentado (TODO: Descomentar cuando exista)
- **Riesgo:** Bajo - Código muerto, pero puede confundir
- **Recomendación:** Eliminar código desactivado o documentar por qué está comentado

### 6.7. Dependencias Obsoletas

**Dependencias a Revisar:**
- `scikit-learn==1.7.2` - Usado para AI assistant (desactivado)
- `scipy==1.16.2` - Usado para AI assistant (desactivado)
- **Riesgo:** Bajo - Dependencias no usadas
- **Recomendación:** Eliminar dependencias no usadas

### 6.8. Documentación

**Documentación Existente:**
- Documentación extensa en `docs/`
- **Riesgo:** Bajo - Buena documentación

**Documentación Faltante:**
- API documentation (OpenAPI/Swagger)
- Diagramas de arquitectura actualizados
- Guías de deployment actualizadas

---

## 7. MAPA DE MÓDULOS

### 7.1. Módulo Actual → Módulo Target Propuesto

| Módulo Actual | Estado | Módulo Target Propuesto | Prioridad |
|---------------|--------|-------------------------|-----------|
| `src/backend/routes/auth_routes.py` | ✅ Activo | Mantener, mejorar documentación | Alta |
| `src/backend/routes/solicitudes.py` | ✅ Activo | Refactorizar validaciones, separar lógica de negocio | Alta |
| `src/backend/routes/planner_routes.py` | ✅ Activo | Integrar con módulo `src/planner/` | Media |
| `src/backend/routes/planificador.py` | ✅ Activo (legacy) | Deprecar, migrar a `planner_routes.py` | Media |
| `src/backend/routes/form_intelligence_routes.py` | ❌ Desactivado | Eliminar o reactivar con documentación | Baja |
| `src/backend/routes/form_intelligence_routes_v2.py` | ❌ Desactivado | Eliminar o reactivar con documentación | Baja |
| `src/backend/routes/admin.py` | ✅ Activo | Mejorar permisos, agregar validaciones | Alta |
| `src/backend/routes/catalogos.py` | ✅ Activo | Optimizar consultas, agregar caché | Media |
| `src/backend/routes/materiales.py` | ✅ Activo | Mejorar búsqueda, agregar índices | Media |
| `src/backend/routes/notificaciones.py` | ✅ Activo | Agregar notificaciones en tiempo real | Baja |
| `src/backend/routes/presupuestos.py` | ✅ Activo | Integrar con módulo de presupuestos | Baja |
| `src/backend/services/auth/` | ✅ Activo | Mejorar seguridad, agregar rate limiting | Alta |
| `src/backend/services/dashboard/` | ✅ Activo | Optimizar consultas, agregar caché | Media |
| `src/planner/` | ✅ Activo | Integrar con backend, mejorar documentación | Alta |
| `src/frontend/` | ✅ Activo | Separar de backend, mejorar estructura | Alta |
| `src/ai_assistant/` | ❌ Desactivado | Eliminar o reactivar con documentación | Baja |

### 7.2. Refactorizaciones Propuestas

1. **Separar Frontend y Backend:**
   - Frontend: Aplicación independiente con Vite
   - Backend: API REST pura
   - Comunicación: API REST sobre HTTP/HTTPS

2. **Refactorizar Rutas de Solicitudes:**
   - Separar lógica de negocio en servicios
   - Validaciones en modelos/schemas
   - Rutas solo para HTTP handling

3. **Integrar Módulo de Planificación:**
   - Conectar `src/planner/` con `src/backend/routes/planner_routes.py`
   - Usar algoritmos de optimización en flujo real
   - Mejorar documentación

4. **Mejorar Seguridad:**
   - Agregar rate limiting
   - Mejorar CSRF protection
   - Validar todas las entradas
   - Usar parámetros preparados en todas las consultas SQL

5. **Migrar a PostgreSQL:**
   - SQLite → PostgreSQL
   - Mejorar escalabilidad
   - Soporte para alta concurrencia

6. **Agregar Tests:**
   - Tests unitarios para servicios
   - Tests de integración para flujos completos
   - Tests de seguridad
   - Tests de performance

---

## 8. RECOMENDACIONES INMEDIATAS

### 8.1. Seguridad (Crítico)

1. **Eliminar Secret Key Hardcodeada:**
   ```dockerfile
   # Dockerfile - ELIMINAR
   ENV SPM_SECRET_KEY=dev-key-12345
   ```
   - Usar siempre variable de entorno
   - Validar que existe en producción

2. **Mejorar AUTH_BYPASS:**
   ```python
   # app.py - MEJORAR
   if os.environ.get("AUTH_BYPASS") == "1" and request.host.startswith(("127.0.0.1", "localhost")):
       # Solo en localhost, nunca en producción
   ```
   - Agregar validación de entorno (development only)
   - Documentar uso

3. **Agregar CSRF Protection:**
   - Verificar CSRF token en todas las rutas POST/PUT/DELETE
   - Agregar middleware de CSRF

4. **Validar Entradas:**
   - Usar Pydantic para validar todas las entradas
   - Sanitizar todas las consultas SQL
   - Usar parámetros preparados siempre

### 8.2. Código (Alto)

1. **Eliminar Código Desactivado:**
   - Eliminar `form_intelligence_routes.py` y `form_intelligence_routes_v2.py`
   - O documentar por qué están desactivados
   - Eliminar dependencias no usadas (scikit-learn, scipy)

2. **Deprecar Rutas Legacy:**
   - Deprecar `/api/auth/usuarios/me` → usar `/api/auth/me`
   - Deprecar `/api/users/me` → usar `/api/auth/me`
   - Agregar warnings en rutas legacy

3. **Refactorizar Solicitudes:**
   - Separar lógica de negocio en servicios
   - Mejorar validaciones
   - Optimizar consultas SQL

### 8.3. Base de Datos (Medio)

1. **Optimizar Consultas:**
   - Agregar índices en tablas frecuentes
   - Optimizar consultas con JOINs
   - Agregar caché para consultas frecuentes

2. **Planificar Migración a PostgreSQL:**
   - Evaluar impacto de migración
   - Crear plan de migración
   - Probar migración en entorno de desarrollo

### 8.4. Testing (Medio)

1. **Ejecutar Tests:**
   - Ejecutar todos los tests
   - Medir cobertura de código
   - Identificar tests faltantes

2. **Agregar Tests:**
   - Tests unitarios para servicios
   - Tests de integración para flujos completos
   - Tests de seguridad

### 8.5. Documentación (Bajo)

1. **Agregar API Documentation:**
   - OpenAPI/Swagger specification
   - Documentar todos los endpoints
   - Ejemplos de uso

2. **Actualizar Documentación:**
   - Actualizar diagramas de arquitectura
   - Actualizar guías de deployment
   - Documentar flujos de negocio

### 8.6. Performance (Bajo)

1. **Optimizar Frontend:**
   - Minificar JavaScript
   - Agregar caché para assets estáticos
   - Optimizar imágenes

2. **Optimizar Backend:**
   - Agregar caché para consultas frecuentes
   - Optimizar consultas SQL
   - Agregar paginación en listados

---

## 9. RESUMEN EJECUTIVO

### 9.1. Estado Actual

- **Backend:** Flask con aplicación factory pattern, bien estructurado
- **Frontend:** HTML/JS vanilla con Vite, acoplado al backend
- **Base de Datos:** SQLite (no escalable para producción)
- **Autenticación:** JWT con cookies, bien implementado
- **Seguridad:** Algunos riesgos identificados (secret key, CSRF)
- **Tests:** 90+ archivos de test, cobertura desconocida
- **Documentación:** Extensa documentación en `docs/`

### 9.2. Fortalezas

1. **Arquitectura clara:** Separación de concerns (routes, services, models)
2. **Autenticación robusta:** JWT con cookies, middleware de autenticación
3. **Módulo de planificación:** Algoritmos de optimización bien estructurados
4. **Documentación extensa:** Buena documentación en `docs/`
5. **Tests existentes:** 90+ archivos de test

### 9.3. Debilidades

1. **Seguridad:** Secret key hardcodeada, CSRF no verificado en todas las rutas
2. **Acoplamiento:** Frontend y backend acoplados
3. **Base de datos:** SQLite no escalable para producción
4. **Código desactivado:** Código comentado sin documentación
5. **Dependencias no usadas:** scikit-learn, scipy (AI assistant desactivado)

### 9.4. Oportunidades

1. **Separar frontend y backend:** Aplicación independiente
2. **Migrar a PostgreSQL:** Mejor escalabilidad
3. **Mejorar seguridad:** CSRF, rate limiting, validaciones
4. **Optimizar performance:** Caché, índices, consultas optimizadas
5. **Agregar tests:** Cobertura completa, tests de seguridad

### 9.5. Amenazas

1. **Seguridad:** Posibles vulnerabilidades (SQL injection, XSS, CSRF)
2. **Escalabilidad:** SQLite no soporta alta concurrencia
3. **Mantenimiento:** Código desactivado, rutas legacy
4. **Performance:** Consultas no optimizadas, falta de caché

---

## 10. CONCLUSIÓN

El proyecto **SPMv1.0** es una aplicación bien estructurada con una arquitectura clara y documentación extensa. Sin embargo, existen algunos riesgos de seguridad y oportunidades de mejora que deben abordarse antes de llevarlo a producción.

**Prioridades inmediatas:**
1. **Seguridad:** Eliminar secret key hardcodeada, mejorar CSRF protection
2. **Código:** Eliminar código desactivado, deprecar rutas legacy
3. **Base de datos:** Planificar migración a PostgreSQL
4. **Tests:** Ejecutar tests, medir cobertura, agregar tests faltantes

**Recomendación final:** El proyecto está listo para desarrollo, pero requiere mejoras de seguridad y optimizaciones antes de producción.

---

**Generado por:** Auditoría Automática  
**Fecha:** 2025-01-27  
**Versión:** 1.0

