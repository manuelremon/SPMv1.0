# ⚡ QUICK START - IMPLEMENTAR FIXES FASE 1

**Tiempo estimado:** 3-4 horas  
**Dificultad:** Media  
**Riesgo:** Bajo  

---

## 📍 EN 30 SEGUNDOS

Tienes **4 fixes críticos listos** para implementar en `src/backend/routes/solicitudes.py`:

1. ✅ Validar material existe en catálogo
2. ✅ Validar aprobador existe y está activo  
3. ✅ Validar planificador existe
4. ✅ Pre-validar antes de aprobar

**Resultado:** -50% errores silenciosos

---

## 🎬 START HERE

### Paso 1: Preparar (2 min)
```bash
cd d:\GitHub\SPMv1.0
git checkout -b feature/fix-validaciones-fase1
cp src/backend/routes/solicitudes.py src/backend/routes/solicitudes.py.backup
```

### Paso 2: Leer documentación (10 min)
```bash
# En este orden:
1. Lee FIXES_FASE_1_CRITICOS.md (overview)
2. Lee IMPLEMENTACION_PASO_A_PASO_FASE1.md (detalles)
3. Mantén ESTADO_PROYECTO_FASE1.md abierto (referencia)
```

### Paso 3: Implementar (180 min)
```bash
# Sigue IMPLEMENTACION_PASO_A_PASO_FASE1.md paso por paso
# Cada paso es una acción concreta

PASO 1: Agregar _validar_material_existe()    [10 min]
PASO 2: Actualizar _normalize_items()         [40 min]
PASO 3: Agregar validación de aprobador       [30 min]
PASO 4: Agregar validación de planificador    [30 min]
PASO 5: Agregar pre-validación                [40 min]
PASO 6: Actualizar llamadas existentes        [20 min]
```

### Paso 4: Testing (30 min)
```bash
python -m pytest tests/test_solicitud_validations.py -v
```

### Paso 5: Commit (5 min)
```bash
git add src/backend/routes/solicitudes.py
git commit -m "fix(validations): Phase 1 validation fixes"
git push origin feature/fix-validaciones-fase1
```

---

## 🔍 BÚSQUEDA RÁPIDA

### ¿Dónde va cada función?

| Función | Búscar en archivo | Acción |
|---------|------------------|--------|
| `_validar_material_existe()` | `def _normalize_items` | Agregar ANTES |
| `_get_approver_config()` | `def _resolve_approver` | Agregar ANTES |
| `_ensure_approver_exists_and_active()` | `def _resolve_approver` | Agregar ANTES |
| `_ensure_planner_exists_and_available()` | `def _normalize_items` | Agregar DESPUÉS |
| `_resolve_planner()` | `def _ensure_planner_exists_and_available` | Agregar DESPUÉS |
| `_pre_validar_aprobacion()` | `def decidir_solicitud` | Agregar ANTES |

### ¿Qué funciones editar?

| Función | Ubicación | Cambio |
|---------|-----------|--------|
| `_normalize_items()` | Línea ~123 | REEMPLAZAR TODO |
| `_resolve_approver()` | Línea ~67 | REEMPLAZAR TODO |
| `_parse_full_payload()` | Línea ~180 | Agregar `con=con` |
| `decidir_solicitud()` | Línea ~990 | Agregar pre-validación |

---

## 💻 COPIAR & PEGAR

Cada función está **lista para copiar** de:
- `FIXES_FASE_1_CRITICOS.md` (overview con explicaciones)
- `IMPLEMENTACION_PASO_A_PASO_FASE1.md` (código exacto con líneas)

Solo copia la función exacta y paste donde corresponda.

---

## 🧪 TESTING RÁPIDO

### Test 1: Material válido
```bash
python -c "
from src.backend.routes.solicitudes import _validate_material_exists
from src.backend.app import get_connection

with get_connection() as con:
    result = _validate_material_exists(con, 'MAT-001')
    if result:
        print('✅ Material encontrado:', result['codigo'])
    else:
        print('❌ Material NO encontrado')
"
```

### Test 2: Material inválido
```bash
python -c "
from src.backend.routes.solicitudes import _validate_material_exists
from src.backend.app import get_connection

with get_connection() as con:
    result = _validate_material_exists(con, 'FAKE-MATERIAL')
    if result is None:
        print('✅ Correctamente rechazado material falso')
    else:
        print('❌ BUG: Material falso fue aceptado')
"
```

### Test 3: _normalize_items con validación
```bash
python -c "
from src.backend.routes.solicitudes import _normalize_items
from src.backend.app import get_connection

with get_connection() as con:
    items = [{'codigo': 'MAT-001', 'cantidad': 10, 'precio_unitario': 100}]
    try:
        result, total = _normalize_items(items, con=con)
        print('✅ Items normalizados correctamente')
        print(f'   Total: {total}')
    except ValueError as e:
        print(f'❌ Error: {e}')
"
```

---

## 🚨 SI ALGO FALLA

