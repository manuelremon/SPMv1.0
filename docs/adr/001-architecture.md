# ADR-001: Arquitectura v2.0 - Migración a Backend API REST + SPA

**Estado:** Aceptado  
**Fecha:** 13 de noviembre de 2025  
**Decisores:** Equipo de desarrollo SPM  
**Contexto técnico:** FASE 2 - Reconstrucción controlada

---

## Contexto

### Sistema Actual (v1.0)

**Stack tecnológico:**
- **Backend:** Flask 3.1.2 + Python 3.13
- **Base de datos:** SQLite (desarrollo y producción)
- **Frontend:** Multi-página HTML + Vanilla JavaScript
- **Arquitectura:** Monolito con server-side rendering parcial
- **Autenticación:** JWT con cookies
- **Dependencias:** 33 paquetes Python (numpy, pandas, scipy, reportlab, etc.)

**Estructura de archivos:**
```
src/
├── backend/
│   ├── app.py (458 líneas, factory pattern)
│   ├── routes/ (10 blueprints: auth, solicitudes, materiales, planner, etc.)
│   ├── services/ (auth, archivos)
│   ├── models/ (schemas Pydantic)
│   ├── core/ (db, config)
│   └── middleware/ (decorators, auth)
└── frontend/
    ├── 20+ archivos HTML (login.html, home.html, etc.)
    ├── app.js (86KB monolítico)
    ├── styles.css (72KB)
    └── utils/ (api.js)
```

### Problemas Identificados

#### 1. **Seguridad**
- ❌ Secretos hardcodeados en Dockerfile (`SPM_SECRET_KEY=dev-key-12345`)
- ❌ `AUTH_BYPASS` permite skip de autenticación en desarrollo
- ❌ Sin CSRF protection
- ❌ Sin rate limiting
- ❌ CORS configurado pero sin validación estricta
- ⚠️ JWT sin refresh token mechanism
- ⚠️ Cookies sin flags `HttpOnly` consistentes

#### 2. **Acoplamiento**
- ❌ **Frontend acoplado al backend:** HTML servido desde Flask, sin API pura
- ❌ **Rutas duplicadas:** `/api/auth/usuarios/me` vs `/api/auth/me` (legacy endpoints)
- ❌ **Módulo planner acoplado:** Lógica en `routes/planner_routes.py` sin interfaz clara
- ❌ **app.js monolítico:** 86KB sin tree-shaking, todo cargado en cada página
- ⚠️ Mezcla de `src/frontend/` con `src/backend/` sin separación clara

#### 3. **Base de Datos (SQLite)**
- ❌ **No apto para producción:** Sin concurrencia real (write locks)
- ❌ **Sin replicación:** No hay backups automáticos
- ❌ **Sin tipos de datos avanzados:** No hay JSONB, arrays, etc.
- ❌ **Sin transacciones distribuidas:** No soporta microservicios futuros
- ⚠️ Archivo único `spm.db` → single point of failure

#### 4. **Testing y CI/CD**
- ❌ Sin pipeline CI/CD automatizado
- ❌ Tests mínimos (solo `test_planner_integration.py`)
- ❌ Sin coverage reporting
- ❌ Sin linting automático (flake8, black, mypy)
- ❌ Sin environment separation (dev/staging/prod)

#### 5. **Escalabilidad**
- ❌ **Deployment manual:** Sin Docker Compose production-ready
- ❌ **Sin balanceador de carga:** Aplicación single-instance
- ❌ **Sin caché:** Redis/Memcached no implementado
- ❌ **Sin CDN:** Archivos estáticos servidos desde Flask

#### 6. **Mantenibilidad**
- ❌ **Código legacy:** 2 endpoints marcados como `@legacy_endpoint`
- ❌ **Dependencias no usadas:** `scikit-learn` comentado pero presente
- ❌ **Logs dispersos:** Sin centralización (Datadog, Sentry)
- ❌ **Documentación fragmentada:** 50+ archivos en `docs/` sin índice

---

## Decisión

Migrar a una **arquitectura desacoplada v2.0** con:

### 1. **Monorepo con separación clara**

