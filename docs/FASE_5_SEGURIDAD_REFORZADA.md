# FASE 5: Seguridad Reforzada - Implementación Completada

**Fecha**: 15 de noviembre de 2025  
**Estado**: ✅ COMPLETADO  
**Rama**: `chore/cleanup/baseline`

---

## 📋 Resumen Ejecutivo

La **Fase 5** implementa un sistema de seguridad robusto conforme a estándares OWASP para proteger contra:

- ✅ **CSRF** (Cross-Site Request Forgery)
- ✅ **XSS** (Cross-Site Scripting)
- ✅ **Clickjacking**
- ✅ **MIME sniffing**
- ✅ **Timing attacks**
- ✅ **Rate limiting** (DoS)
- ✅ **Exposición de headers**

### Componentes Implementados

| Componente | Archivo | Propósito |
|-----------|---------|----------|
| Rate Limiter | `core/rate_limiter.py` | Protección contra ataques de fuerza bruta |
| CSRF Protection | `core/csrf.py` | Validación de tokens CSRF |
| Security Headers | `core/security_headers.py` | Headers HTTP de seguridad |
| JWT Manager | `core/jwt_manager.py` | Autenticación con refresh tokens |
| Auth Routes | `routes/auth.py` | Endpoints de autenticación |

---

## 🔐 1. Rate Limiting

### Descripción
Implementa **token bucket algorithm** con soporte para Redis (producción) e in-memory cache (desarrollo).

### Archivo
- **`backend_v2/core/rate_limiter.py`** (nuevo)

### Características

#### InMemoryRateLimiter (Desarrollo)
```python
from core.rate_limiter import rate_limiter

# Verificar si está permitido
if rate_limiter.is_allowed("192.168.1.1"):
    # Procesar request
    pass

# Obtener requests restantes
remaining = rate_limiter.get_remaining("192.168.1.1")
```

#### RedisRateLimiter (Producción)
```python
import redis
from core.rate_limiter import create_rate_limiter

redis_client = redis.Redis(host="localhost", port=6379)
rate_limiter = create_rate_limiter(redis_client)
```

### Decorator `@require_rate_limit`

Se aplica automáticamente en endpoints sensibles:

```python
@bp.post("/api/auth/login")
@require_rate_limit
def login():
    """Endpoint protegido por rate limiting"""
    pass
```

**Respuesta cuando se excede el límite** (HTTP 429):
```json
{
  "ok": false,
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Max 60 requests per minute.",
    "retry_after": 60
  }
}
```

### Configuración

En `core/config.py`:
```python
# Rate limiting
RATE_LIMIT_ENABLED: bool = False  # Activar en producción
RATE_LIMIT_PER_MINUTE: int = 60   # Límite por defecto
```

### Casos de Uso
- ✅ Login (proteger contra brute force)
- ✅ Registro (proteger contra spam)
- ✅ APIs públicas
- ✅ Endpoints de reset de contraseña

---

## 🛡️ 2. CSRF Protection

### Descripción
Protección contra **Cross-Site Request Forgery** mediante tokens firmados con HMAC-SHA256.

### Archivo
- **`backend_v2/core/csrf.py`** (nuevo)

### Arquitectura

1. **Token Generation**: Se crea un token único por sesión
2. **Token Signing**: Se firma con HMAC-SHA256 para evitar tampering
3. **Token Validation**: Se valida en métodos POST/PUT/PATCH/DELETE

### Uso desde Frontend

#### 1. Obtener token CSRF (GET, no requiere autenticación)
```javascript
async function getCsrfToken() {
  const response = await fetch("/api/csrf");
  const data = await response.json();
  return data.csrf_token;
}

const csrfToken = await getCsrfToken();
```

#### 2. Incluir token en requests que modifican datos
```javascript
// Opción A: Header (recomendado para AJAX)
fetch("/api/solicitudes", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": csrfToken
  },
  body: JSON.stringify({ ... })
})

// Opción B: Form data
const formData = new FormData();
formData.append("csrf_token", csrfToken);
formData.append("data", JSON.stringify({ ... }));

fetch("/api/solicitudes", {
  method: "POST",
  body: formData
})
```

