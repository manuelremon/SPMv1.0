# FASE 1: Cambios Detallados - Limpieza Controlada

## 📋 Resumen de Cambios

### Archivos Modificados

1. **`.env.example`** (nuevo)
   - Creado archivo con todas las variables de entorno necesarias
   - Incluye documentación de cada variable
   - Notas de seguridad y producción

2. **`.gitignore`**
   - Agregado `src/backend/logs/` a la lista de ignorados
   - Ya tenía `.env` y `*.db` ignorados

3. **`Dockerfile`**
   - Eliminada línea `SPM_SECRET_KEY=dev-key-12345`
   - Agregado comentario indicando que debe proporcionarse como variable de entorno
   - Comentario con ejemplo de uso

4. **`requirements.txt`**
   - Eliminado `scikit-learn==1.7.2` (solo usado en código desactivado)
   - Comentado `scipy==1.16.2` con nota de que se mantiene (usado en planner)
   - `threadpoolctl` se mantiene (dependencia de scipy)

5. **`src/backend/app.py`**
   - Importado `legacy_endpoint` de `middleware.decorators`
   - Mejorada validación de `AUTH_BYPASS`:
     - Solo funciona en `SPM_ENV=development`
     - Solo en localhost (127.0.0.1, localhost)
     - Log warning cuando se activa
     - Log error si se intenta usar en producción
   - Marcada ruta legacy `/api/users/me` con `@legacy_endpoint`
   - Actualizados comentarios de `form_intelligence` para reflejar que fue archivado

6. **`src/backend/routes/auth_routes.py`**
   - Marcada ruta legacy `/api/auth/usuarios/me` con headers legacy
   - Agregado log warning cuando se accede a la ruta legacy
   - Agregados headers `X-Legacy-Endpoint` y `X-Legacy-Deprecation`

7. **`src/backend/middleware/decorators.py`**
   - Agregado decorator `@legacy_endpoint`:
     - Agrega header `X-Legacy-Endpoint: true`
     - Agrega header `X-Legacy-Deprecation: Migrate to v2.0 API`
     - Log warning cuando se accede a la ruta
     - Funciona con respuestas tupla (body, status) y respuestas normales

### Archivos Movidos

1. **`src/backend/routes/form_intelligence_routes.py`** → `docs/_archive/form_intelligence/form_intelligence_routes.py`
2. **`src/backend/routes/form_intelligence_routes_v2.py`** → `docs/_archive/form_intelligence/form_intelligence_routes_v2.py`
3. **`src/backend/services/form_intelligence.py`** → `docs/_archive/form_intelligence/form_intelligence.py`
4. **`src/backend/services/form_intelligence_v2.py`** → `docs/_archive/form_intelligence/form_intelligence_v2.py`

### Archivos Creados

1. **`.env.example`** (nuevo)
   - Archivo de ejemplo con todas las variables de entorno

2. **`docs/_archive/form_intelligence/README.md`** (nuevo)
   - Explicación de por qué se movió el código
   - Instrucciones para reactivación si es necesario
   - Notas técnicas

3. **`docs/v2.0/FASE_1_PLAN_ACCION.md`** (nuevo)
   - Plan de acción detallado

4. **`docs/v2.0/FASE_1_RESUMEN.md`** (nuevo)
   - Resumen de cambios completados

5. **`docs/v2.0/FASE_1_CAMBIOS_DETALLADOS.md`** (este archivo)
   - Cambios detallados

## 🔍 Dependencias

### Eliminadas
- `scikit-learn==1.7.2` - Solo usado en código desactivado (form_intelligence)

### Mantenidas
- `scipy==1.16.2` - Usado en módulo planner (activo)
- `threadpoolctl==3.6.0` - Dependencia de scipy
- `numpy==2.3.4` - Dependencia de pandas/scipy
- `pandas==2.3.3` - Usado en `data_providers.py` (activo)

## ✅ Validación

- [x] Secret key eliminada de Dockerfile
- [x] .env.example creado
- [x] .gitignore actualizado
- [x] Decorator `@legacy_endpoint` creado
- [x] Rutas legacy marcadas
- [x] Código desactivado movido a `docs/_archive/`
- [x] Dependencias no usadas eliminadas
- [x] AUTH_BYPASS mejorado
- [x] No hay errores de linter
- [x] Documentación actualizada
- [x] No hay imports rotos

## 🚀 Próximos Pasos

1. Ejecutar tests para verificar que no se rompió nada
2. Verificar que las rutas legacy funcionan correctamente
3. Verificar que AUTH_BYPASS solo funciona en desarrollo
4. Crear PR con los cambios
5. Continuar con FASE 2

## 📝 Notas

- `scipy` se mantiene porque se usa en `src/planner/` (módulo activo)
- `threadpoolctl` se mantiene porque es dependencia de `scipy`
- El código de `form_intelligence` está preservado en `docs/_archive/` para referencia futura
- Las rutas legacy siguen funcionando pero ahora están marcadas para deprecación
- AUTH_BYPASS ahora tiene validación estricta para prevenir uso en producción

---

**Fecha**: 2025-01-27  
**Estado**: ✅ Completado  
**Rama**: `chore/cleanup/baseline`