```
SPMv1.0/
├── backend_v2/          # API REST pura (FastAPI o Flask-RESTful)
│   ├── api/             # Endpoints REST organizados por dominio
│   ├── domain/          # Modelos de dominio (Entities, Value Objects)
│   ├── application/     # Casos de uso (Services, Use Cases)
│   ├── infrastructure/  # DB, cache, external APIs
│   ├── ports/           # Interfaces (abstracciones)
│   └── adapters/        # Implementaciones de ports
│
├── frontend_v2/         # SPA (React, Vue, o Svelte)
│   ├── src/
│   │   ├── components/  # Componentes reutilizables
│   │   ├── pages/       # Páginas SPA
│   │   ├── services/    # API clients
│   │   ├── store/       # Estado global (Redux, Pinia, etc.)
│   │   └── utils/       # Helpers
│   └── public/          # Assets estáticos
│
├── database/            # Migraciones y schemas
│   ├── migrations/      # Alembic o similares
│   └── seeds/           # Datos de prueba
│
├── infra/               # Docker, K8s, Terraform
│   ├── docker/
│   ├── k8s/
│   └── terraform/
│
└── docs/
    ├── adr/             # Architecture Decision Records
    ├── api/             # Especificación OpenAPI
    └── guides/          # Guías de desarrollo
```

### 2. **Backend v2: API REST pura**

**Framework candidato:** FastAPI (alternativa: Flask-RESTful)

**Razones:**
- ✅ **Auto-documentación:** OpenAPI/Swagger out-of-the-box
- ✅ **Validación automática:** Pydantic models integrados
- ✅ **Async support:** Para operaciones I/O intensivas
- ✅ **Type hints:** Mejora mantenibilidad y IDE support
- ✅ **Performance:** 2-3x más rápido que Flask tradicional

**Arquitectura de capas:**
```python
# Ejemplo: Endpoint de solicitudes
# api/solicitudes.py
@router.post("/solicitudes", response_model=SolicitudResponse)
async def create_solicitud(
    payload: CreateSolicitudDTO,
    service: SolicitudesService = Depends(get_solicitudes_service)
):
    return await service.create(payload)

# application/services/solicitudes_service.py
class SolicitudesService:
    def __init__(self, repo: SolicitudesRepository, planner: PlannerPort):
        self.repo = repo
        self.planner = planner  # ← Inyección de dependencias
    
    async def create(self, dto: CreateSolicitudDTO) -> Solicitud:
        # Lógica de negocio
        solicitud = Solicitud.from_dto(dto)
        await self.repo.save(solicitud)
        await self.planner.assign_to_queue(solicitud)  # ← Interfaz
        return solicitud

# ports/planner_port.py (Interfaz)
class PlannerPort(ABC):
    @abstractmethod
    async def assign_to_queue(self, solicitud: Solicitud) -> None:
        pass
    
    @abstractmethod
    async def optimize(self, solicitud_id: int) -> OptimizationResult:
        pass

# adapters/planner_adapter.py (Implementación)
class PlannerAdapter(PlannerPort):
    async def assign_to_queue(self, solicitud: Solicitud) -> None:
        # Implementación real con scipy, algoritmos, etc.
        pass
```

### 3. **Frontend v2: SPA (Single Page Application)**

**Framework candidato:** Vue 3 (alternativas: React, Svelte)

**Razones:**
- ✅ **Progresividad:** Migración incremental posible
- ✅ **Composable API:** Código más limpio y reutilizable
- ✅ **Ecosystem maduro:** Pinia (state), Vue Router, Vite
- ✅ **TypeScript support:** Mejora DX y refactorings
- ✅ **Menor curva de aprendizaje** vs React (para equipo actual)

**Estructura:**
```
frontend_v2/src/
├── components/
│   ├── common/          # Botones, inputs, modals
│   ├── solicitudes/     # Componentes de dominio
│   └── planner/         # Módulo planificador
├── pages/
│   ├── LoginPage.vue
│   ├── DashboardPage.vue
│   ├── SolicitudesPage.vue
│   └── PlannerPage.vue
├── services/
│   ├── api.ts           # Axios instance configurada
│   ├── solicitudes.ts   # Cliente API solicitudes
│   └── auth.ts          # Cliente API auth
├── store/
│   ├── auth.ts          # Pinia store autenticación
│   └── solicitudes.ts   # Pinia store solicitudes
└── router/
    └── index.ts         # Vue Router config
```

### 4. **Módulo Planner: Desacoplamiento por interfaz**

**Contrato definido (PlannerPort):**

