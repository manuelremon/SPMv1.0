# 🎯 SPM - Sistema de Solicitudes de Materiales

Una aplicación web profesional para gestionar solicitudes de materiales, construida con **Flask** (backend) + **Vite + JavaScript** (frontend).

**Versión:** 1.0 | **Estado:** ✅ Producción | **Última actualización:** Octubre 2025

---

## 📌 Descripción General

SPM es un sistema integral de gestión de solicitudes diseñado para optimizar procesos administrativos:

- ✅ **Autenticación segura** basada en roles (Admin, Coordinador, Usuario)
- ✅ **Flujo de aprobación** completo con notificaciones
- ✅ **Gestión de materiales** y almacenes multiubicación
- ✅ **Reportes y análisis** en tiempo real
- ✅ **Consola IA** para asistencia inteligente
- ✅ **API REST** completamente documentada
- ✅ **Interfaz moderna y responsiva**

---

## 📋 Requisitos Previos

| Componente | Versión | Propósito |
|-----------|---------|----------|
| Python | 3.11+ / 3.12 | Backend y scripts |
| Node.js | 18+ | Build del frontend |
| Docker | Última | Contenedorización (opcional) |
| SQLite | Incluido | Base de datos |
| Git | 2.0+ | Control de versiones |

---

## 🚀 Inicio Rápido

### 1️⃣ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/manuelremon/SPMv1.0.git
cd SPMv1.0

# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env .env.local
# Editar .env.local con tus valores

# Ejecutar servidor
python src/backend/app.py
```

✅ Disponible en: `http://localhost:5000`

### 2️⃣ Instalación con Docker

```bash
# Construir e iniciar
docker compose up --build

# Solo iniciar (sin rebuild)
docker compose up
```

✅ Disponible en: `http://localhost:5000`

---

## 📁 Estructura del Proyecto

```
SPMv1.0/
├── src/                              # 📦 Código fuente
│   ├── backend/                      # 🔧 API Flask
│   │   ├── app.py                   # ⚙️ Aplicación principal
│   │   ├── auth.py                  # 🔐 Autenticación JWT
│   │   ├── routes/                  # 🛣️ Endpoints API
│   │   ├── models/                  # 📊 Modelos BD (SQLAlchemy)
│   │   ├── services/                # 💼 Lógica de negocio
│   │   ├── middleware/              # 🚀 Middleware personalizado
│   │   ├── core/                    # 🔌 Utilidades core
│   │   └── data/                    # 📥 CSV para inicialización
│   │
│   ├── frontend/                     # 🎨 Interfaz web
│   │   ├── index.html               # 🏠 Punto de entrada
│   │   ├── components/              # 🧩 Componentes JS
│   │   ├── pages/                   # 📄 Páginas principales
│   │   ├── ui/                      # 🎭 Componentes UI
│   │   ├── styles.css               # 🎨 Estilos globales
│   │   └── utils/                   # 🛠️ Funciones de utilidad
│   │
│   └── agent/                        # 🤖 Asistente IA (prototipo)
│
├── config/                           # ⚙️ Configuraciones
├── database/                         # 🗄️ Base de datos
│   ├── migrations/                  # 📜 Scripts de migración
│   └── seeds/                       # 🌱 Datos iniciales
│
├── docs/                             # 📚 Documentación
│   ├── guides/                      # 📖 Guías de uso
│   ├── api/                         # 🔌 Documentación API
│   ├── archive/                     # 📦 Documentación histórica
│   ├── CHANGELOG.md                 # 📝 Historial de cambios
│   └── STRUCTURE.md                 # 🗂️ Estructura técnica
│
├── infrastructure/                  # 🏗️ Infraestructura
├── scripts/                          # 🔨 Utilidades
│   ├── utilities/                   # 🛠️ Scripts de desarrollo
│   └── migrations/                  # 🔄 Scripts de migración
│
├── tests/                            # ✅ Suite de pruebas
│   ├── unit/                        # 🔬 Pruebas unitarias
│   ├── integration/                 # 🔗 Pruebas de integración
│   └── e2e/                         # 🚀 Pruebas end-to-end
│
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
├── 📦 package.json & requirements.txt
├── ⚙️ Archivos de configuración
└── 📖 README.md (este archivo)
```

