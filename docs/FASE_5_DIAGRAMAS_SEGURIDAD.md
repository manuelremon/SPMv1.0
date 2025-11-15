# FASE 5: Diagramas de Arquitectura de Seguridad

## 1. Flujo de Autenticación con JWT + Refresh Tokens

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTE (React/Vue)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  POST /login     │
                    │  username/pwd    │
                    └──────────────────┘
                              ↓
        ┌─────────────────────────────────────────────────┐
        │         BACKEND - AUTENTICACIÓN                 │
        │  ✓ Validar credenciales                         │
        │  ✓ Hash contraseña con bcrypt                   │
        │  ✓ Crear access token (1h)  [JWT HS256]        │
        │  ✓ Crear refresh token (7d) [JWT HS256]        │
        │  ✓ Setear cookies HttpOnly                      │
        └─────────────────────────────────────────────────┘
                              ↓
            ┌──────────────────────────────────┐
            │ RESPONSE (200 OK)                │
            │ ┌─────────────────────────────┐ │
            │ │ JSON: {user data}           │ │
            │ └─────────────────────────────┘ │
            │ Cookies:                        │
            │ - spm_token = access_token      │
            │ - spm_token_refresh = refresh   │
            └──────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────────────┐
        │     CLIENT ALMACENA COOKIES (automático)        │
        │     Navegador: HttpOnly → no accesible por JS  │
        └─────────────────────────────────────────────────┘
                              ↓
            REQUEST a endpoint protegido (con cookie)
                    GET /api/solicitudes
            Browser envía automáticamente spm_token
                              ↓
        ┌─────────────────────────────────────────────────┐
        │    BACKEND - VALIDACIÓN DE ACCESS TOKEN        │
        │  ✓ Leer token de cookie                         │
        │  ✓ Verificar firma JWT                          │
        │  ✓ Validar expiration (1h)                      │
        │  ✓ Extraer claims (sub, role, etc.)            │
        └─────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Access Válido   │
                    │  Procesar request│
                    │  Retornar 200 OK │
                    └──────────────────┘
                              ↓
              DESPUÉS DE 1 HORA (token expira)
                              ↓
        ┌─────────────────────────────────────────────────┐
        │         CLIENT RECIBE 401 Unauthorized          │
        │  ✓ Detecta token expirado                       │
        │  ✓ Hace POST /api/auth/refresh                 │
        └─────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────────────┐
        │    BACKEND - VALIDACIÓN DE REFRESH TOKEN       │
        │  ✓ Leer refresh token de cookie                 │
        │  ✓ Verificar firma y expiration (7d)           │
        │  ✓ Validar que tipo es "refresh"              │
        │  ✓ Crear nuevo access token (1h)              │
        │  ✓ Setear nueva cookie spm_token               │
        └─────────────────────────────────────────────────┘
                              ↓
            ┌──────────────────────────────────┐
            │ RESPONSE (200 OK)                │
            │ ┌─────────────────────────────┐ │
            │ │ JSON: {user data}           │ │
            │ └─────────────────────────────┘ │
            │ Cookie: spm_token = NEW TOKEN   │
            └──────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────────────┐
        │   CLIENT - REINTENTAR REQUEST ORIGINAL         │
        │  ✓ Usar nuevo access token                      │
        │  ✓ Completar acción sin re-login               │
        └─────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Request éxito   │
                    │  Datos obtenidos │
                    └──────────────────┘
                              ↓
              CUANDO USUARIO HACE LOGOUT
                              ↓
        ┌─────────────────────────────────────────────────┐
        │        BACKEND - LOGOUT                         │
        │  ✓ Leer access token de cookie                  │
        │  ✓ Validar que es válido                        │
        │  ✓ Eliminar ambas cookies:                      │
        │    - spm_token = ""  (max_age=0)               │
        │    - spm_token_refresh = "" (max_age=0)        │
        └─────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Sesión cerrada  │
                    │  Tokens eliminados│
                    └──────────────────┘
