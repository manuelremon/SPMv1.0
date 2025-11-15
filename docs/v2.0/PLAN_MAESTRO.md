# PLAN MAESTRO DE RECONSTRUCCIÓN - SPM v2.0

## 🎯 Visión Final de SPM v2.0 (TARGET)

### ✅ Backend Independiente (API REST pura)
- Flask + Blueprints
- JWT
- CORS
- PostgreSQL
- Servicios → Lógica de negocio
- Modelos → Pydantic y ORM
- Rutas → Sólo HTTP handlers
- Tests automáticos

### ✅ Frontend Desacoplado (SPA)
- Vite + JS/TS
- Componentes modulares
- Fetch/axios
- Routing de lado del cliente
- Store para estado global
- Tests con Jest

### ✅ Planner Modular Integrado
- Importable como paquete
- Tests de algoritmos
- Flujo claro con backend

### ✅ Infra Lista para Deploy
- Docker
- Postgres
- Nginx
- CI/CD

---

## 📋 Precondiciones y Convenciones

Ver [00_PRECONDICIONES_CONVENCIONES.md](./00_PRECONDICIONES_CONVENCIONES.md) para detalles completos.

### Regla de Oro
> **Copia/mueve por módulo con pruebas; no "big-bang".**  
> **Mantén v1.0 funcional mientras sube v2.0 en paralelo.**

### Branching
- `main`: estable
- `feat/spm-v2/<fase>`: trabajo por fase
- `chore/cleanup/<tema>`: limpiezas puntuales

---

## 🗺️ Fases del Plan

### Fase 1: Backend Base
**Objetivo**: Crear estructura base del backend con Flask, PostgreSQL y configuración.

### Fase 2: Frontend Base
**Objetivo**: Crear estructura base del frontend con Vite y componentes modulares.

### Fase 3: Autenticación
**Objetivo**: Implementar autenticación JWT completa (login, logout, refresh).

### Fase 4: Solicitudes
**Objetivo**: Migrar módulo de solicitudes (CRUD, aprobación, cancelación).

### Fase 5: Planificación
**Objetivo**: Integrar módulo de planificación con algoritmos de optimización.

### Fase 6: Reportes
**Objetivo**: Implementar reportes y exportación (Excel, PDF).

### Fase 7: Infraestructura
**Objetivo**: Configurar Docker, Nginx, CI/CD y deployment.

### Fase 8: Migración y Deploy
**Objetivo**: Migrar datos de v1.0 a v2.0 y deployar a producción.

---

## 📚 Documentación

- [Precondiciones y Convenciones](./00_PRECONDICIONES_CONVENCIONES.md)
- [ADR-001: Arquitectura General](./adr/001-architecture.md)
- [Auditoría v1.0](../../INFORME_AUDITORIA.md)

---

**Última actualización**: 2025-01-27