```python
# backend_v2/ports/planner_port.py
from abc import ABC, abstractmethod
from typing import List
from ..domain.entities import Solicitud, Material, OptimizationResult

class PlannerPort(ABC):
    """
    Puerto para el módulo de planificación.
    Permite desacoplar lógica de negocio de implementación de algoritmos.
    """
    
    @abstractmethod
    async def assign_to_queue(self, solicitud: Solicitud) -> None:
        """Asignar solicitud a cola de planificación."""
        pass
    
    @abstractmethod
    async def get_queue(self, planner_id: str) -> List[Solicitud]:
        """Obtener cola de solicitudes de un planificador."""
        pass
    
    @abstractmethod
    async def optimize(
        self, 
        solicitud_id: int, 
        constraints: dict
    ) -> OptimizationResult:
        """
        Optimizar solicitud considerando:
        - Inventario disponible
        - Costos de transporte
        - Lead times
        - Restricciones de almacén
        """
        pass
    
    @abstractmethod
    async def suggest_materials(
        self, 
        solicitud_id: int, 
        partial_description: str
    ) -> List[Material]:
        """Sugerir materiales basados en descripción parcial."""
        pass
    
    @abstractmethod
    async def calculate_criticality(
        self, 
        solicitud: Solicitud
    ) -> str:
        """Calcular criticidad (Alta/Media/Baja) basado en reglas."""
        pass
```

**Beneficios:**
- ✅ **Testeable:** Mock fácil para unit tests
- ✅ **Intercambiable:** Cambiar algoritmo sin tocar lógica de negocio
- ✅ **Portable:** Planner puede ser microservicio futuro
- ✅ **Documentado:** Interface sirve como contrato

### 5. **Base de Datos: PostgreSQL en producción**

**Migración gradual:**
```
FASE 2-3: SQLite (desarrollo) → Alembic migrations
FASE 4-5: PostgreSQL (staging) → Testing con Postgres
FASE 6+: PostgreSQL (producción) → Migración de datos real
```

**Razones para PostgreSQL:**
- ✅ **Concurrencia:** MVCC para writes simultáneos
- ✅ **Replicación:** Streaming replication out-of-the-box
- ✅ **JSONB:** Para metadatos y configuraciones dinámicas
- ✅ **Full-text search:** Para búsqueda de materiales
- ✅ **Partitioning:** Para tablas grandes (históricos)
- ✅ **Extensions:** PostGIS (futuro), pg_stat_statements (monitoring)

**Plan de migración de datos:**
```python
# Ejemplo de migración
# database/migrations/001_sqlite_to_postgres.py

def migrate_solicitudes():
    # 1. Export SQLite to CSV
    sqlite_conn = sqlite3.connect('spm.db')
    df = pd.read_sql_query("SELECT * FROM solicitudes", sqlite_conn)
    df.to_csv('solicitudes_export.csv', index=False)
    
    # 2. Import to Postgres
    pg_conn = psycopg2.connect(DATABASE_URL)
    cursor = pg_conn.cursor()
    with open('solicitudes_export.csv', 'r') as f:
        cursor.copy_expert(
            "COPY solicitudes FROM STDIN WITH CSV HEADER",
            f
        )
    pg_conn.commit()
```

---

## Alternativas Consideradas

### Alternativa 1: Mantener SQLite + Mejorar v1.0

**Propuesta:**
- Refactorizar `app.js` a módulos ES6
- Agregar tests unitarios
- Mantener SQLite con backups manuales
- Mejorar seguridad (CSRF, rate limiting)

**Descartada porque:**
- ❌ **SQLite no escala:** Write locks bloquean toda la DB
- ❌ **Acoplamiento persiste:** Frontend sigue mezclado con backend
- ❌ **Deuda técnica crece:** Sin separación clara de capas
- ❌ **Dificulta microservicios:** SQLite no soporta conexiones remotas

### Alternativa 2: Mantener Server-Side Rendering (SSR)

**Propuesta:**
- Usar Jinja2 templates + HTMX para interactividad
- Mantener estructura multi-página HTML
- Mejorar Progressive Enhancement

**Descartada porque:**
- ❌ **Experiencia de usuario inferior:** Recargas de página completas
- ❌ **Dificulta estado compartido:** Session storage vs in-memory store
- ❌ **Menos reutilizable:** Componentes HTML duplicados
- ❌ **Testing más complejo:** E2E tests vs component tests
- ❌ **Mobile no friendly:** Sin app móvil futura (React Native/Capacitor)

### Alternativa 3: Microservicios desde el inicio

**Propuesta:**
- Separar en servicios: auth-service, solicitudes-service, planner-service
- Usar API Gateway + Service Mesh
- Event-driven con Kafka/RabbitMQ

**Descartada porque:**
- ❌ **Complejidad prematura:** Equipo pequeño, overhead grande
- ❌ **Costos de infraestructura:** K8s, message brokers, monitoring
- ❌ **Debugging difícil:** Distributed tracing necesario
- ❌ **No necesario aún:** Tráfico actual no justifica

