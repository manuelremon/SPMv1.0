# FASE 1: Plan de Acción - Limpieza Controlada

## 📋 Resumen de Cambios Propuestos

### 1. Secret Key Hardcodeada

**Archivo**: `Dockerfile`
- **Problema**: `SPM_SECRET_KEY=dev-key-12345` hardcodeada
- **Acción**: Eliminar línea, usar variable de entorno
- **Riesgo**: Bajo (solo afecta Docker)

### 2. .env.example

**Archivo**: `.env.example` (nuevo)
- **Acción**: Crear archivo con todas las variables necesarias
- **Variables**: 
  - `SPM_SECRET_KEY`
  - `FRONTEND_ORIGIN`
  - `DB_PATH`
  - `LOG_PATH`
  - `OLLAMA_ENDPOINT`
  - `MAX_CONTENT_LENGTH`
  - `JWT_ALG`
  - `JWT_TTL`
  - `AUTH_BYPASS`
  - `SPM_ENV`
  - `SPM_DEBUG`

### 3. .gitignore

**Archivo**: `.gitignore`
- **Acción**: Verificar/actualizar para ignorar:
  - `.env` (ya existe)
  - `*.db` (ya existe)
  - `logs/` (ya existe)
  - Agregar `src/backend/logs/` si es necesario

### 4. Rutas Legacy

**Archivos**: 
- `src/backend/app.py` - `/api/users/me`
- `src/backend/routes/auth_routes.py` - `/api/auth/usuarios/me`

**Acción**: 
- Crear decorator `@legacy_endpoint` en `src/backend/middleware/decorators.py`
- Marcar rutas legacy con el decorator
- Agregar header `X-Legacy-Endpoint: true`
- Log warning cuando se use

### 5. Código Desactivado

**Archivos**:
- `src/backend/routes/form_intelligence_routes.py`
- `src/backend/routes/form_intelligence_routes_v2.py`
- `src/backend/services/form_intelligence.py`
- `src/backend/services/form_intelligence_v2.py`

**Acción**: 
- Mover a `docs/_archive/form_intelligence/`
- Crear nota explicativa
- Mantener imports comentados en `app.py` por ahora (para referencia)

### 6. Dependencias No Usadas

**Archivo**: `requirements.txt`
- **scikit-learn**: Solo usado en `ai_service.py` (no activo) - ELIMINAR
- **scipy**: Usado en `src/planner/` (activo) - MANTENER
- **numpy**: Dependencia de pandas/scipy - MANTENER
- **pandas**: Usado en `data_providers.py` (activo) - MANTENER

**Acción**: 
- Eliminar `scikit-learn==1.7.2`
- Eliminar `scipy==1.16.2` si confirmamos que no se usa activamente
- Verificar que `threadpoolctl` (dependencia de scikit-learn) también se puede eliminar

### 7. AUTH_BYPASS

**Archivo**: `src/backend/app.py`
- **Acción**: Mejorar validación para que solo funcione en desarrollo
- **Validación**: 
  - Solo en `SPM_ENV=development`
  - Solo en localhost (127.0.0.1, localhost)
  - Agregar warning log

## 🔍 Análisis Detallado

### Dependencias

**scikit-learn**:
- Usado en: `src/backend/services/ai_service.py`, `src/ai_assistant/embeddings.py`
- Estado: No activo (no se importa en rutas activas)
- Acción: ELIMINAR

**scipy**:
- Usado en: `src/planner/optimization/constraint_builder.py`, `src/planner/scoring/base_scorer.py`
- Estado: ACTIVO (módulo planner está activo)
- Acción: MANTENER

**numpy**:
- Usado en: `src/backend/services/ai_service.py`, dependencia de pandas/scipy
- Estado: Dependencia indirecta necesaria
- Acción: MANTENER

**pandas**:
- Usado en: `src/backend/services/data_providers.py`
- Estado: ACTIVO
- Acción: MANTENER

### Rutas Legacy

1. **`/api/users/me`** (PUT) - `src/backend/app.py:396`
   - Función: `update_me()`
   - Ruta moderna: `/api/auth/me/fields` (PATCH)
   - Acción: Marcar con `@legacy_endpoint`

2. **`/api/auth/usuarios/me`** (GET) - `src/backend/routes/auth_routes.py:123`
   - Función: `me_legacy()`
   - Ruta moderna: `/api/auth/me` (GET)
   - Acción: Marcar con `@legacy_endpoint`

### Código Desactivado

**form_intelligence_routes.py**:
- Blueprint: `form_intelligence_bp`
- Estado: Comentado en `app.py`
- Acción: Mover a `docs/_archive/form_intelligence/`

**form_intelligence_routes_v2.py**:
- Blueprint: `form_intelligence_v2_bp`
- Estado: Comentado en `app.py`
- Acción: Mover a `docs/_archive/form_intelligence/`

**form_intelligence.py**:
- Servicio: `FormIntelligenceEngine`
- Estado: No usado
- Acción: Mover a `docs/_archive/form_intelligence/`

**form_intelligence_v2.py**:
- Servicio: `FormIntelligenceEngineV2`
- Estado: No usado
- Acción: Mover a `docs/_archive/form_intelligence/`

## ✅ Checklist de Validación

- [ ] Secret key eliminada de Dockerfile
- [ ] .env.example creado
- [ ] .gitignore actualizado
- [ ] Decorator `@legacy_endpoint` creado
- [ ] Rutas legacy marcadas
- [ ] Código desactivado movido a `docs/_archive/`
- [ ] Dependencias no usadas eliminadas
- [ ] AUTH_BYPASS mejorado
- [ ] Tests pasando
- [ ] Documentación actualizada

## 🚀 Próximos Pasos

1. Crear rama `chore/cleanup/baseline`
2. Aplicar cambios uno por uno
3. Verificar que no se rompe nada
4. Ejecutar tests
5. Crear PR con cambios

---

**Fecha**: 2025-01-27  
**Estado**: En progreso