```

---

## 2. Validación de CSRF en POST/PUT/PATCH/DELETE

```
┌─────────────────────────────────────────────────────┐
│  CLIENT - FORMULARIO O AJAX REQUEST                 │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  1. Obtener CSRF Token         │
        │  GET /api/csrf                 │
        │  Response: {csrf_token: "..."}│
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  2. Incluir token en Request   │
        │  POST /api/solicitudes         │
        │  Header:                       │
        │  X-CSRF-Token: "token:sig"    │
        │  Body: {data}                  │
        └────────────────────────────────┘
                         ↓
        ┌─────────────────────────────────────────────────┐
        │  BACKEND - BEFORE_REQUEST Middleware            │
        │  ✓ Leer X-CSRF-Token del header                 │
        │  ✓ Leer token session                           │
        │  ✓ Separar token:signature                      │
        │  ✓ Recalcular HMAC-SHA256                       │
        │  ✓ Comparar timing-safe (hmac.compare_digest)   │
        │  ✓ Si no coincide → 403 Forbidden              │
        └─────────────────────────────────────────────────┘
                         ↓
                ┌─────────────────────┐
                │  Token Válido       │
                │  Procesar request   │
                │  Retornar 200 OK    │
                └─────────────────────┘
                         ↓
                ┌─────────────────────┐
                │  Datos guardados    │
                │  Cambios aplicados  │
                └─────────────────────┘

ESCENARIO MALICIOSO (CSRF Attack):
───────────────────────────────────
1. Attacker intenta hacer POST desde otro sitio
2. Browser SI envía cookies automáticamente
3. PERO Attacker NO tiene X-CSRF-Token válido
4. Middleware rechaza con 403
5. Request BLOQUEADA ✓
```

---

## 3. Security Headers en Response

```
┌──────────────────────────────────────┐
│  REQUEST (cualquier método)          │
│  GET /api/solicitudes                │
└──────────────────────────────────────┘
                   ↓
        ┌──────────────────────────────┐
        │ BACKEND - after_request()    │
        │ Agrega headers de seguridad  │
        └──────────────────────────────┘
                   ↓
        ┌────────────────────────────────────────────────────┐
        │ RESPONSE Headers:                                  │
        ├────────────────────────────────────────────────────┤
        │ Strict-Transport-Security:                         │
        │   max-age=31536000; includeSubDomains; preload    │
        │   → Obliga HTTPS por 1 año                        │
        ├────────────────────────────────────────────────────┤
        │ X-Content-Type-Options: nosniff                    │
        │   → Previene MIME sniffing attacks                │
        ├────────────────────────────────────────────────────┤
        │ X-Frame-Options: DENY                              │
        │   → No permitir embedding en frames                │
        │   → Previene clickjacking                          │
        ├────────────────────────────────────────────────────┤
        │ Content-Security-Policy:                           │
        │   default-src 'self'                              │
        │   script-src 'self'                               │
        │   style-src 'self' 'unsafe-inline'                │
        │   → Restricción de recursos que puede cargar      │
        │   → Previene XSS                                   │
        ├────────────────────────────────────────────────────┤
        │ Referrer-Policy: strict-no-referrer                │
        │   → No enviar información del referrer             │
        │   → Privacidad mejorada                            │
        ├────────────────────────────────────────────────────┤
        │ Permissions-Policy:                                │
        │   camera=(); microphone=(); geolocation=()        │
        │   → Denegar acceso a hardware                      │
        ├────────────────────────────────────────────────────┤
        │ X-XSS-Protection: 1; mode=block                    │
        │   → Protección XSS (navegadores antiguos)         │
        └────────────────────────────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │ RESPUESTA SEGURA ENTREGADA AL CLIENTE    │
        │ Navegador respeta todos los headers      │
        │ y aplica restricciones de seguridad      │
        └──────────────────────────────────────────┘
```

---

## 4. Rate Limiting Middleware

```
REQUEST llega a endpoint
         ↓
  ¿Tiene @require_rate_limit?
         ↓
    SÍ (ej: /login)
         ↓
