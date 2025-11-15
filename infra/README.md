# Infraestructura - SPM v2.0

Configuración de infraestructura (Docker, Nginx, CI/CD) para SPM v2.0.

## 🏗️ Estructura

```
infra/
├── docker-compose.dev.yml   # Docker Compose desarrollo
├── docker-compose.prod.yml  # Docker Compose producción
└── nginx.conf               # Nginx (reverse proxy)
```

## 🚀 Tecnologías

- **Contenedores**: Docker, Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **CI/CD**: GitHub Actions
- **BD**: PostgreSQL (contenedor)

## 📚 Documentación

- [Plan Maestro](../docs/v2.0/PLAN_MAESTRO.md)
- [ADR-001: Arquitectura](../docs/v2.0/adr/001-architecture.md)
- [Precondiciones y Convenciones](../docs/v2.0/00_PRECONDICIONES_CONVENCIONES.md)

---

**Estado**: Pendiente (Fase 7)

