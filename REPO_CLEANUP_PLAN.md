# PLAN DE REORGANIZACIÓN Y LIMPIEZA DEL REPOSITORIO
**Generado**: Análisis exhaustivo - Repositorio SPM v1.0
**Estado**: LISTO PARA EJECUCIÓN

---

## RESUMEN EJECUTIVO

### Problemas Identificados
1. **15 GRUPOS DE DUPLICADOS** - Archivos HTML repetidos en 2 ubicaciones
2. **6 ARCHIVOS OBSOLETOS** - Backups viejos (.bak files)
3. **42 ARCHIVOS EN RAÍZ** - Desorganización, falta categorización
4. **14 TESTS FUERA DE CARPETA** - `test_*.py` dispersos por repo
5. **17 DOCS DISPERSOS** - Documentación fuera de `docs/`
6. **3 REQUIREMENTS** - Archivos de dependencias duplicados

**Total de issues**: 97 archivos/problemas detectados

---

## HALLAZGOS DETALLADOS

### 1️⃣ DUPLICADOS POR CONTENIDO IDÉNTICO

#### Grupo 1: Archivos de Base de Datos (vacíos)
```
- Agent/gemini2.5-agent-starter/agent/__init__.py
- src/__init__.py
```
**Acción**: ELIMINAR duplicados, MANTENER en src/__init__.py

#### Grupo 2-4: Archivos de Logo
```
Grupo 2:
- src/backend/data/SPM_logo_bundle/ChatGPT Image 13 oct 2025, 06_41_08 p.m..png
- src/backend/data/SPM_logo_bundle/SPM_logo_1024.png

Grupo 3:
- src/backend/data/SPM_logo_bundle/SPM_logo_master.svg
- src/frontend/assets/spm-logo.svg

Grupo 4:
- src/backend/uploads/ab9fffda4181438ca66a0aa5234397aa.png
- src/frontend/assets/spm-logo.png
```
**Acción**: CONSOLIDAR logos en `src/frontend/assets/`, LIMPIAR duplicados en data/

#### Grupos 5-15: HTML Pages DUPLICADAS (CRÍTICO)
```
Origen:          src/frontend/*.html
Duplicados en:   src/frontend/pages/admin/*.html
                 src/frontend/pages/user/*.html

Ejemplos:
- admin-solicitudes.html (2 copias)
- mis-solicitudes.html (2 copias)
- agregar-materiales.html (2 copias)
- reportes.html (2 copias)
- equipo-solicitudes.html (2 copias)
```
**Acción**: ELIMINAR duplicados en `pages/`, MANTENER solo en raíz de frontend

**IMPACTO**: Estos duplicados rompen el SPA. El home.html (5400+ líneas) tiene referencias a las ubicaciones antiguas. Eliminar duplicados limpia estructura.

---

### 2️⃣ ARCHIVOS OBSOLETOS PARA ELIMINAR

| Archivo | Tamaño | Razón |
|---------|--------|-------|
| `database/backup/spm.db.bak` | ? | Backup viejo de BD |
| `database/backup/spm.db.bak` | ? | Duplicado |
| `docs/archive/legacy/src_backend_server.py.bak` | ? | Código obsoleto |
| `src/backend/data/Materiales.csv.bak` | ? | Backup de datos |

**Acción**: ELIMINAR todos - Son backups viejos, la BD actual es operativa.

---

### 3️⃣ ARCHIVOS EN RAÍZ SIN CATEGORIZAR (42 archivos)

#### Documentación Dispersa (DEBE IR A docs/)
```
- FINAL_STATUS_PLANIFICACION.txt → docs/planning/
- ITERACION_COMPLETADA_*.txt → docs/history/
- MENU_NAVIGATION_COMPLETE.md → docs/guides/
- PLANIFICACION_*.md → docs/planning/
- RESUMEN_FINAL_PLANIFICACION.md → docs/planning/
- SISTEMA_REPAIRED.txt → docs/system/
- TESTING_MANUAL_PLANIFICACION.md → docs/testing/
- QUICK_REFERENCE_PLANIFICACION.txt → docs/planning/
```
**Total**: 13 archivos de docs en raíz

