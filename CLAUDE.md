# 🔍 CLAUDE.md - Guía Completa del Codebase SPM v1.0

**Versión:** 1.0 | **Última actualización:** 8 de noviembre de 2025 | **Estado:** Producción ✅

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estructura de Directorios](#estructura-de-directorios)
5. [Backend (Flask)](#backend-flask)
6. [Frontend (Vite + JavaScript)](#frontend-vite--javascript)
7. [Base de Datos](#base-de-datos)
8. [Módulos Especializados](#módulos-especializados)
9. [API REST](#api-rest)
10. [Flujos Clave](#flujos-clave)
11. [Configuración y Entorno](#configuración-y-entorno)
12. [Guía Rápida de Desarrollo](#guía-rápida-de-desarrollo)

---

## 🎯 Resumen Ejecutivo

**SPM (Sistema de Solicitudes de Materiales)** es una aplicación web empresarial completa para gestionar solicitudes de materiales con:

- ✅ **Arquitectura moderna**: Flask backend + Vite frontend
- ✅ **Autenticación basada en roles**: Admin, Coordinador, Usuario
- ✅ **Flujo de aprobación completo** con notificaciones en tiempo real
- ✅ **Gestión de materiales y almacenes** multiubicación
- ✅ **Planificación inteligente** (AI + Algoritmos de optimización)
- ✅ **Reportes y análisis** en tiempo real
- ✅ **Base de datos SQLite** robusta con auditoría

**Público objetivo**: Empresas que necesitan automatizar la gestión de solicitudes de materiales con flujos complejos de aprobación.

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│         Frontend (Vite + JavaScript/HTML/CSS)           │
│              http://localhost:5173                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ • Dashboard                                       │   │
│  │ • Solicitudes (crear, editar, listar)           │   │
│  │ • Gestión de Materiales                          │   │
│  │ • Administración (usuarios, centros, almacenes)  │   │
│  │ • Planificación                                  │   │
│  │ • Reportes                                       │   │
│  │ • Consola IA                                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓ (API REST)
┌─────────────────────────────────────────────────────────┐
│         Backend (Flask)                                  │
│         http://localhost:5000                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Rutas (Routes)                                   │   │
│  │ • auth_routes.py          → Autenticación       │   │
│  │ • solicitudes.py           → Solicitudes        │   │
│  │ • materiales.py            → Búsqueda/catálogo  │   │
│  │ • admin.py                 → Administración      │   │
│  │ • planner_routes.py        → Planificación      │   │
│  │ • preferences.py           → Preferencias       │   │
│  │ • catalogos.py             → Catálogos          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Servicios (Services)                             │   │
│  │ • auth/ → JWT, tokens, seguridad                │   │
│  │ • dashboard/ → Estadísticas y métricas          │   │
│  │ • ai_service.py → Integración IA               │   │
│  │ • form_intelligence.py → Análisis de solicitudes │   │
│  │ • db/ → Operaciones de BD                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓ (SQLite)
┌─────────────────────────────────────────────────────────┐
│         Base de Datos (SQLite)                          │
│         src/backend/core/data/spm.db                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │ • usuarios                                       │   │
│  │ • solicitudes + solicitudes_items (JSON)         │   │
│  │ • materiales                                     │   │
│  │ • presupuestos                                   │   │
│  │ • catalógos (centros, sectores, almacenes)       │   │
│  │ • notificaciones                                 │   │
│  │ • presupuesto_incorporaciones                    │   │
│  │ • planificadores                                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológico

### Backend
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **Python** | 3.11+ | Runtime |
| **Flask** | 3.1.2 | Framework web |
| **Flask-CORS** | 6.0.1 | CORS handling |
| **SQLAlchemy** | 2.0.44 | ORM (configuración) |
| **Pydantic** | 2.12.3 | Validación de datos |
| **PyJWT** | 2.10.1 | Autenticación JWT |
| **python-dotenv** | 1.1.1 | Variables de entorno |
| **bcrypt** | 5.0.0 | Hashing de contraseñas |

### Frontend
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **Vite** | 5.4.21 | Build tool y dev server |
| **JavaScript** | ES2023+ | Lógica del frontend |
| **HTML5** | Latest | Estructura |
| **CSS3** | Latest | Estilos y temas |
| **Fetch API** | Native | Comunicación con backend |

### Infraestructura
| Componente | Uso |
|-----------|-----|
| **SQLite** | Base de datos relacional |
| **Docker** | Containerización (opcional) |
| **Git** | Control de versiones |

---

## 📁 Estructura de Directorios

```
SPMv1.0/
├── src/
│   ├── backend/
│   │   ├── app.py                          # Inicializador principal de Flask
│   │   ├── routes/
│   │   │   ├── auth_routes.py              # Autenticación y registro
│   │   │   ├── solicitudes.py              # CRUD de solicitudes (★ MÁS IMPORTANTE)
│   │   │   ├── materiales.py               # Búsqueda y catálogo de materiales
│   │   │   ├── admin.py                    # Panel de administración
│   │   │   ├── planner_routes.py           # Rutas de planificación
│   │   │   ├── catalogos.py                # Catálogos (centros, almacenes, sectores)
│   │   │   ├── preferences.py              # Preferencias de usuario
│   │   │   └── [otros archivos].py
│   │   ├── services/
│   │   │   ├── auth/
│   │   │   │   ├── jwt_utils.py            # Gestión de tokens JWT
│   │   │   │   └── ...
│   │   │   ├── dashboard/
│   │   │   │   └── ...                     # Estadísticas y métricas
│   │   │   ├── db/
│   │   │   │   └── ...                     # Operaciones de BD
│   │   │   ├── ai_service.py               # Integración IA (Anthropic)
│   │   │   ├── form_intelligence.py        # Análisis inteligente de solicitudes
│   │   │   ├── form_intelligence_v2.py     # v2 mejorada
│   │   │   └── ...
│   │   ├── models/
│   │   │   ├── schemas.py                  # Esquemas Pydantic (★ CRÍTICO)
│   │   │   ├── roles.py                    # Definición de roles
│   │   │   └── catalog_schema.py
│   │   ├── core/
│   │   │   ├── config.py                   # Configuración (env variables)
│   │   │   ├── db.py                       # Conexión a BD
│   │   │   ├── init_db.py                  # Inicialización de BD (★ IMPORTANTE)
│   │   │   ├── data/
│   │   │   │   ├── spm.db                  # Base de datos SQLite
│   │   │   │   ├── Usuarios.csv            # Datos iniciales
│   │   │   │   ├── Materiales.csv
│   │   │   │   └── Presupuestos.csv
│   │   │   └── logs/
│   │   │       └── app.log                 # Logs de la aplicación
│   │   ├── middleware/
│   │   ├── static/
│   │   ├── uploads/                        # Archivos cargados por usuarios
│   │   └── __init__.py
│   │
│   ├── frontend/
│   │   ├── index.html                      # Punto de entrada principal
│   │   ├── app.js                          # Lógica principal (★ 3900+ líneas)
│   │   ├── boot.js                         # Bootstrap del frontend
│   │   ├── styles.css                      # Estilos principales
│   │   │
│   │   ├── [páginas HTML]
│   │   ├── dashboard.html                  # Dashboard principal
│   │   ├── solicitudes.html                # Listar solicitudes
│   │   ├── nueva-solicitud.html            # Crear solicitud
│   │   ├── materiales.html                 # Ver materiales
│   │   ├── agregar-materiales.html         # Agregar materiales a solicitud
│   │   ├── admin-*.html                    # Paneles de administración
│   │   ├── planificacion.html              # Módulo de planificación
│   │   ├── reportes.html                   # Reportes y análisis
│   │   ├── ai-console.html                 # Consola de IA
│   │   │
│   │   ├── components/                     # Componentes reutilizables
│   │   ├── pages/                          # Páginas complejas
│   │   ├── modules/                        # Módulos JavaScript (vacío)
│   │   ├── utils/                          # Utilidades JS
│   │   ├── ui/                             # Componentes UI
│   │   ├── assets/                         # Recursos (iconos, imágenes)
│   │   └── __tests__/                      # Tests del frontend
│   │
│   ├── planner/                            # ★ Módulo especializado: Planificación
│   │   ├── algorithms/                     # Algoritmos de optimización
│   │   ├── models/                         # Modelos de planificación
│   │   ├── scoring/                        # Sistema de puntuación
│   │   ├── optimization/                   # Optimizaciones
│   │   ├── rules/                          # Reglas de negocio
│   │   └── README_MODELS.md                # Documentación de modelos
│   │
│   ├── agent/                              # ★ Módulo especializado: Agentes IA
│   │   ├── catalog.py                      # Catálogo de agentes
│   │   ├── llm.py                          # Integración con LLMs
│   │   ├── models.py                       # Modelos de agentes
│   │   ├── rules.py                        # Reglas para agentes
│   │   └── main.py
│   │
│   └── ai_assistant/                       # ★ Módulo especializado: Asistente IA
│       └── [archivos de IA]
│
├── database/
│   ├── schemas/                            # Esquemas SQL
│   ├── migrations/                         # Migraciones de BD
│   ├── audit/                              # Auditoría
│   ├── backup/                             # Backups
│   └── fixes/                              # Fixes de BD
│
├── docs/
│   ├── 00_COMIENZA_AQUI.md                 # Punto de entrada documentación
│   ├── ARCHITECTURE.md                     # Arquitectura detallada
│   ├── api.md                              # Documentación de API
│   ├── QUICK_START.txt                     # Inicio rápido
│   ├── guides/
│   │   ├── QUICK_REFERENCE_BD.md           # Queries útiles de BD
│   │   ├── IMPLEMENTACION_*.md             # Guías de implementación
│   │   └── ...
│   └── [otros documentos]
│
├── scripts/
│   ├── dev/
│   │   ├── start_dev_servers.ps1           # Script para iniciar dev
│   │   ├── setup.ps1
│   │   ├── start_server.ps1
│   │   └── ...
│   ├── utilities/
│   │   └── [scripts de utilidad]
│   └── [otros scripts]
│
├── tests/
│   ├── test_create_solicitud.py            # Test de creación de solicitudes
│   └── ...
│
├── config/
│   └── devcontainer.json                   # Dev container config
│
├── infrastructure/
│   └── [configuración de infraestructura]
│
├── package.json                            # Dependencias Node.js
├── pyproject.toml                          # Configuración Python
├── requirements.txt                        # Dependencias Python
├── requirements-dev.txt
├── vite.config.js                          # Configuración Vite
├── jest.config.js                          # Configuración Jest
├── docker-compose.yml                      # Docker compose
├── Dockerfile                              # Dockerfile
├── wsgi.py                                 # Entry point WSGI
├── run_backend.py                          # Script para ejecutar backend
├── README.md                               # README principal
├── DEPLOYMENT.md                           # Guía de deployment
├── LICENSE
└── .env                                    # Variables de entorno (no trackeado)
```

---

## 💼 Backend (Flask)

### Estructura General

```python
# src/backend/app.py
from flask import Flask
from flask_cors import CORS

# Blueprints registrados:
- auth_bp          → /api/auth/*
- solicitudes_bp   → /api/solicitudes/*
- materiales_bp    → /api/materiales/*
- catalogos_bp     → /api/catalogos/*
- admin_bp         → /api/admin/*
- planner_bp       → /api/planner/*
- preferences_bp   → /api/preferencias/*
```

### Rutas Principales

#### 🔐 Autenticación (`auth_routes.py`)
```
POST   /api/auth/login              → Iniciar sesión
POST   /api/auth/register           → Registro de usuario
POST   /api/auth/logout             → Cerrar sesión
POST   /api/auth/refresh            → Refrescar token
GET    /api/auth/me                 → Datos del usuario actual
PATCH  /api/auth/me/fields          → Actualizar campos de usuario
POST   /api/auth/me/mail            → Cambiar correo
POST   /api/auth/me/telefono        → Cambiar teléfono
GET    /api/auth/dashboard/stats    → Estadísticas del dashboard
```

#### 📋 Solicitudes (`solicitudes.py`) ★ MÁS IMPORTANTE
```
GET    /api/solicitudes                      → Listar solicitudes
POST   /api/solicitudes                      → Crear solicitud
GET    /api/solicitudes/<int:sol_id>         → Detalle de solicitud
PUT    /api/solicitudes/<int:sol_id>         → Actualizar solicitud
PATCH  /api/solicitudes/<int:sol_id>/draft   → Guardar como borrador
POST   /api/solicitudes/<int:sol_id>/decidir → Aprobar/Rechazar
POST   /api/solicitudes/drafts               → Crear/actualizar borrador
GET    /api/solicitudes/export/excel         → Exportar a Excel
GET    /api/solicitudes/export/pdf           → Exportar a PDF
```

**Estructura de Solicitud:**
```json
{
  "id": 1,
  "id_usuario": "usuario1",
  "centro": "1008",
  "sector": "Mantenimiento",
  "justificacion": "Descripción de la solicitud",
  "centro_costos": "CC001",
  "almacen_virtual": "ALM0001",
  "criticidad": "Normal|Alta",
  "fecha_necesidad": "2025-11-15",
  "status": "draft|submitted|approved|rejected|processing|dispatched|closed",
  "data_json": {
    "items": [
      {
        "codigo": "1000000006",
        "descripcion": "TUERCA M12",
        "cantidad": 10,
        "precio_unitario": 45.50,
        "comentario": "Para mantenimiento"
      }
    ]
  },
  "total_monto": 455.00,
  "created_at": "2025-11-08T10:30:00",
  "updated_at": "2025-11-08T10:30:00"
}
```

#### 🏪 Materiales (`materiales.py`)
```
GET    /api/materiales?q=&codigo=&descripcion=&limit=100
       → Buscar materiales
```

**Parámetros de búsqueda:**
- `q`: Término general de búsqueda
- `codigo`: Buscar por código SAP
- `descripcion`: Buscar por descripción
- `limit`: Límite de resultados (máx. 100,000)

**Respuesta:**
```json
[
  {
    "codigo": "1000000006",
    "descripcion": "TUERCA M12",
    "descripcion_larga": "Tuerca hexagonal de acero inoxidable...",
    "unidad": "UNI",
    "precio_usd": 45.50,
    "centro": "1008",
    "sector": "Almacén Central"
  }
]
```

#### 📊 Catálogos (`catalogos.py`)
```
GET    /api/catalogos                    → Todos los catálogos
GET    /api/catalogos/<resource>         → Catálogo específico
                                           (centros, almacenes, sectores, etc.)
```

#### ⚙️ Administración (`admin.py`)
```
GET    /api/admin/summary                → Resumen ejecutivo
GET    /api/admin/solicitudes            → Listar solicitudes (admin)
GET    /api/admin/usuarios               → Listar usuarios
GET    /api/admin/materiales             → Listar materiales
POST   /api/admin/usuarios               → Crear usuario
PUT    /api/admin/usuarios/<id>          → Actualizar usuario
```

#### 📅 Planificación (`planner_routes.py`)
```
GET    /api/planner/dashboard            → Dashboard de planificador
GET    /api/planner/solicitudes          → Solicitudes pendientes
GET    /api/planner/solicitudes/<id>     → Detalle de solicitud
POST   /api/planner/solicitudes/<id>/optimize  → Optimizar solicitud
```

#### 💬 Preferencias (`preferences.py`)
```
GET    /api/preferencias                 → Obtener preferencias
PATCH  /api/preferencias                 → Actualizar preferencias
```

### Servicios (Services)

#### `auth/jwt_utils.py`
- **Funciones clave:**
  - `verify_token()` → Verifica JWT y retorna user ID
  - `create_access_token()` → Crea token JWT
  - `decode_token()` → Decodifica token

#### `ai_service.py`
- Integración con Claude API (Anthropic)
- Análisis inteligente de solicitudes
- Generación de sugerencias

#### `form_intelligence.py` y `form_intelligence_v2.py`
- Análisis de formularios inteligente
- Sugerencias de materiales basadas en IA
- Análisis de solicitudes anteriores

#### `dashboard/`
- Generación de estadísticas
- Métricas en tiempo real
- Reportes

### Modelos y Esquemas

#### `models/schemas.py` ★ CRÍTICO
Define todos los esquemas Pydantic para validación:

```python
# Usuarios
class LoginRequest(BaseModel):
    mail: EmailStr
    contrasena: str

# Solicitudes
class SolicitudItem(BaseModel):
    codigo: str
    descripcion: Optional[str]
    cantidad: int ≥ 1
    precio_unitario: float ≥ 0
    comentario: Optional[str]

class SolicitudCreate(BaseModel):
    id_usuario: str
    centro: str
    sector: str
    justificacion: str
    centro_costos: str
    almacen_virtual: str
    criticidad: Literal["Normal", "Alta"]
    fecha_necesidad: date
    items: List[SolicitudItem]

# Búsqueda de materiales
class MaterialSearchQuery(BaseModel):
    q: Optional[str]
    codigo: Optional[str]
    descripcion: Optional[str]
    limit: int (1-100,000)
```

### Configuración (`core/config.py`)

**Variables de Entorno Principales:**
```
# Base de datos
SPM_DB_PATH=src/backend/core/data/spm.db
SPM_LOG_PATH=src/backend/core/logs/app.log

# Seguridad
SPM_SECRET_KEY=<generado automáticamente en dev>
SPM_ACCESS_TTL=3600          # Token expiration (segundos)
SPM_REFRESH_GRACE_PERIOD=300

# CORS
SPM_CORS_ORIGINS=http://127.0.0.1:5173

# Archivos
SPM_UPLOAD_DIR=src/backend/uploads
SPM_MAX_CONTENT_LENGTH=16777216  # 16MB

# IA
AI_ENABLE=1
AI_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
AI_MAX_SUGGESTIONS=5

# Entorno
SPM_ENV=development|production
SPM_DEBUG=1
```

### Inicialización de BD (`core/init_db.py`) ★ IMPORTANTE

Crea la estructura completa de la BD:

**Tablas principales:**
1. `usuarios` → Usuarios del sistema
2. `solicitudes` → Solicitudes principales
3. `materiales` → Catálogo de materiales
4. `presupuestos` → Presupuestos por centro/sector
5. `catalog_centros` → Centros de costo
6. `catalog_sectores` → Sectores
7. `catalog_almacenes` → Almacenes
8. `notificaciones` → Sistema de notificaciones
9. `planificadores` → Asignación de planificadores

---

## 🎨 Frontend (Vite + JavaScript)

### Arquitectura

```javascript
// src/frontend/app.js (★ 3900+ líneas)
// - Gestión centralizada de estado
// - Sistema de routing
// - Gestión de formularios
// - Integración con API
// - Manejo de errores
```

### Sistema de Enrutamiento

```javascript
// app.js contiene un router custom que mapea:
'/'                    → dashboard.html
'/login'              → login.html
'/solicitudes'        → solicitudes.html
'/nueva-solicitud'    → nueva-solicitud.html
'/materiales'         → materiales.html
'/admin-usuarios'     → admin-usuarios.html
// ... 20+ más rutas
```

### Flujo de Datos

```
Frontend (app.js)
      ↓
Captura eventos del usuario
      ↓
Valida datos localmente (Pydantic-like)
      ↓
Llama API (fetch)
      ↓
Backend responde
      ↓
Actualiza estado global
      ↓
Re-renderiza componentes afectados
```

### Páginas Principales

#### 📊 Dashboard (`dashboard.html`)
- Resumen de solicitudes
- Estadísticas de estado
- Últimas solicitudes
- KPIs principales

#### 📋 Solicitudes (`solicitudes.html`)
- Lista de solicitudes del usuario
- Filtros por estado
- Acciones rápidas
- Exportación a PDF/Excel

#### ➕ Nueva Solicitud (`nueva-solicitud.html`)
- **Paso 1:** Seleccionar centro, sector, criticidad
- **Paso 2:** Agregar materiales (búsqueda inteligente)
- **Paso 3:** Revisión y envío
- **Paso 4:** Confirmación

#### 🏪 Materiales (`materiales.html`)
- Búsqueda avanzada
- Filtros por centro, sector
- Detalles de materiales
- Precios y disponibilidad

#### 👥 Admin (`admin-*.html`)
- Gestión de usuarios
- Gestión de materiales
- Gestión de centros y almacenes
- Reportes de auditoría

#### 📅 Planificación (`planificacion.html`)
- Vista de solicitudes pendientes
- Optimización automática
- Asignación de planificadores
- Timeline de ejecución

### Estilos

```css
/* src/frontend/styles.css */
- Sistema de variables CSS
- Tema claro/oscuro
- Responsive design (mobile-first)
- Componentes reutilizables (btn, input, modal, etc.)
```

### Componentes Clave

```javascript
// Gestión de estado
state = {
  auth: { user, token, roles },
  datos: { solicitudes, materiales, usuarios },
  preferencias: { tema, idioma, notificaciones },
  formularios: { formData, errores, submitting }
}

// Funciones principales
renderDashboard()
createSolicitud()
updateSolicitud()
searchMaterials()
navigateFormStep()
showModal()
makeRequest()  // Wrapper de fetch
```

---

## 💾 Base de Datos

### Archivo Principal
```
src/backend/core/data/spm.db
```

### Estructura de Tablas

#### `usuarios`
```sql
CREATE TABLE usuarios (
    id_spm TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    rol TEXT NOT NULL,  -- 'admin', 'coordinador', 'usuario'
    posicion TEXT,
    sector TEXT,
    mail TEXT UNIQUE NOT NULL,
    telefono TEXT,
    id_ypf TEXT,
    jefe TEXT,
    gerente1 TEXT,
    gerente2 TEXT,
    centros TEXT,  -- JSON array de centros autorizados
    estado_registro TEXT DEFAULT 'activo',
    contrasena TEXT NOT NULL,  -- bcrypt hash
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### `solicitudes` ★ TABLA PRINCIPAL
```sql
CREATE TABLE solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario TEXT NOT NULL,
    centro TEXT NOT NULL,
    sector TEXT NOT NULL,
    justificacion TEXT NOT NULL,
    centro_costos TEXT,
    almacen_virtual TEXT,
    criticidad TEXT DEFAULT 'Normal',  -- 'Normal', 'Alta'
    fecha_necesidad TEXT,
    data_json TEXT NOT NULL,  -- JSON con items
    status TEXT DEFAULT 'pendiente_de_aprobacion',
    aprobador_id TEXT,
    planner_id TEXT,
    total_monto REAL DEFAULT 0,
    notificado_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id_spm)
);

-- Estructura de data_json:
{
  "items": [
    {
      "codigo": "1000000006",
      "descripcion": "TUERCA M12",
      "cantidad": 10,
      "precio_unitario": 45.50,
      "comentario": "..."
    }
  ]
}
```

#### `materiales`
```sql
CREATE TABLE materiales (
    codigo TEXT PRIMARY KEY,  -- SAP code
    descripcion TEXT NOT NULL,
    descripcion_larga TEXT,
    centro TEXT,
    sector TEXT,
    unidad TEXT,  -- 'UNI', 'KG', 'L', etc.
    precio_usd REAL DEFAULT 0,
    activo INTEGER DEFAULT 1
);

CREATE INDEX idx_mat_desc ON materiales(descripcion);
```

#### `presupuestos`
```sql
CREATE TABLE presupuestos (
    centro TEXT,
    sector TEXT,
    monto_usd REAL DEFAULT 0,
    saldo_usd REAL DEFAULT 0,
    PRIMARY KEY(centro, sector)
);
```

#### `catalog_centros`, `catalog_sectores`, `catalog_almacenes`
```sql
CREATE TABLE catalog_centros (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    responsable TEXT
);

CREATE TABLE catalog_sectores (
    nombre TEXT PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE catalog_almacenes (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    centro_codigo TEXT,
    capacidad REAL,
    FOREIGN KEY(centro_codigo) REFERENCES catalog_centros(codigo)
);
```

#### `notificaciones`
```sql
CREATE TABLE notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destinatario_id TEXT NOT NULL,
    solicitud_id INTEGER,
    mensaje TEXT NOT NULL,
    leido INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(solicitud_id) REFERENCES solicitudes(id),
    FOREIGN KEY(destinatario_id) REFERENCES usuarios(id_spm)
);
```

#### `presupuesto_incorporaciones`
```sql
CREATE TABLE presupuesto_incorporaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    centro TEXT NOT NULL,
    sector TEXT,
    monto REAL NOT NULL,
    motivo TEXT,
    estado TEXT DEFAULT 'pendiente',  -- 'pendiente', 'aprobado', 'rechazado'
    solicitante_id TEXT NOT NULL,
    aprobador_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT,
    FOREIGN KEY(solicitante_id) REFERENCES usuarios(id_spm),
    FOREIGN KEY(aprobador_id) REFERENCES usuarios(id_spm)
);
```

#### `planificadores`
```sql
CREATE TABLE planificadores (
    usuario_id TEXT,
    centro TEXT NOT NULL,
    sector TEXT NOT NULL,
    almacen_virtual TEXT NOT NULL,
    capacidad_maxima REAL,
    estado TEXT DEFAULT 'activo',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(usuario_id, centro, sector, almacen_virtual),
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id_spm)
);
```

### Cargas de Datos Iniciales

```
src/backend/core/data/
├── Usuarios.csv       → Carga 100+ usuarios de ejemplo
├── Materiales.csv     → Carga 10,000+ materiales
└── Presupuestos.csv   → Presupuestos iniciales
```

---

## 🚀 Módulos Especializados

### 1️⃣ Planificador (`src/planner/`)

**Propósito:** Optimizar y programar solicitudes de materiales automáticamente.

**Componentes:**

```
algorithms/          → Algoritmos de optimización (ej: greedy, dynamic programming)
models/             → Modelos de datos (Request, Schedule, Resource)
scoring/            → Sistema de puntuación para priorización
optimization/       → Estrategias de optimización
filters/            → Filtros para restricciones
rules/              → Reglas de negocio
events/             → Sistema de eventos
decision_tree/      → Árboles de decisión
```

**Funcionalidades:**
- Optimización automática de solicitudes
- Asignación inteligente de recursos
- Predicción de tiempos
- Análisis de restricciones

### 2️⃣ Agentes IA (`src/agent/`)

**Propósito:** Sistema de agentes inteligentes basado en LLM.

**Componentes:**
- `catalog.py` → Catálogo de agentes disponibles
- `llm.py` → Integración con modelos de lenguaje
- `models.py` → Modelos de agentes
- `rules.py` → Reglas y limitaciones
- `main.py` → Orquestación

**Integraciones:**
- Claude API (Anthropic)
- Ollama (local LLM)

### 3️⃣ Asistente IA (`src/ai_assistant/`)

**Propósito:** Asistencia inteligente para usuarios.

**Características:**
- Chat en tiempo real
- Análisis de solicitudes
- Sugerencias automáticas
- Análisis predictivo

---

## 🔌 API REST

### Autenticación

**Tipo:** JWT Bearer Token

**Header requerido:**
```
Authorization: Bearer <token>
```

**Flujo:**
1. `POST /api/auth/login` → Retorna `access_token` y `refresh_token`
2. Incluir token en headers de requests posteriores
3. Si expira: `POST /api/auth/refresh` → Obtener nuevo token

### Códigos de Respuesta

```
200 OK                      → Éxito
201 Created                 → Recurso creado
204 No Content             → Éxito sin contenido
400 Bad Request            → Datos inválidos
401 Unauthorized           → No autenticado
403 Forbidden              → No autorizado (permisos insuficientes)
404 Not Found              → Recurso no encontrado
409 Conflict               → Conflicto (ej: email duplicado)
422 Unprocessable Entity   → Validación fallida
500 Internal Server Error  → Error del servidor
```

### Formatos de Respuesta

**Éxito:**
```json
{
  "ok": true,
  "data": { /* datos */ }
}
```

**Error:**
```json
{
  "ok": false,
  "error": "error_code",
  "message": "Descripción del error",
  "details": { /* detalles adicionales */ }
}
```

---

## 🔄 Flujos Clave

### Flujo 1: Crear Solicitud

```
1. Usuario accede a /nueva-solicitud
   ↓
2. Frontend carga catálogos (centros, materiales, etc.)
   GET /api/catalogos → Backend
   ↓
3. Usuario completa formulario:
   - Paso 1: Centro, sector, criticidad, fecha_necesidad
   - Paso 2: Buscar y agregar materiales
     GET /api/materiales?q=... → Búsqueda inteligente
   - Paso 3: Revisar y enviar
   ↓
4. Frontend valida datos localmente (Pydantic schemas)
   ↓
5. POST /api/solicitudes → Backend
   {
     "id_usuario": "usuario1",
     "centro": "1008",
     "sector": "Mantenimiento",
     "justificacion": "...",
     "centro_costos": "CC001",
     "almacen_virtual": "ALM0001",
     "criticidad": "Normal",
     "fecha_necesidad": "2025-11-15",
     "items": [
       { "codigo": "...", "cantidad": 10, "precio_unitario": 45.50 }
     ]
   }
   ↓
6. Backend:
   - Valida con Pydantic
   - Calcula total_monto
   - Verifica presupuesto disponible
   - Inserta en BD
   - Crea notificaciones para aprobadores
   ↓
7. Backend retorna: { "ok": true, "id": 1, "status": "submitted" }
   ↓
8. Frontend muestra confirmación
   Redirige a /solicitudes
```

### Flujo 2: Aprobar/Rechazar Solicitud

```
1. Admin ve solicitud pendiente en /admin-solicitudes
   ↓
2. Admin clicks "Aprobar" o "Rechazar"
   ↓
3. Frontend abre modal con opciones
   ↓
4. Admin completa detalles (comentario, etc.)
   ↓
5. POST /api/solicitudes/<id>/decidir
   {
     "decision": "aprobado|rechazado",
     "comentario": "...",
     "motivo": "..."
   }
   ↓
6. Backend:
   - Valida autorización (solo admin/coordinador)
   - Actualiza status en BD
   - Crea notificación para solicitante
   - Empieza proceso de planificación si se aprueba
   ↓
7. Frontend muestra confirmación
```

### Flujo 3: Planificación Automática

```
1. Solicitud es aprobada
   ↓
2. Trigger automático:
   POST /api/planner/solicitudes/<id>/optimize
   ↓
3. Backend (módulo planner):
   - Analiza solicitud
   - Verifica disponibilidad de materiales
   - Asigna planificador
   - Crea schedule
   - Estima fecha de entrega
   ↓
4. Backend actualiza solicitud:
   - status = "processing"
   - planner_id = <planificador asignado>
   - data_json.schedule = <schedule optimizado>
   ↓
5. Notifica al planificador asignado
```

### Flujo 4: Búsqueda de Materiales

```
1. Usuario en /nueva-solicitud paso 2 busca material
   ↓
2. Escribe en input: "tuerca" o código "1000000006"
   ↓
3. Frontend:
   - Valida entrada mínima
   - Hace debounce de 300ms
   ↓
4. GET /api/materiales?q=tuerca&limit=100
   ↓
5. Backend:
   - Busca en tabla materiales
   - LIKE COLLATE NOCASE (case-insensitive)
   - Retorna hasta 100 resultados
   - Ordena por relevancia + descripción
   ↓
6. Respuesta:
   [
     { "codigo": "1000000006", "descripcion": "TUERCA M12", "precio_usd": 45.50 },
     { "codigo": "1000000007", "descripcion": "TUERCA M16", "precio_usd": 65.00 }
   ]
   ↓
7. Frontend renderiza lista de sugerencias
   ↓
8. Usuario selecciona material
   - Se agrega a tabla
   - Calcula subtotal
   - Actualiza total_monto
```

---

## ⚙️ Configuración y Entorno

### Variables de Entorno Principales

**Archivo:** `.env` (no trackeado en Git)

```bash
# Flask
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1

# Base de datos
SPM_DB_PATH=src/backend/core/data/spm.db
SPM_LOG_PATH=src/backend/core/logs/app.log
SPM_UPLOAD_DIR=src/backend/uploads

# Seguridad
SPM_SECRET_KEY=<auto-generado en dev>
SPM_ACCESS_TTL=3600
SPM_COOKIE_SECURE=0  # 1 en producción
SPM_COOKIE_SAMESITE=Lax

# CORS
SPM_CORS_ORIGINS=http://127.0.0.1:5173

# IA
AI_ENABLE=1
AI_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
AI_MAX_SUGGESTIONS=5

# Ollama (LLM local)
SPM_OLLAMA_URL=http://127.0.0.1:11434
SPM_OLLAMA_MODEL=mistral

# Entorno
SPM_ENV=development
SPM_DEBUG=1
```

### Configuración de Desarrollo

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar (Linux/macOS)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
cp .env.example .env

# Inicializar BD
python -c "from src.backend.core.init_db import build_db; build_db()"

# Ejecutar servidor
python wsgi.py                    # Backend en 5000
npm run dev                       # Frontend en 5173
```

---

## 🚀 Guía Rápida de Desarrollo

### Iniciar Aplicación

```powershell
# Terminal 1: Backend
cd d:\GitHub\SPMv1.0
.\.venv\Scripts\Activate.ps1
python wsgi.py

# Terminal 2: Frontend
cd d:\GitHub\SPMv1.0
npm run dev
```

### URLs de Acceso

```
Frontend:     http://localhost:5173
Backend:      http://localhost:5000
API:          http://localhost:5000/api
```

### Usuario de Prueba

```
Email: usuario@ejemplo.com
Contraseña: (verificar en Usuarios.csv)
Rol: usuario
```

### Comandos Útiles

```bash
# Backend
python wsgi.py                    # Ejecutar servidor
python -m pytest tests/           # Ejecutar tests
python -c "from src.backend.core.init_db import build_db; build_db()"  # Resetear BD

# Frontend
npm run dev                       # Dev server
npm run build                     # Build para producción
npm test                          # Ejecutar tests

# Utilidades
python scripts/utilities/debug_*.py  # Scripts de debug
```

### Debugging

**Backend (Python):**
```python
# Usar print o logging
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje de debug")

# O usar debugger
import pdb; pdb.set_trace()
```

**Frontend (JavaScript):**
```javascript
// Browser DevTools
console.log("Debug info")
debugger;  // Pausa ejecución en DevTools
```

**Base de Datos:**
```bash
# Acceder a BD directamente
sqlite3 src/backend/core/data/spm.db

# Queries útiles
SELECT * FROM usuarios;
SELECT * FROM solicitudes ORDER BY created_at DESC;
SELECT * FROM materiales LIMIT 10;
```

### Estructura de Carpetas Clave para Modificaciones

```
Para agregar una nueva ruta:
- Crear archivo en src/backend/routes/nueva_ruta.py
- Registrar blueprint en src/backend/app.py
- Crear esquemas en src/backend/models/schemas.py

Para agregar una nueva página frontend:
- Crear HTML en src/frontend/
- Agregar lógica en src/frontend/app.js
- Agregar estilos en src/frontend/styles.css

Para agregar nueva tabla BD:
- Modificar src/backend/core/init_db.py
- Crear migraciones en database/migrations/
- Actualizar schemas.py si es necesario
```

---

## 📚 Documentación Adicional

Para más información, consulta:

- `docs/00_COMIENZA_AQUI.md` → Punto de entrada
- `docs/ARCHITECTURE.md` → Arquitectura detallada
- `docs/api.md` → Referencia API completa
- `docs/guides/QUICK_REFERENCE_BD.md` → Queries útiles
- `README.md` → README principal
- `DEPLOYMENT.md` → Guía de deployment
- `docs/guides/` → Múltiples guías de implementación

---

## 🔧 Próximos Pasos Típicos

1. **Agregar nueva funcionalidad:**
   - Crear ruta en backend
   - Crear esquema Pydantic
   - Crear endpoint API
   - Crear UI en frontend
   - Crear tests

2. **Debuggear problema:**
   - Revisar logs en `src/backend/core/logs/app.log`
   - Inspeccionar BD con SQLite
   - Usar DevTools del navegador
   - Revisar red API en DevTools

3. **Deployar cambios:**
   - Seguir `DEPLOYMENT.md`
   - Crear migration si hay cambios de BD
   - Generar build Vite
   - Actualizar Docker si aplica

---

**Última actualización:** 8 de noviembre de 2025
**Autor:** Análisis automático de codebase
**Revisiones:** Consulta git log para historial completo