### Endpoints Automáticos

#### GET `/api/csrf` - Obtener token CSRF

**Response:**
```json
{
  "ok": true,
  "csrf_token": "abc123def456:signature..."
}
```

### Decorator `@csrf_exempt`

Eximir endpoints de validación CSRF (ej: webhooks externos):

```python
from core.csrf import csrf_exempt

@app.post("/api/webhook/external")
@csrf_exempt
def external_webhook():
    """Este endpoint no requiere CSRF token"""
    pass
```

### Configuración

Automática en `app.py`:
```python
from core.csrf import init_csrf_protection

app = Flask(__name__)
init_csrf_protection(app)  # Activa protección CSRF automática
```

### Detalles Técnicos

- **Token Size**: 32 bytes (64 caracteres hex)
- **Signature Algorithm**: HMAC-SHA256
- **Storage**: Session cookies (respaldadas por servidor)
- **Validation**: Timing-safe comparison para prevenir timing attacks

---

## 🔑 3. Security Headers

### Descripción
Agrega headers HTTP de seguridad recomendados por OWASP a TODAS las respuestas.

### Archivo
- **`backend_v2/core/security_headers.py`** (nuevo)

### Headers Implementados

| Header | Valor | Propósito |
|--------|-------|----------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Fuerza HTTPS (1 año) |
| `X-Content-Type-Options` | `nosniff` | Previene MIME sniffing |
| `X-Frame-Options` | `DENY` | Previene clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Protección XSS (navegadores antiguos) |
| `Content-Security-Policy` | Varias directivas | Restricción de recursos |
| `Referrer-Policy` | `strict-no-referrer` | Privacidad del referrer |
| `Permissions-Policy` | Varias características bloqueadas | Acceso a hardware (cámara, micrófono, etc.) |

### Content-Security-Policy (CSP)

```
default-src 'self'                    # Solo contenido del mismo origen
script-src 'self'                      # Solo scripts locales
style-src 'self' 'unsafe-inline'       # Estilos locales + inline (React/Vue)
img-src 'self' data: https:            # Imágenes locales + data URLs + HTTPS
font-src 'self' data:                  # Fuentes locales
connect-src 'self'                     # XHR/fetch solo al mismo origen
frame-ancestors 'none'                 # No embedding en frames
base-uri 'self'                        # <base> solo del mismo origen
form-action 'self'                     # Formularios solo al mismo origen
```

### Configuración

Automática en `app.py`:
```python
from core.security_headers import init_security_headers

app = Flask(__name__)
init_security_headers(app)  # Agrega headers automáticamente
```

---

## 🎫 4. JWT con Refresh Tokens

### Descripción
Sistema de autenticación mediante JWT con tokens de acceso (short-lived) y refresh (long-lived).

### Archivo
- **`backend_v2/core/jwt_manager.py`** (mejorado)
- **`backend_v2/routes/auth.py`** (actualizado)

### Tipos de Token

#### Access Token (spm_token)
- **Duración**: 1 hora (configurable en `JWT_ACCESS_TOKEN_TTL`)
- **Uso**: Autenticación en endpoints protegidos
- **Almacenamiento**: Cookie HttpOnly, Secure, SameSite=Lax
- **Claims**: `sub`, `uid`, `id_spm`, `rol`, `roles`, `email`, `exp`, `iat`, `type`

#### Refresh Token (spm_token_refresh)
- **Duración**: 7 días
- **Uso**: Solo para obtener nuevos access tokens
- **Almacenamiento**: Cookie HttpOnly, Secure, SameSite=Lax
- **Claims**: `sub`, `exp`, `iat`, `type`

### Endpoints

#### POST `/api/auth/login` - Autenticación

**Request:**
```json
{
  "username": "admin@spm.com",
  "password": "admin123"
}
```

**Response (201):**
```json
{
  "ok": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@spm.com",
    "role": "Administrador",
    "nombre": "Admin",
    "apellido": "Sistema",
    ...
  }
}
```

**Cookies establecidas:**
- `spm_token`: Access token (1 hora)
- `spm_token_refresh`: Refresh token (7 días)

