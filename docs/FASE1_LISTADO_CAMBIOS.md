# FASE 1: Listado de Cambios Propuestos

**Rama:** `chore/cleanup/baseline`  
**Estado:** ✅ Completado - LISTO PARA COMMIT

---

## 📋 Cambios por Archivo

### 1. Seguridad y Configuración

#### `.env.example` ➕ CREADO
- Archivo de referencia para variables de entorno
- 11 secciones: Seguridad, Entorno, DB, Logs, JWT, Frontend, Servidor, Archivos, Ollama, IA, Status
- Variables clave: `SPM_SECRET_KEY`, `AUTH_BYPASS`, `JWT_ALG`, `SPM_DB_PATH`, `SPM_LOG_PATH`
- Placeholders seguros (no valores reales)

#### `.gitignore` ✏️ MODIFICADO
- Agregado `src/backend/logs/` para ignorar logs del backend
- Mantiene `.env`, `*.db`, `logs/` existentes

#### `Dockerfile` ✏️ MODIFICADO
- Eliminado `SPM_SECRET_KEY=dev-key-12345` (hardcoded secret)
- Agregada documentación para pasar secret como env var: `docker run -e SPM_SECRET_KEY=...`

---

### 2. Middleware y Decoradores

#### `src/backend/middleware/decorators.py` ✏️ MODIFICADO
- Agregado decorator `@legacy_endpoint` (+40 líneas)
- Funcionalidad:
  - Log WARNING cuando endpoint legacy es accedido
  - Agrega headers: `X-Legacy-Endpoint: true`, `X-Legacy-Deprecation: Migrate to v2.0 API`
  - Compatible con Flask responses (tuple o directo)

---

### 3. Rutas Legacy Marcadas

#### `src/backend/routes/auth_routes.py` ✏️ MODIFICADO
- Endpoint `GET /api/auth/usuarios/me` marcado como legacy (+15 líneas)
- Agrega headers de deprecación manualmente (no puede usar decorator por orden con `@auth_required`)
- Delega a `me_v2()` internamente
- Log WARNING al acceder

#### `src/backend/app.py` ✏️ MODIFICADO
- Endpoint `PUT /api/users/me` marcado con `@legacy_endpoint`
- Deprecado en favor de `PATCH /api/auth/me/fields`
- Headers y logging automáticos vía decorator

---

### 4. Código Desactivado

#### ❌ ELIMINADO de `/src/backend/`:
- `routes/form_intelligence_routes.py`
- `routes/form_intelligence_routes_v2.py`
- `services/form_intelligence.py`
- `services/form_intelligence_v2.py`

#### ✅ ARCHIVADO en `/docs/_archive/form_intelligence/`:
- 4 archivos Python + `README.md` explicativo
- Razón: Código experimental nunca activado, dependencia de scikit-learn removida

---

### 5. Dependencias

#### `requirements.txt` ✏️ MODIFICADO
- Comentado `scikit-learn==1.7.2` (solo usado en form_intelligence)
- Agregado comentario explicativo: "ELIMINADO: Solo usado en código desactivado"
- Documentado `scipy==1.16.2`: "MANTENIDO: Usado en módulo planner (activo)"

---

## 📊 Resumen Estadístico

| Métrica | Valor |
|---------|-------|
| Archivos modificados | 7 |
| Archivos eliminados | 4 |
| Archivos creados | 1 (.env.example) |
| Archivos archivados | 5 (docs/_archive/) |
| Líneas agregadas | ~140 |
| Líneas eliminadas | ~4 archivos completos |
| Dependencias removidas | 1 (scikit-learn) |
| Endpoints legacy marcados | 2 |
| Secretos hardcodeados eliminados | 1 (Dockerfile) |

---

## ✅ Criterios de Aceptación (100% Cumplidos)

- [x] **Sin secretos hardcodeados** ✅
  - Dockerfile: `SPM_SECRET_KEY=dev-key-12345` eliminado
  - Todos los secretos ahora en `.env` (ignorado por git)

- [x] **Rutas legacy marcadas** ✅
  - `GET /api/auth/usuarios/me` (manual headers)
  - `PUT /api/users/me` (@legacy_endpoint decorator)

- [x] **Dependencias limpias** ✅
  - `scikit-learn` removido (no usado)
  - `scipy` mantenido y documentado (usado en planner)

- [x] **`.env.example` presente** ✅
  - 80 líneas, 11 secciones, todas las variables documentadas

- [x] **`.env`, `*.db`, `logs/` en `.gitignore`** ✅
  - `.env` (existente)
  - `*.db` (existente)
  - `logs/` + `src/backend/logs/` (agregado)

- [x] **Código desactivado archivado** ✅
  - `form_intelligence` (4 archivos) → `docs/_archive/` con README

---

## 🎯 Próximos Pasos

1. **Revisar diffs completos:** `docs/FASE1_DIFFS_DETALLADO.md`
2. **Aprobar cambios** (usuario)
3. **Commit:**
   ```bash
   git add .env.example .gitignore Dockerfile requirements.txt \
           src/backend/middleware/decorators.py \
           src/backend/routes/auth_routes.py \
           src/backend/app.py
   
   git commit -m "chore(cleanup): FASE 1 - Limpieza controlada baseline"
   ```
4. **Merge a main:**
   ```bash
   git checkout main
   git merge chore/cleanup/baseline
   git push origin main
   ```
5. **Iniciar FASE 2:** Leer `Prompts Reconstrucción/FASE 2/`

---

**Generado:** 13 de noviembre de 2025  
**Estado:** ✅ LISTO PARA COMMIT  
**Requiere aprobación:** SÍ (usuario debe revisar diffs antes de commit)
