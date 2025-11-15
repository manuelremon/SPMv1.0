# Precondiciones y Convenciones - SPM v2.0

## 📋 Regla de Oro de Migración

> **Copia/mueve por módulo con pruebas; no "big-bang".**  
> **Mantén v1.0 funcional mientras sube v2.0 en paralelo.**

---

## 🌿 Branching Strategy

### Branches Principales

- **`main`**: Código estable (solo v1.0 por ahora)
- **`feat/spm-v2/<fase>`**: Trabajo por fase (ej: `feat/spm-v2/fase-1-backend`)
- **`chore/cleanup/<tema>`**: Limpiezas puntuales (ej: `chore/cleanup/deps`)

### Convenciones de Commits

```
feat(v2): [fase] descripción
fix(v2): [fase] descripción
refactor(v2): [fase] descripción
docs(v2): descripción
test(v2): [fase] descripción
```

### Ejemplo

```bash
git checkout -b feat/spm-v2/fase-1-backend
git commit -m "feat(v2): [fase-1] estructura base backend"
git push origin feat/spm-v2/fase-1-backend
```

---

## 📁 Estructura Meta (Target)

```
spm/
├── backend_v2/              # Backend independiente (API REST pura)
│   ├── app.py               # Aplicación Flask
│   ├── core/                # Configuración, DB, seguridad, JWT
│   │   ├── config.py        # Configuración centralizada
│   │   ├── db.py            # PostgreSQL (ORM)
│   │   ├── security.py      # Seguridad (CSRF, rate limiting)
│   │   └── jwt_manager.py   # Gestión de JWT
│   ├── models/              # Modelos ORM (SQLAlchemy)
│   ├── schemas/             # Schemas Pydantic (validación)
│   ├── services/            # Lógica de negocio
│   ├── routes/              # Blueprints (solo HTTP handlers)
│   ├── tests/               # Tests automáticos
│   ├── pyproject.toml       # Dependencias Python
│   └── Dockerfile           # Docker para backend
│
├── frontend_v2/             # Frontend desacoplado (SPA)
│   ├── src/
│   │   ├── pages/           # Páginas principales
│   │   ├── components/      # Componentes modulares
│   │   ├── services/        # Servicios API (fetch/axios)
│   │   └── store/           # Store para estado global
│   ├── vite.config.js       # Configuración Vite
│   ├── package.json         # Dependencias Node.js
│   └── Dockerfile           # Docker para frontend
│
├── infra/                   # Infraestructura
│   ├── docker-compose.dev.yml    # Docker Compose desarrollo
│   ├── docker-compose.prod.yml   # Docker Compose producción
│   └── nginx.conf         # Nginx (reverse proxy)
│
├── .github/workflows/       # CI/CD
│   └── ci.yml               # Pipeline CI/CD
│
└── docs/
    ├── v2.0/                # Documentación v2.0
    │   ├── PLAN_MAESTRO.md  # Plan maestro (este documento)
    │   └── adr/             # Architecture Decision Records
    │       └── 001-architecture.md
    └── ...                  # Documentación v1.0 (mantener)
```

---

## 🔄 Estrategia de Migración

### Principios

1. **Migración Modular**: Mover por módulo, no todo de golpe
2. **Pruebas Continuas**: Cada módulo debe tener tests antes de migrar
3. **Paralelo**: v1.0 sigue funcionando mientras se desarrolla v2.0
4. **Reversibilidad**: Cada cambio debe ser reversible

### Proceso

1. **Análisis**: Identificar módulo a migrar
2. **Planificación**: Definir qué se migra y cómo
3. **Implementación**: Crear código en v2.0
4. **Pruebas**: Tests unitarios e integración
5. **Validación**: Comparar funcionalidad con v1.0
6. **Documentación**: Actualizar ADR y docs

---

## 🛠️ Tecnologías Target

### Backend

- **Framework**: Flask 3.1+
- **ORM**: SQLAlchemy 2.0+
- **Validación**: Pydantic 2.0+
- **BD**: PostgreSQL 14+
- **Autenticación**: JWT (PyJWT)
- **Seguridad**: CSRF, Rate Limiting, CORS
- **Tests**: Pytest, pytest-cov

### Frontend

- **Build Tool**: Vite 5.0+
- **Lenguaje**: JavaScript/TypeScript
- **HTTP Client**: Axios o Fetch API
- **Routing**: Client-side routing
- **Estado**: Store global (simple o Redux)
- **Tests**: Jest, Vitest

### Infraestructura

- **Contenedores**: Docker, Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **CI/CD**: GitHub Actions
- **BD**: PostgreSQL (contenedor)

---

## 📝 Convenciones de Código

### Python

- **Estilo**: PEP 8
- **Type Hints**: Sí (Python 3.11+)
- **Docstrings**: Google style
- **Formateo**: Black
- **Linting**: Ruff

### JavaScript

- **Estilo**: ESLint (config estándar)
- **Type Checking**: TypeScript (opcional)
- **Formateo**: Prettier
- **Linting**: ESLint

---

## 🧪 Testing

### Backend

- **Unitarios**: Pytest
- **Integración**: Pytest + Flask Test Client
- **Cobertura**: pytest-cov (objetivo: 80%+)

### Frontend

- **Unitarios**: Jest/Vitest
- **Integración**: Jest + Testing Library
- **E2E**: Playwright (opcional)

---

## 📚 Documentación

### ADR (Architecture Decision Records)

- `docs/v2.0/adr/001-architecture.md` - Arquitectura general
- `docs/v2.0/adr/002-database.md` - Decisiones de BD
- `docs/v2.0/adr/003-security.md` - Decisiones de seguridad
- etc.

### Formato ADR

```markdown
# ADR-XXX: Título

## Estado
[Aceptado | Rechazado | Propuesto]

## Contexto
Descripción del problema/necesidad

## Decisión
Qué se decidió y por qué

## Consecuencias
Implicaciones positivas y negativas
```

---

## 🚀 Entregables por Fase

Cada fase debe incluir:

1. **Código**: Implementación funcional
2. **Tests**: Tests unitarios e integración
3. **Documentación**: ADR y docs actualizadas
4. **Validación**: Comparación con v1.0
5. **Deploy**: Docker Compose funcional

---

## ✅ Checklist de Validación

Antes de marcar una fase como completa:

- [ ] Código implementado y funcional
- [ ] Tests pasando (80%+ cobertura)
- [ ] Documentación actualizada
- [ ] ADR creado/actualizado
- [ ] Docker Compose funcional
- [ ] Validación con v1.0
- [ ] Code review aprobado

---

## 📅 Timeline (Estimado)

- **Fase 1**: Backend Base (2-3 semanas)
- **Fase 2**: Frontend Base (2-3 semanas)
- **Fase 3**: Autenticación (1-2 semanas)
- **Fase 4**: Solicitudes (2-3 semanas)
- **Fase 5**: Planificación (2-3 semanas)
- **Fase 6**: Reportes (1-2 semanas)
- **Fase 7**: Infraestructura (1-2 semanas)
- **Fase 8**: Migración y Deploy (2-3 semanas)

**Total estimado**: 13-21 semanas (3-5 meses)

---

## 🔗 Referencias

- [Arquitectura v2.0](./adr/001-architecture.md)
- [Plan Maestro](./PLAN_MAESTRO.md)
- [Auditoría v1.0](../../INFORME_AUDITORIA.md)

---

**Última actualización**: 2025-01-27