#### POST `/api/auth/refresh` - Refrescar token

Permite mantener sesiones activas sin re-autenticación.

**Request:**
```
POST /api/auth/refresh
Cookie: spm_token_refresh=<valid_refresh_token>
```

**Response (200):**
```json
{
  "ok": true,
  "user": { ... }
}
```

**Cookies actualizadas:**
- `spm_token`: Nuevo access token

#### POST `/api/auth/logout` - Cerrar sesión

**Request:**
```
POST /api/auth/logout
Cookie: spm_token=<valid_access_token>
```

**Response (200):**
```json
{
  "ok": true,
  "message": "Logged out successfully"
}
```

**Cookies eliminadas:**
- `spm_token`
- `spm_token_refresh`

### API de JWTManager

```python
from core.jwt_manager import jwt_manager

# Crear token de acceso
access_token = jwt_manager.create_access_token({
    "sub": "1",
    "username": "admin"
})

# Crear token de refresh
refresh_token = jwt_manager.create_refresh_token({
    "sub": "1"
})

# Verificar token (retorna payload o None)
payload = jwt_manager.verify_token(access_token, token_type="access")

# Setear token en cookie
response = make_response(jsonify({"ok": True}))
response = jwt_manager.set_token_cookie(response, access_token, token_type="access")
response = jwt_manager.set_token_cookie(response, refresh_token, token_type="refresh")

# Limpiar cookies (logout)
response = jwt_manager.clear_token_cookie(response)
```

### Flujo de Autenticación

```
1. Usuario hace POST /api/auth/login
   ├─ Valida credenciales
   ├─ Crea access token (1h)
   ├─ Crea refresh token (7d)
   └─ Retorna usuario + cookies

2. Usuario hace request a endpoint protegido
   ├─ Lee spm_token desde cookie
   ├─ Valida y decodifica JWT
   └─ Procesa request si es válido

3. Access token expira
   ├─ Usuario recibe 401 Unauthorized
   ├─ Frontend hace POST /api/auth/refresh
   ├─ Backend valida spm_token_refresh
   ├─ Crea nuevo access token (spm_token)
   └─ Usuario continúa sin re-autenticarse

4. Usuario hace POST /api/auth/logout
   ├─ Backend valida token
   ├─ Elimina cookies (spm_token + spm_token_refresh)
   └─ Sesión cerrada
```

### Configuración

En `core/config.py`:
```python
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_TTL: int = 3600  # 1 hora
JWT_COOKIE_NAME: str = "spm_token"
JWT_COOKIE_HTTPONLY: bool = True
JWT_COOKIE_SECURE: bool = False  # True en producción (HTTPS)
JWT_COOKIE_SAMESITE: Literal["Lax", "Strict", "None"] = "Lax"
```

---

## 📦 Dependencias Nuevas

Se agregó a `requirements.txt`:
```
redis==5.0.1  # Para rate limiting en producción
```

Las demás dependencias ya estaban:
- `PyJWT==2.10.1` (tokens JWT)
- `bcrypt==5.0.0` (hashing de contraseñas)
- `Flask==3.1.2` (framework web)
- `flask-cors==6.0.1` (CORS)

---

## 🧪 Testing

### Test de Rate Limiting
```python
def test_rate_limit_exceeded():
    """Verifica que 429 se retorna cuando se excede límite"""
    from core.config import settings
    settings.RATE_LIMIT_ENABLED = True
    
    # Hacer 61 requests en rápida sucesión
    # El 61ero debe retornar 429
```

### Test de CSRF
```python
def test_csrf_token_validation():
    """Verifica que CSRF token es requerido"""
    # GET /api/csrf -> obtiene token
    # POST /api/solicitudes sin token -> 403
    # POST /api/solicitudes con token -> 200
```

### Test de JWT
```python
def test_jwt_refresh_token():
    """Verifica refresh token flow"""
    # POST /api/auth/login -> obtiene access + refresh tokens
    # POST /api/auth/refresh -> obtiene nuevo access token
```

---

## 🚀 Guía de Uso para Desarrolladores

### Backend (Flask)

