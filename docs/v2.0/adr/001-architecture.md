# ADR-001: Arquitectura General - SPM v2.0

## Estado
**Aceptado** - 2025-01-27

## Contexto

SPM v1.0 tiene una arquitectura acoplada donde:
- Frontend y backend están mezclados
- SQLite no es escalable para producción
- Falta separación clara de responsabilidades
- Tests insuficientes
- Seguridad mejorable

Necesitamos una arquitectura moderna, escalable y segura para SPM v2.0.

## Decisión

Implementar una arquitectura de **microservicios ligeros** con:

### Backend Independiente (API REST pura)

- **Framework**: Flask 3.1+ (ligero, flexible)
- **ORM**: SQLAlchemy 2.0+ (abstracción de BD)
- **Validación**: Pydantic 2.0+ (validación de datos)
- **BD**: PostgreSQL 14+ (escalable, robusta)
- **Autenticación**: JWT (stateless, escalable)
- **Seguridad**: CSRF, Rate Limiting, CORS
- **Tests**: Pytest (unitarios e integración)

**Estructura**:
```
backend_v2/
├── app.py              # Aplicación Flask (factory pattern)
├── core/               # Configuración, DB, seguridad, JWT
├── models/             # Modelos ORM (SQLAlchemy)
├── schemas/            # Schemas Pydantic (validación)
├── services/           # Lógica de negocio (pura)
├── routes/             # Blueprints (solo HTTP handlers)
└── tests/              # Tests automáticos
```

### Frontend Desacoplado (SPA)

- **Build Tool**: Vite 5.0+ (rápido, moderno)
- **Lenguaje**: JavaScript/TypeScript
- **HTTP Client**: Axios o Fetch API
- **Routing**: Client-side routing
- **Estado**: Store global (simple o Redux)
- **Tests**: Jest/Vitest

**Estructura**:
```
frontend_v2/
├── src/
│   ├── pages/          # Páginas principales
│   ├── components/     # Componentes modulares
│   ├── services/       # Servicios API (fetch/axios)
│   └── store/          # Store para estado global
├── vite.config.js
└── package.json
```

### Infraestructura

- **Contenedores**: Docker, Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **CI/CD**: GitHub Actions
- **BD**: PostgreSQL (contenedor)

**Estructura**:
```
infra/
├── docker-compose.dev.yml   # Desarrollo
├── docker-compose.prod.yml  # Producción
└── nginx.conf               # Nginx config
```

## Principios de Diseño

### 1. Separación de Responsabilidades

- **Routes**: Solo HTTP handling (request/response)
- **Services**: Lógica de negocio (pura, testable)
- **Models**: Acceso a datos (ORM)
- **Schemas**: Validación de datos (Pydantic)

### 2. Independencia

- Frontend y backend completamente separados
- Comunicación solo vía API REST
- Sin acoplamiento directo

### 3. Escalabilidad

- PostgreSQL para alta concurrencia
- Stateless backend (JWT)
- Frontend puede ser CDN

### 4. Seguridad

- JWT para autenticación
- CSRF protection
- Rate limiting
- CORS configurado
- Validación de entrada (Pydantic)

### 5. Testabilidad

- Tests unitarios para servicios
- Tests de integración para rutas
- Tests E2E para flujos completos
- Cobertura objetivo: 80%+

## Flujo de Datos

```
Frontend (SPA)
    ↓
    HTTP Request (JSON)
    ↓
Nginx (Reverse Proxy)
    ↓
Backend (Flask API)
    ↓
Routes (HTTP Handlers)
    ↓
Services (Business Logic)
    ↓
Models (ORM)
    ↓
PostgreSQL
```

## Consecuencias

### Positivas

- ✅ Escalabilidad: PostgreSQL soporta alta concurrencia
- ✅ Mantenibilidad: Separación clara de responsabilidades
- ✅ Testabilidad: Servicios puros, fáciles de testear
- ✅ Seguridad: JWT stateless, CSRF, rate limiting
- ✅ Flexibilidad: Frontend y backend independientes
- ✅ Deploy: Puede deployarse por separado

### Negativas

- ⚠️ Complejidad: Más componentes que mantener
- ⚠️ Latencia: Una llamada extra (Nginx)
- ⚠️ Desarrollo: Más setup inicial
- ⚠️ Migración: Requiere migración de datos

### Mitigaciones

- **Complejidad**: Docker Compose simplifica setup
- **Latencia**: Nginx es muy rápido (despreciable)
- **Desarrollo**: Scripts de setup automatizados
- **Migración**: Scripts de migración de datos

## Alternativas Consideradas

### 1. Monolito Acoplado (v1.0 actual)

**Rechazado porque**:
- No escalable
- Difícil de mantener
- Tests insuficientes

### 2. Microservicios Complejos

**Rechazado porque**:
- Overhead innecesario
- Complejidad excesiva
- No necesario para el tamaño del proyecto

### 3. Serverless (AWS Lambda, etc.)

**Rechazado porque**:
- Vendor lock-in
- Complejidad de deployment
- Costos variables

## Referencias

- [Flask Best Practices](https://flask.palletsprojects.com/en/3.0.x/patterns/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 2.0](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Última actualización**: 2025-01-27