#### Scripts de Utilidad (DEBE IR A scripts/)
```
- analyze_repo.py → scripts/utilities/
- check_db.py → scripts/utilities/
- create_planner_demo.py → scripts/utilities/
- create_test_data.py → scripts/db/
- fix_*.py (5 archivos) → scripts/repair/
- init_db.py → scripts/db/
- list_tables.py → scripts/db/
- validate_*.py → scripts/utilities/
```
**Total**: 15 scripts en raíz

#### Verificación/Demostración (DEBE IR A docs/testing/)
```
- CHECK_FINAL.ps1 → scripts/dev/
- PLANNER_DEMO_CREDENTIALS.txt → docs/planning/
- PRUEBA_MANUAL_MENU.md → docs/testing/
- QUICK_START.txt → docs/
- VERIFY_MENU_NAVIGATION.ps1 → scripts/dev/
- validate_planificacion.sh → scripts/dev/
```
**Total**: 6 archivos de testing/verificación

#### MANTENER en Raíz (Estándar)
```
✓ .dockerignore
✓ .env
✓ .gitattributes
✓ .gitignore
✓ Dockerfile
✓ README.md
✓ docker-compose.yml
✓ jest.config.js
✓ package.json
✓ package-lock.json
✓ pyproject.toml
✓ requirements.txt (CONSOLIDAR 3 → 1)
✓ vite.config.js
```
**Total**: 13 archivos OK en raíz

---

### 4️⃣ TESTS DISPERSOS (14 archivos fuera de tests/)

**Ubicaciones incorrectas**:
- `docs/archive/form-intelligence-v2/test_form_intelligence_v2.html`
- `src/backend/static/test_auth.html`
- `src/backend/static/test_login_flow.html`
- `src/frontend/test_login_smoke.js`
- `src/planner/algorithms/test_algorithms_base.py`
- ... y 9 más

**Acción**: MOVER TODOS a `tests/` con estructura reflejada:
```
tests/
├── unit/
│   ├── backend/
│   ├── frontend/
│   └── planner/
├── integration/
└── e2e/
```

---

### 5️⃣ DOCUMENTACIÓN DISPERSA (17 archivos)

**Actualmente en**:
- `.github/copilot-instructions.md`
- `Agent/*/README.md`
- `database/audit/report.md`
- `database/migrations/README.md`
- `src/planner/README_MODELS.md`
- ... y más

**Centralizar en `docs/`** con estructura:
```
docs/
├── README.md (índice general)
├── guides/
├── api/
├── architecture/
├── planning/
├── testing/
├── history/
└── system/
```

---

### 6️⃣ REQUIREMENTS DUPLICADOS (3 archivos)

| Archivo | Ubicación | Uso |
|---------|-----------|-----|
| `requirements.txt` | Raíz | MANTENER (producción) |
| `requirements-dev.txt` | Raíz | MANTENER (desarrollo) |
| `Agent/gemini2.5-agent-starter/requirements.txt` | Agente | REVISAR si aún necesario |

**Acción**: Consolidar en raíz, eliminar duplicado del Agent si no se usa.

---

## PLAN DE EJECUCIÓN

### FASE 1: ELIMINAR DUPLICADOS (NO DESTRUCTIVO)
```bash
# HTML Pages duplicados - Eliminar copias, mantener originals
rm -r src/frontend/pages/*
# Logos duplicados - Consolidar en assets
rm src/backend/uploads/ab9fffda4181438ca66a0aa5234397aa.png
rm src/backend/data/SPM_logo_bundle/ChatGPT Image*
# Scripts de __init__.py
rm Agent/gemini2.5-agent-starter/agent/__init__.py
```

### FASE 2: ELIMINAR OBSOLETOS
```bash
# Backups viejos
rm database/backup/spm.db.bak
rm docs/archive/legacy/*.bak
rm src/backend/data/Materiales.csv.bak
```

### FASE 3: REORGANIZAR ARCHIVOS DE RAÍZ

#### Mover documentación
```bash
mkdir -p docs/planning docs/history docs/system
mv FINAL_STATUS_PLANIFICACION.txt docs/planning/
mv ITERACION_COMPLETADA_*.txt docs/history/
mv RESUMEN_FINAL_PLANIFICACION.md docs/planning/
mv SYSTEM_REPAIRED.txt docs/system/
```

