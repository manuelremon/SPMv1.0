# FASE 1: Diffs Detallados - Cambios por Archivo

**Rama:** `chore/cleanup/baseline`  
**Fecha:** 13 de noviembre de 2025

---

## 📄 Resumen de Cambios

| Archivo | Líneas +/- | Tipo | Descripción |
|---------|-----------|------|-------------|
| `Dockerfile` | +2 -1 | Seguridad | Removido SPM_SECRET_KEY hardcodeado |
| `.env.example` | +80 -72 | Config | Reescritura completa con nuevas vars |
| `.gitignore` | +1 | Seguridad | Agregado `src/backend/logs/` |
| `requirements.txt` | +2 -1 | Deps | scikit-learn comentado, scipy documentado |
| `decorators.py` | +40 | Feature | Agregado decorator `@legacy_endpoint` |
| `auth_routes.py` | +15 | Refactor | Marcado endpoint legacy `/api/auth/usuarios/me` |
| `app.py` | +3 | Refactor | Marcado endpoint legacy `/api/users/me` |

---

## 🔐 1. Dockerfile - Seguridad

### Diff Completo

```diff
--- a/Dockerfile
+++ b/Dockerfile
@@ -7,8 +7,9 @@ ENV PYTHONDONTWRITEBYTECODE=1 \
     PIP_NO_CACHE_DIR=1 \
     PYTHONPATH=/app \
     SPM_ENV=development \
-    SPM_DEBUG=1 \
-    SPM_SECRET_KEY=dev-key-12345
+    SPM_DEBUG=1
+# SPM_SECRET_KEY debe ser proporcionada como variable de entorno en producción
+# Ejemplo: docker run -e SPM_SECRET_KEY=your-secret-key ...
 
 WORKDIR /app
```

### Impacto

- ✅ **Eliminado secreto hardcodeado:** `SPM_SECRET_KEY=dev-key-12345`
- ✅ **Agregada documentación:** Instrucciones para pasar SECRET_KEY como env var
- ✅ **Método seguro:** `docker run -e SPM_SECRET_KEY=...`

---

## ⚙️ 2. .env.example - Configuración

### Diff Completo (líneas relevantes)

```diff
--- a/.env.example
+++ b/.env.example
@@ -1,72 +1,80 @@
-# SPM Configuration - Example (.env.example)
-# Copy this file to .env and update with your values
+# ============================================
+# SPM v1.0 - Variables de Entorno
+# ============================================
+# Copia este archivo a .env y configura los valores segun tu entorno
+# IMPORTANTE: Nunca commitees el archivo .env con valores reales
 
 # ============================================
-# 🔧 BACKEND CONFIGURATION
+# Seguridad
 # ============================================
+SPM_SECRET_KEY=change-me-in-production-generate-secure-key
+AUTH_BYPASS=0
 
-# Flask Environment
+# ============================================
+# Entorno
+# ============================================
 SPM_ENV=development
 SPM_DEBUG=1
-SPM_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
-
-# Database
-SPM_DB_PATH=./spm.db
-SPM_DATABASE_URL=sqlite:///spm.db
 
-# Logging
-SPM_LOG_PATH=./logs
-SPM_LOG_LEVEL=INFO
+# ============================================
+# Base de Datos
+# ============================================
+SPM_DB_PATH=src/backend/data/spm.db
+SPM_UPLOAD_DIR=src/backend/uploads
 
-# File Uploads
-SPM_UPLOAD_DIR=./uploads
-SPM_MAX_UPLOAD_SIZE=16777216  # 16MB in bytes
-
-# CORS
-CORS_ORIGINS=http://localhost:5173,http://localhost:5000,http://127.0.0.1:5173
-
-# JWT Configuration
-JWT_ALGORITHM=HS256
-JWT_EXPIRATION_HOURS=24
+# ============================================
+# Logs
+# ============================================
+SPM_LOG_PATH=src/backend/logs/app.log
 
-# Email Configuration (Optional)
-SMTP_SERVER=smtp.gmail.com
-SMTP_PORT=587
-SMTP_USERNAME=your-email@gmail.com
-SMTP_PASSWORD=your-app-password
-SMTP_FROM=noreply@spm.local
+# ============================================
+# JWT
+# ============================================
+JWT_ALG=HS256
+SPM_ACCESS_TTL=3600
+SPM_TOKEN_TTL=3600
+SPM_COOKIE_NAME=spm_token
+SPM_COOKIE_SAMESITE=Lax
+SPM_COOKIE_SECURE=0
+SPM_COOKIE_DOMAIN=
+SPM_REFRESH_GRACE_PERIOD=300
```