---

## 🔧 Configuración de Entorno

Crea `.env` en la raíz:

```env
# 🔐 Seguridad
SPM_SECRET_KEY=tu-clave-secreta-super-segura-aqui
AUTH_BYPASS=0                    # 0=producción, 1=desarrollo

# 🗄️ Base de Datos
SPM_DB_PATH=./spm.db
SPM_UPLOAD_DIR=./uploads

# 🔧 Flask
FLASK_ENV=development
DEBUG=1
FLASK_APP=src/backend/app.py

# 🚀 Servidor
PORT=5000
HOST=0.0.0.0
```

---

## 📚 Documentación

### 👥 Para Usuarios Finales
- 📖 [Guía de Inicio](docs/guides/GUIA_INICIO.md)
- 📋 [Gestión de Solicitudes](docs/guides/)
- 📊 [Reportes y Análisis](docs/guides/)

### 👨‍💻 Para Desarrolladores
- 🔧 [Guía de Desarrollo](docs/guides/README-dev.md)
- 🔌 [API REST Documentation](docs/api/)
- 🏗️ [Arquitectura Técnica](docs/STRUCTURE.md)

### ⚡ Referencia Rápida
- ⚡ [Quick Start](docs/guides/QUICK_START.md)
- 🔍 [Referencias de BD](docs/guides/QUICK_REFERENCE_BD.md)

---

## 🧪 Ejecutar Pruebas

```bash
# ✅ Unitarias
pytest tests/unit/ -v

# 🔗 Integración
pytest tests/integration/ -v

# 🚀 End-to-end
pytest tests/e2e/ -v

# 📊 Con cobertura
pytest tests/ --cov=src --cov-report=html
```

---

## 🐳 Despliegue

### Docker
```bash
# Construir e iniciar
docker compose up --build

# Detener
docker compose down
```

### Servidor Flask Local
```bash
python src/backend/app.py
```

---

## 💾 Base de Datos

```bash
# Inicializar
python scripts/utilities/seed_db.py

# Inspeccionar
python scripts/utilities/inspect_tables.py

# Verificar esquema
python scripts/utilities/check_schema.py
```

---

## 🔐 Seguridad

✅ **Implementado:**
- JWT Tokens para autenticación
- CORS configurado
- Protección CSRF
- ORM contra SQL Injection
- Validación de entrada
- Encriptación con bcrypt

⚠️ **Checklist Producción:**
- [ ] Cambiar `SPM_SECRET_KEY`
- [ ] Desactivar `AUTH_BYPASS` (= 0)
- [ ] Configurar HTTPS/SSL
- [ ] Revisar permisos de archivos
- [ ] Configurar backups

---

## 🤝 Contribuir

1. Fork el repositorio
2. `git checkout -b feature/nueva-funcionalidad`
3. Haz cambios y commits
4. `git push origin feature/nueva-funcionalidad`
5. Abre Pull Request

**Estándares:**
- Python: PEP 8
- JavaScript: ESLint
- Mensajes en español

---

## 🆘 Troubleshooting

**Error de BD:**
```bash
rm spm.db
python scripts/utilities/seed_db.py
```

**Puerto ocupado:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Dependencias:**
```bash
pip install --upgrade -r requirements.txt
```

---

## 📦 Cambios Recientes

**v1.0 - Octubre 2025:**
- ✨ Reorganización completa
- 🗑️ Eliminación de obsolescencias
- 📚 Documentación actualizada
- 🔧 Configuración centralizada

Ver [CHANGELOG.md](docs/CHANGELOG.md) para más.

---

**¡Gracias por usar SPM!** 🚀

*Última actualización: Octubre 26, 2025*
