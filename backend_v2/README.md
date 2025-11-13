# Backend v2.0 - SPM

Backend independiente (API REST pura) para SPM v2.0.

## 🏗️ Estructura

```
backend_v2/
├── app.py              # Aplicación Flask (factory pattern)
├── core/               # Configuración, DB, seguridad, JWT
│   ├── config.py       # Configuración centralizada
│   ├── db.py           # PostgreSQL (ORM)
│   ├── security.py     # Seguridad (CSRF, rate limiting)
│   └── jwt_manager.py  # Gestión de JWT
├── models/             # Modelos ORM (SQLAlchemy)
├── schemas/            # Schemas Pydantic (validación)
├── services/           # Lógica de negocio (pura)
├── routes/             # Blueprints (solo HTTP handlers)
├── tests/              # Tests automáticos
├── pyproject.toml      # Dependencias Python
└── Dockerfile          # Docker para backend
```

## 🚀 Tecnologías

- **Framework**: Flask 3.1+
- **ORM**: SQLAlchemy 2.0+
- **Validación**: Pydantic 2.0+
- **BD**: PostgreSQL 14+
- **Autenticación**: JWT (PyJWT)
- **Seguridad**: CSRF, Rate Limiting, CORS
- **Tests**: Pytest, pytest-cov

## 📚 Documentación

- [Plan Maestro](../docs/v2.0/PLAN_MAESTRO.md)
- [ADR-001: Arquitectura](../docs/v2.0/adr/001-architecture.md)
- [Precondiciones y Convenciones](../docs/v2.0/00_PRECONDICIONES_CONVENCIONES.md)

---

**Estado**: En desarrollo (Fase 1)