#### Proteger un endpoint con autenticación
```python
from routes.auth import auth_required

@app.post("/api/solicitudes")
@auth_required
def create_solicitud(user_payload):
    user_id = user_payload["sub"]
    # Crear solicitud...
```

#### Proteger contra CSRF
Automático en POST/PUT/PATCH/DELETE. No requiere acción adicional.

#### Proteger contra rate limiting
```python
from core.rate_limiter import require_rate_limit

@app.post("/api/auth/login")
@require_rate_limit
def login():
    # Limitado a 60 requests/minuto por IP
    pass
```

### Frontend (React/Vue)

#### Flujo de autenticación

```javascript
// 1. Login
const response = await fetch("/api/auth/login", {
  method: "POST",
  credentials: "include",  // Incluir cookies
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username, password })
});

// 2. Hacer requests autenticados (cookie automática)
const data = await fetch("/api/solicitudes", {
  credentials: "include"
});

// 3. Si acceso token expira, refresh automáticamente
async function fetchWithAutoRefresh(url, options) {
  let response = await fetch(url, { ...options, credentials: "include" });
  
  if (response.status === 401) {
    // Intentar refrescar
    const refreshResponse = await fetch("/api/auth/refresh", {
      method: "POST",
      credentials: "include"
    });
    
    if (refreshResponse.ok) {
      // Reintentar request original
      response = await fetch(url, { ...options, credentials: "include" });
    }
  }
  
  return response;
}

// 4. Obtener CSRF token y usarlo en requests POST/PUT/PATCH
const csrfResponse = await fetch("/api/csrf");
const { csrf_token } = await csrfResponse.json();

await fetch("/api/solicitudes", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": csrf_token
  },
  body: JSON.stringify({ ... })
});

// 5. Logout
await fetch("/api/auth/logout", {
  method: "POST",
  credentials: "include"
});
```

---

## 🔒 Checklist de Seguridad

- ✅ Rate limiting en endpoints sensibles
- ✅ CSRF protection en métodos POST/PUT/PATCH/DELETE
- ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)
- ✅ JWT con access + refresh tokens
- ✅ Cookies HttpOnly para tokens (previene XSS)
- ✅ Comparación timing-safe para CSRF (previene timing attacks)
- ✅ Session cookies secure en producción
- ✅ CORS habilitado pero restringido a origen local

---

## ⚙️ Próximos Pasos

### Fase 6: Frontend v2
- Implementar flujo de autenticación en React/Vue
- Intercepción de 401 para refresh automático
- Obtención y envío automático de CSRF token

### Fase 7: PostgreSQL
- Migrar de SQLite a PostgreSQL
- Mantener compatibilidad con JWT y seguridad

### Fase 8: CI/CD y Testing
- Tests unitarios para rate limiting, CSRF, JWT
- Tests de integración para flujos de autenticación
- Coverage > 80%

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html#rate-limit)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

## 📝 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `backend_v2/core/rate_limiter.py` | ✨ Nuevo - Rate limiting con Redis |
| `backend_v2/core/csrf.py` | ✨ Nuevo - CSRF protection |
| `backend_v2/core/security_headers.py` | ✨ Nuevo - Security headers |
| `backend_v2/core/jwt_manager.py` | 📝 Actualizado - Refresh tokens |
| `backend_v2/core/security.py` | 🔄 Refactorizado - Depreca funciones |
| `backend_v2/app.py` | 📝 Actualizado - Inicializa middleware |
| `backend_v2/routes/auth.py` | 📝 Actualizado - Endpoint refresh |
| `requirements.txt` | ➕ Agregado redis==5.0.1 |

---

## ✅ Validación

Para validar que la Fase 5 funciona correctamente:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar tests
pytest backend_v2/tests/ -v

# 3. Revisar headers en response
curl -i http://localhost:5000/api/health

# 4. Probar rate limiting
for i in {1..70}; do curl http://localhost:5000/api/auth/login & done; wait

# 5. Probar CSRF
curl http://localhost:5000/api/csrf

# 6. Probar JWT
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

**Estado**: ✅ Fase 5 Completada y Lista para Fase 6 (Frontend v2)