#### Mover scripts
```bash
mkdir -p scripts/db scripts/repair scripts/testing
mv analyze_repo.py scripts/utilities/
mv create_test_data.py scripts/db/
mv init_db.py scripts/db/
mv fix_*.py scripts/repair/
```

### FASE 4: MOVER TESTS FUERA DE LUGAR
```bash
mkdir -p tests/unit/backend tests/unit/frontend tests/unit/planner
mv src/planner/algorithms/test_*.py tests/unit/planner/
mv src/backend/static/test_*.html tests/unit/backend/
mv src/frontend/test_*.js tests/unit/frontend/
```

### FASE 5: CONSOLIDAR DOCUMENTACIÓN
```bash
mkdir -p docs/architecture docs/api
# Revisar y consolidar todos los README.md
# Centralizar guías
```

---

## ESTRUCTURA FINAL ESPERADA

```
SPMv1.0/
├── .github/               (Configuración GitHub)
├── config/                (Configuración general)
├── database/
│   ├── audit/
│   ├── migrations/
│   ├── schemas/
│   └── fixes/
├── docs/                  (📁 TODA documentación aquí)
│   ├── README.md
│   ├── api/
│   ├── architecture/
│   ├── guides/
│   ├── planning/
│   ├── system/
│   ├── testing/
│   ├── history/
│   └── archive/
├── infrastructure/        (Terraform, nginx)
├── scripts/               (📁 TODOS los scripts aquí)
│   ├── db/
│   ├── dev/
│   ├── repair/
│   ├── testing/
│   ├── utilities/
│   └── utils/
├── src/
│   ├── agent/
│   ├── ai_assistant/
│   ├── backend/           (API Flask)
│   ├── frontend/          (SPA - sin subdirectorios redundantes)
│   └── planner/
├── tests/                 (📁 TODOS los tests aquí)
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── auth/
│   ├── e2e/
│   └── ui/
│
├── .dockerignore
├── .env
├── .gitignore
├── Dockerfile
├── README.md              (SOLO entrada principal)
├── docker-compose.yml
├── jest.config.js
├── package.json
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── vite.config.js
```

---

## IMPACTO Y BENEFICIOS

| Problema | Impacto | Beneficio |
|----------|---------|-----------|
| Duplicados HTML | Confusión, mantenimiento 2x | -33% archivos frontend |
| Archivos en raíz | Desorden, difícil encontrar | Estructura clara |
| Tests dispersos | Difícil ejecutar suite | Fácil ejecutar: `pytest tests/` |
| Docs dispersas | Confusión sobre dónde buscar | Documentación centralizada |
| .bak obsoletos | Confusión, BD vieja | Código limpio |

---

## CHECKLIST DE EJECUCIÓN

### Antes de empezar
- [ ] Backup actual del repo (git status)
- [ ] Verificar que no hay cambios sin commitear
- [ ] Crear rama `cleanup/repo-organization`

### Ejecución
- [ ] FASE 1: Eliminar duplicados HTML
- [ ] FASE 2: Limpiar archivos obsoletos
- [ ] FASE 3: Mover docs a raíz
- [ ] FASE 4: Mover scripts a carpeta
- [ ] FASE 5: Consolidar tests

### Validación
- [ ] Ejecutar: `pytest tests/` (todos los tests)
- [ ] Verificar: Flask inicia sin errores
- [ ] Verificar: Frontend carga correctamente
- [ ] Revisar: Todos los imports siguen funcionando
- [ ] Git: Sin archivos dangling

### Finalización
- [ ] Generar reporte final
- [ ] Crear commit: "chore: reorganize repo structure"
- [ ] Hacer merge a main

---

## NOTA IMPORTANTE

**Este plan NO elimina funcionalidad, solo organiza.**
- Los duplicados son exactos (no hay pérdida)
- Los .bak son backups antiguos (BD actual es operativa)
- Los scripts se mueven, no se eliminan
- Los tests se reorganizan, no se pierden

**Se recomienda**: Ejecutar FASE 1-2 ahora, luego FASE 3-5 después de validar que todo funciona.