**Nota:** Arquitectura v2.0 permite migración futura a microservicios gracias a **Ports & Adapters**.

---

## Consecuencias

### Positivas ✅

1. **Mayor claridad arquitectónica**
   - Separación frontend/backend obvia
   - Capas bien definidas (domain, application, infrastructure)
   - Módulos con responsabilidades únicas

2. **Mejores tests**
   - Unit tests con mocks de interfaces (PlannerPort)
   - Integration tests con API REST
   - E2E tests con Playwright/Cypress

3. **CI/CD más simple**
   - Backend y frontend pueden desplegarse independientemente
   - Tests paralelos (backend Python, frontend JS)
   - Docker multi-stage builds optimizados

4. **Developer Experience mejorado**
   - Hot reload en desarrollo (Vite para frontend, uvicorn para backend)
   - Type hints everywhere (Python + TypeScript)
   - Auto-documentación (OpenAPI + Storybook)

5. **Escalabilidad futura**
   - Backend API puede escalar horizontalmente (load balancer)
   - Frontend estático puede servirse desde CDN
   - Postgres permite replicación read replicas

### Negativas ⚠️

1. **Migración de datos compleja**
   - SQLite → Postgres requiere validación exhaustiva
   - Downtime necesario (o migración dual-write)
   - Riesgo de pérdida de datos si falla

2. **Curva de aprendizaje**
   - Equipo debe aprender FastAPI/Vue
   - Ports & Adapters pattern nuevo para algunos
   - Async/await en Python (si se usa FastAPI)

3. **Esfuerzo de desarrollo**
   - Reescribir frontend completo (~3-4 sprints)
   - Reescribir backend API (~2-3 sprints)
   - Testing exhaustivo (~1-2 sprints)

4. **Mantenimiento dual temporal**
   - v1.0 debe mantenerse mientras se desarrolla v2.0
   - Bugfixes deben aplicarse a ambas versiones
   - Documentación duplicada

5. **Costos de infraestructura**
   - Postgres (managed DB) más caro que SQLite
   - CDN para frontend estático (Cloudflare/AWS)
   - Monitoring tools (Datadog, Sentry) tienen costos

---

## Roadmap de Migración

### FASE 1: Limpieza Controlada ✅ **COMPLETADO**
- Externalizar secretos a `.env`
- Marcar endpoints legacy
- Archivar código desactivado (form_intelligence)
- Remover dependencias no usadas

### FASE 2: ADR y Arquitectura Target ⏳ **EN PROGRESO**
- Crear ADR-001 (este documento)
- Definir contrato PlannerPort
- Diseñar estructura backend_v2/frontend_v2

### FASE 3: Scaffold Backend v2
- Crear estructura de carpetas
- Configurar FastAPI + Alembic
- Implementar capa de dominio (entities)
- Migrar 2-3 endpoints (auth, solicitudes)

### FASE 4: Scaffold Frontend v2
- Configurar Vite + Vue 3 + TypeScript
- Crear componentes base (Button, Input, Modal)
- Implementar LoginPage + DashboardPage
- Conectar con backend v2

### FASE 5: Migrar Módulo Planner
- Implementar PlannerPort interface
- Migrar algoritmos de optimización
- Tests unitarios con mocks
- Integration tests con API

### FASE 6: Migración de Datos
- Crear scripts SQLite → Postgres
- Testing en staging con Postgres
- Validación de integridad de datos
- Plan de rollback

### FASE 7: CI/CD + Deployment
- GitHub Actions pipelines
- Docker Compose production
- Monitoring (Datadog/Sentry)
- Rollout gradual (canary deployment)

### FASE 8: Sunset v1.0
- Redirects permanentes v1 → v2
- Deprecation notices
- Backup final de v1.0
- Documentación de migración

---

## Aprobación

**Aprobado por:** Equipo de desarrollo  
**Fecha de aprobación:** 13 de noviembre de 2025  
**Próxima revisión:** FASE 5 (antes de migración de planner)

---

## Referencias

- [FASE 1: Informe de Cambios](../FASE1_INFORME_CAMBIOS.md)
- [PLANNER Architecture](../PLANNER_ARCHITECTURE.md)
- [Architecture v1.0](../ARCHITECTURE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Guide](https://vuejs.org/guide/)
- [PostgreSQL vs SQLite](https://www.postgresql.org/about/)
- [Ports & Adapters (Hexagonal Architecture)](https://alistair.cockburn.us/hexagonal-architecture/)