┌─────────────────────────────────────────────┐
│  Rate Limiter Check                         │
│  ✓ Obtener IP del cliente                   │
│  ✓ Buscar contador en Redis/Memory          │
│  ✓ ¿Contador < 60 requests/min?            │
│  ✓ Incrementar contador                     │
│  ✓ Setear expiration a 60 segundos         │
└─────────────────────────────────────────────┘
         ↓
  ┌──────────┴──────────┐
  ↓                     ↓
Bajo límite        EXCEDIDO (≥61)
  ↓                     ↓
Procesar         ┌──────────────────────┐
request          │ RESPONSE 429          │
  ↓              │ Too Many Requests    │
Retornar         │ {error, retry_after} │
200 OK           │ Bloqueado por 60s    │
                 └──────────────────────┘

REDIS KEYS:
──────────
rate_limit:192.168.1.100 = 5  (5 requests hechos)
EXPIRE = 60 segundos
CADA REQUEST incrementa el contador
```

---

## 5. Stack de Seguridad Completo

```
┌────────────────────────────────────────────────────────────┐
│                      CLIENT (Frontend)                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Login Form → POST /api/auth/login                   │ │
│  │ Credentials + Rate Limit (60 req/min)               │ │
│  │ Recibe: access_token + refresh_token (HttpOnly)    │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│                 HTTP TRANSPORT LAYER                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Cookies HttpOnly, Secure, SameSite=Lax              │ │
│  │ HSTS (Strict-Transport-Security)                    │ │
│  │ X-Frame-Options, X-Content-Type-Options             │ │
│  │ Content-Security-Policy                             │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask App)                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Middleware 1: Rate Limiting                         │ │
│  │  - Validar IP contra límites                        │ │
│  │  - Redis/In-Memory storage                          │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Middleware 2: CSRF Validation                       │ │
│  │  - Check X-CSRF-Token header (POST/PUT/PATCH/DEL)  │ │
│  │  - Verify HMAC-SHA256 signature                     │ │
│  │  - Timing-safe comparison (hmac.compare_digest)    │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Middleware 3: Security Headers                      │ │
│  │  - Agregar 7 headers OWASP en TODAS las respuestas │ │
│  │  - HSTS, CSP, X-Frame-Options, etc.                │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Decorator 1: @auth_required                         │ │
│  │  - Leer JWT de cookie                               │ │
│  │  - Validar firma y expiration                       │ │
│  │  - Inyectar user_payload en kwargs                 │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ JWT Manager                                         │ │
│  │  - Access tokens: 1 hora (short-lived)             │ │
│  │  - Refresh tokens: 7 días (long-lived)             │ │
│  │  - Algorithm: HS256 (HMAC-SHA256)                  │ │
│  │  - Claims: sub, uid, role, exp, iat, type         │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Data Layer (Database)                               │ │
│  │  - SQL con prepared statements (SQLAlchemy ORM)     │ │
│  │  - Password hashing con bcrypt                      │ │
│  │  - No plain-text passwords                          │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Resumen: Capas de Defensa

```
ATAQUE                    DEFENSA
──────────────────────────────────────────────
Brute Force Login    →   Rate Limiting (60 req/min)
CSRF Attack          →   CSRF Token + HMAC Signature
XSS Attack           →   Content-Security-Policy
Clickjacking         →   X-Frame-Options: DENY
MIME Sniffing        →   X-Content-Type-Options: nosniff
Timing Attack (CSRF) →   hmac.compare_digest()
Session Hijacking    →   JWT expiration + HttpOnly
HTTPS Downgrade      →   HSTS header (1 año)
Session Fixation     →   Refresh token rotation
Token Reuse          →   Short-lived access tokens
Hardware Access      →   Permissions-Policy headers
Referrer Leakage     →   Referrer-Policy: strict-no-referrer
```

Este diseño de seguridad **multi-layer** sigue estándares OWASP y proporciona protección robusta contra vectores de ataque comunes.