### Cambios Clave

1. **Agregadas variables de seguridad:**
   - `SPM_SECRET_KEY` (con placeholder claro)
   - `AUTH_BYPASS=0` (desactivado por defecto)

2. **Organización por secciones:**
   - Seguridad, Entorno, Base de Datos, Logs, JWT, Frontend, Servidor, Archivos, Ollama, IA, Status Checks

3. **Rutas absolutas corregidas:**
   - `SPM_DB_PATH`: `./spm.db` → `src/backend/data/spm.db`
   - `SPM_LOG_PATH`: `./logs` → `src/backend/logs/app.log`

4. **Nuevas variables documentadas:**
   - `SPM_OLLAMA_URL`, `SPM_OLLAMA_MODEL`
   - `AI_ENABLE`, `AI_EMBED_MODEL`, `AI_PRICE_SMOOTHING`
   - `STATUS_TIMEOUT_MS`, `STATUS_CACHE_SECS`

5. **Eliminadas configuraciones no usadas:**
   - SMTP (email no configurado)
   - DOCKER_REGISTRY (no utilizado)
   - VITE_* (frontend es vanilla HTML, no Vite)

---

## 🛡️ 3. .gitignore - Seguridad

### Diff Completo

```diff
--- a/.gitignore
+++ b/.gitignore
@@ -40,6 +40,7 @@ htmlcov/
 # Logs
 *.log
 logs/
+src/backend/logs/
 
 # Database
 *.db
```

### Impacto

- ✅ **Agregado:** `src/backend/logs/` - previene commit de logs del backend
- ✅ **Mantiene:** `.env`, `*.db`, `logs/` existentes

---

## 📦 4. requirements.txt - Dependencias

### Diff (líneas 33-34)

```diff
--- a/requirements.txt
+++ b/requirements.txt
@@ -30,7 +30,8 @@ pytz==2025.2
 reportlab==4.4.4
 requests==2.32.5
-scikit-learn==1.7.2
+# scikit-learn==1.7.2  # ELIMINADO: Solo usado en código desactivado (form_intelligence)
+scipy==1.16.2  # MANTENIDO: Usado en módulo planner (activo)
```

### Impacto

- ✅ **Eliminado:** `scikit-learn==1.7.2` (solo usado en form_intelligence archivado)
- ✅ **Documentado:** `scipy==1.16.2` sigue activo (usado en planner)
- ✅ **Beneficio:** Reducción de dependencias y tamaño de build

---

## 🔧 5. src/backend/middleware/decorators.py - Decorator Legacy

### Código Agregado (líneas 60-100)

```python
def legacy_endpoint(fn: F) -> F:
    """
    Decorator para marcar endpoints legacy que serán deprecados en v2.0.
    
    Agrega headers:
    - X-Legacy-Endpoint: true
    - X-Legacy-Deprecation: Migrate to v2.0 API
    
    Logs WARNING cuando el endpoint es accedido.
    
    Uso:
        @app.get('/api/old-route')
        @legacy_endpoint
        def old_route():
            return {"message": "This is legacy"}
    """
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        # Log warning cuando se accede
        logger.warning(
            "Legacy endpoint accessed: %s %s - Consider migrating to v2.0",
            request.method,
            request.path
        )
        
        # Ejecutar función original
        response = fn(*args, **kwargs)
        
        # Agregar headers de deprecación
        if isinstance(response, tuple):
            resp = make_response(*response)
        else:
            resp = make_response(response)
        
        resp.headers['X-Legacy-Endpoint'] = 'true'
        resp.headers['X-Legacy-Deprecation'] = 'Migrate to v2.0 API'
        
        return resp
    
    return cast(F, wrapper)
```

### Impacto

- ✅ **Funcionalidad:** Headers automáticos en respuestas legacy
- ✅ **Logging:** Rastreo de uso de endpoints obsoletos
- ✅ **Type-safe:** Usa `typing.cast` para preservar tipos

---

## 🔀 6. src/backend/routes/auth_routes.py - Endpoint Legacy

### Código Agregado (endpoint `/api/auth/usuarios/me`)