### Sintaxis error en Python
```bash
# Verificar sintaxis
python -m py_compile src/backend/routes/solicitudes.py

# Si falla, revisar líneas indicadas
```

### Import error
```bash
# Verificar que todas las funciones estén definidas
grep -n "def _validar_material_existe\|def _get_approver_config\|def _ensure_approver" \
  src/backend/routes/solicitudes.py

# Deben mostrar 6 funciones nuevas
```

### Database error
```bash
# Verificar que tabla materiales existe
python -c "
from src.backend.app import get_connection
with get_connection() as con:
    tables = con.execute(
        \"SELECT name FROM sqlite_master WHERE type='table'\"
    ).fetchall()
    print('Tablas:', [t[0] for t in tables])
"
```

### Rollback si algo va mal
```bash
# Restaurar backup
cp src/backend/routes/solicitudes.py.backup src/backend/routes/solicitudes.py
git checkout -- src/backend/routes/solicitudes.py

# O deshacer último commit
git reset --hard HEAD~1
```

---

## 📊 CHECKPOINTS

Después de cada fix, verificar:

✅ **Fix #1 (Material):**
```python
from src.backend.routes.solicitudes import _validar_material_existe
# Debe existir función
```

✅ **Fix #2 (Aprobador):**
```python
from src.backend.routes.solicitudes import _ensure_approver_exists_and_active
# Debe existir función
```

✅ **Fix #3 (Planificador):**
```python
from src.backend.routes.solicitudes import _ensure_planner_exists_and_available
# Debe existir función
```

✅ **Fix #4 (Pre-validación):**
```python
from src.backend.routes.solicitudes import _pre_validar_aprobacion
# Debe existir función
```

---

## ⏱️ TIMELINE REALISTA

```
HORA 0:00 - Preparar repo
         - Leer documentación
         
HORA 0:15 - FIX #1 empezado
         - _validar_material_existe() agregada
         - _normalize_items() actualizada

HORA 1:00 - FIX #2 empezado
         - Funciones de aprobador agregadas
         - _resolve_approver() actualizada

HORA 1:45 - FIX #3 empezado
         - Funciones de planificador agregadas
         - Llamadas actualizadas

HORA 2:15 - FIX #4 empezado
         - _pre_validar_aprobacion() agregada
         - Integrada en decidir_solicitud()

HORA 3:00 - Testing
         - Tests unitarios
         - Tests manuales con curl
         - Debugging si falla

HORA 3:45 - Commit
         - git add
         - git commit
         - git push

HORA 4:00 - ✅ DONE
```

---

## 🎓 QUÉ APRENDERÁS

- Cómo validar datos contra BD
- Fallback strategies (primaria + fallback)
- Pre-validation patterns
- Testing de funciones con BD
- Git workflow (branching + commits)

---

## 📚 DOCUMENTOS DE REFERENCIA

| Doc | Propósito | Cuándo usar |
|-----|----------|-------------|
| FIXES_FASE_1_CRITICOS.md | Overview + código | Entender qué y por qué |
| IMPLEMENTACION_PASO_A_PASO_FASE1.md | Instrucciones exactas | Paso a paso durante implementación |
| ANALISIS_5_PROCESOS_CRITICOS.md | Contexto completo | Entender el problema profundamente |
| ESTADO_PROYECTO_FASE1.md | Roadmap + métricas | Visión general del proyecto |

---

## 🎯 OBJETIVO

Después de 4 horas:

✅ 4 validaciones críticas implementadas  
✅ 6 funciones nuevas + 4 funciones actualizadas  
✅ Errores silenciosos reducidos ~50%  
✅ Código en branch, listo para review  

---

## ✨ BONUS TIPS

1. **Usa VS Code search** (Ctrl+F) para encontrar líneas rápidamente
2. **Abre dos tabs** - uno con doc, otro con código
3. **Test individual functions** antes de test end-to-end
4. **Commit frecuente** - cada fix es un commit separado
5. **Mantén backup** - ya hiciste uno, está en .backup

---

## 🆘 NECESITO AYUDA

### Si no entiendes qué hace una función:
→ Ver el docstring en IMPLEMENTACION_PASO_A_PASO_FASE1.md

### Si no sabes dónde insertar código:
→ Buscar el nombre de función en el archivo (Ctrl+F)
→ Ver línea aproximada en tabla de QUICK START

### Si tests fallan:
→ Verificar que materiales/usuarios existan en BD
→ Ejecutar queries manuales en DB
→ Ver logs en terminal donde corre Flask

### Si hay merge conflicts:
→ `git status` para ver archivos conflictivos
→ Resolver manualmente uno por uno
→ `git add` + `git commit`

---

**Estado:** 🟢 LISTO PARA COMENZAR  
**Próximo paso:** Abre IMPLEMENTACION_PASO_A_PASO_FASE1.md y comienza en PASO 1  
**Tiempo total:** 4 horas | 🔴 NO DESISTIR 🔴

---

*Que la fuerza esté contigo ⚡*