```python
@auth_bp.get('/usuarios/me')
@auth_required
def me_legacy():
    """
    LEGACY ENDPOINT: /api/auth/usuarios/me
    DEPRECATED: Use /api/auth/me instead
    
    Mantiene compatibilidad con frontend v1.
    Marca headers de deprecación.
    """
    logger.warning(
        "Legacy endpoint accessed: GET /api/auth/usuarios/me - Use /api/auth/me instead"
    )
    
    # Delegar a endpoint nuevo
    response = me_v2()
    
    # Agregar headers de deprecación (manual, no se puede usar decorator por @auth_required)
    if isinstance(response, tuple):
        resp = make_response(*response)
    else:
        resp = make_response(response)
    
    resp.headers['X-Legacy-Endpoint'] = 'true'
    resp.headers['X-Legacy-Deprecation'] = 'Use /api/auth/me instead'
    
    return resp
```

### Impacto

- ✅ **Compatibilidad:** Frontend v1 sigue funcionando
- ✅ **Deprecación:** Headers y logs marcan como obsoleto
- ✅ **Migración:** Redirige internamente a `/api/auth/me`

---

## 🔀 7. src/backend/app.py - Endpoint Legacy

### Código Modificado (endpoint `/api/users/me`)

```python
@app.put('/api/users/me')
@legacy_endpoint
def update_me():
    """
    LEGACY ENDPOINT: /api/users/me (PUT)
    DEPRECATED: Use /api/auth/me/fields (PATCH) instead
    
    Mantiene compatibilidad con frontend v1.
    El decorator @legacy_endpoint marca headers automáticamente.
    """
    # ... implementación existente ...
```

### Impacto

- ✅ **Decorator aplicado:** `@legacy_endpoint` agrega headers automáticamente
- ✅ **Deprecación:** Marcado para migración a `/api/auth/me/fields` (PATCH)
- ✅ **Compatibilidad:** Frontend v1 sigue funcionando

---

## 📊 8. Archivos Eliminados (Archivados)

### Rutas Eliminadas

```
src/backend/routes/form_intelligence_routes.py      (DELETED)
src/backend/routes/form_intelligence_routes_v2.py   (DELETED)
src/backend/services/form_intelligence.py           (DELETED)
src/backend/services/form_intelligence_v2.py        (DELETED)
```

### Nueva Ubicación

```
docs/_archive/form_intelligence/
├── form_intelligence.py
├── form_intelligence_routes.py
├── form_intelligence_routes_v2.py
├── form_intelligence_v2.py
└── README.md
```

### Contenido de `README.md` (archivado)

```markdown
# Form Intelligence - Código Archivado

Este módulo fue removido en FASE 1 de la reconstrucción v2.0.

## Razón
- Código experimental nunca activado en producción
- Dependencia de scikit-learn (removida)
- Lógica nunca integrada con frontend

## Archivado
- 2025-11-13
- FASE 1: Limpieza Controlada
```

---

## ✅ Validación de Cambios

### Checklist de Seguridad

- [x] No hay secretos hardcodeados en Dockerfile
- [x] `.env.example` usa placeholders seguros
- [x] `.env` está en `.gitignore`
- [x] `SPM_SECRET_KEY` nunca está en código fuente
- [x] `AUTH_BYPASS` solo funciona en localhost + development

### Checklist de Funcionalidad

- [x] Endpoints legacy marcados con headers
- [x] Logs de WARNING cuando se acceden rutas legacy
- [x] Decorator `@legacy_endpoint` implementado
- [x] Código archivado (no eliminado sin respaldo)
- [x] Dependencias limpias (solo las usadas)

---

## 🚀 Próximos Pasos

1. **Commit cambios:**
   ```bash
   git add .env.example .gitignore Dockerfile requirements.txt
   git add src/backend/middleware/decorators.py
   git add src/backend/routes/auth_routes.py
   git add src/backend/app.py
   git commit -m "chore(cleanup): FASE 1 - Limpieza controlada baseline

   - Externalizados secretos a .env (SPM_SECRET_KEY, AUTH_BYPASS)
   - Implementado decorator @legacy_endpoint para deprecación
   - Marcados endpoints legacy: /api/auth/usuarios/me, /api/users/me
   - Archivado código AI assistant (form_intelligence)
   - Removido scikit-learn (no usado), documentado scipy (activo)"
   ```

2. **Merge a main:**
   ```bash
   git checkout main
   git merge chore/cleanup/baseline
   git push origin main
   ```

3. **Iniciar FASE 2:**
   - Leer `Prompts Reconstrucción/FASE 2/...`

---

**Generado:** 13 de noviembre de 2025  
**Autor:** GitHub Copilot  
**Status:** ✅ LISTO PARA COMMIT
