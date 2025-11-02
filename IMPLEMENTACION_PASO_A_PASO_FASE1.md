# 🚀 IMPLEMENTACIÓN PASO A PASO - FASE 1

**Objetivo:** Implementar los 4 fixes críticos de validación  
**Duración Estimada:** 3-4 horas  
**Dificultad:** Media  

---

## PASO 1: Preparar el Entorno

### 1.1 Crear rama de feature
```bash
cd d:\GitHub\SPMv1.0
git checkout -b feature/fix-validaciones-fase1
git branch -v
```

### 1.2 Hacer backup del archivo original
```bash
cp src/backend/routes/solicitudes.py src/backend/routes/solicitudes.py.backup
```

### 1.3 Verificar estado actual
```bash
python -m pytest tests/ -v -k "solicitud" 2>&1 | head -50
```

---

## PASO 2: Agregar Función de Validación de Material

### 2.1 Ubicación
**Archivo:** `src/backend/routes/solicitudes.py`  
**Después de línea:** 150 (después de `_normalize_items`)  

### 2.2 Código a insertar

Agregar esta función nueva:

```python
def _validar_material_existe(con, codigo: str) -> dict[str, Any] | None:
    """
    Valida que material existe en catálogo y retorna sus datos.
    
    Args:
        con: Conexión a base de datos
        codigo: Código del material (ej: "MAT-001")
    
    Returns:
        Dict con material si existe, None si no existe
        Contiene: codigo, descripcion, precio, unidad_medida
    
    Raises:
        Nada (returns None si no existe)
    """
    if not codigo or not isinstance(codigo, str):
        return None
    
    try:
        material = con.execute(
            """
            SELECT codigo, descripcion, precio, unidad_medida
              FROM materiales
             WHERE LOWER(codigo) = LOWER(?)
             LIMIT 1
            """,
            (codigo.strip(),),
        ).fetchone()
        return material
    except Exception as e:
        import logging
        logging.error(f"Error validating material {codigo}: {e}")
        return None
```

**Verificación:**
```bash
# Buscar que la función esté en el archivo
grep -n "_validar_material_existe" src/backend/routes/solicitudes.py
```

---

## PASO 3: Actualizar `_normalize_items()`

### 3.1 Ubicación
**Archivo:** `src/backend/routes/solicitudes.py`  
**Líneas aproximadas:** 123-160  

### 3.2 Reemplazo de función

BUSCAR esta firma:
```python
def _normalize_items(raw_items) -> tuple[list[dict[str, Any]], float]:
```

REEMPLAZAR por:

```python
def _normalize_items(
    raw_items,
    con=None,
    allow_missing_description=False,
) -> tuple[list[dict[str, Any]], float]:
    """
    Normaliza y valida items de solicitud.
    
    Si con=None: Solo validación de formato
    Si con=Connection: Validación contra catálogo
    
    Args:
        raw_items: Lista de items del request
        con: Conexión BD (opcional)
        allow_missing_description: Si False, requiere descripción
    
    Returns:
        (items_validados, total)
    
    Raises:
        ValueError: Si algún item es inválido
    """
    items: list[dict[str, Any]] = []
    total = 0.0
    
    if not raw_items:
        return [], 0.0
    
    if not isinstance(raw_items, (list, tuple)):
        raise ValueError("Items debe ser una lista")
    
    for idx, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise ValueError(f"Item {idx}: no es un diccionario")
        
        # ===== CÓDIGO =====
        codigo = _coerce_str(raw.get("codigo"))
        if not codigo:
            raise ValueError(f"Item {idx}: código requerido (empty/null)")
        
        codigo = codigo.strip().upper()
        
        # ===== VALIDACIÓN CONTRA CATÁLOGO =====
        if con:
            material = _validar_material_existe(con, codigo)
            if not material:
                raise ValueError(
                    f"Item {idx}: Material '{codigo}' no existe en catálogo"
                )
            # Usar datos del catálogo como fallback
            descripcion = _coerce_str(raw.get("descripcion")) or material["descripcion"]
            precio_unitario = raw.get("precio_unitario")
            if precio_unitario is None:
                precio_unitario = material.get("precio", 0)
        else:
            material = None
            descripcion = _coerce_str(raw.get("descripcion"))
            precio_unitario = raw.get("precio_unitario")
            
            if not allow_missing_description and not descripcion:
                raise ValueError(f"Item {idx}: descripción requerida")
        
        # ===== DESCRIPCIÓN =====
        if not descripcion:
            raise ValueError(f"Item {idx}: descripción vacía")
        
        descripcion = descripcion.strip()
        if len(descripcion) > 500:
            descripcion = descripcion[:500]
        
        # ===== CANTIDAD =====
        try:
            cantidad = int(raw.get("cantidad", 0))
        except (TypeError, ValueError):
            raise ValueError(
                f"Item {idx}: cantidad debe ser entero, got {raw.get('cantidad')}"
            )
        
        if cantidad < 1:
            raise ValueError(f"Item {idx}: cantidad debe ser >= 1")
        if cantidad > 10000:
            raise ValueError(f"Item {idx}: cantidad debe ser <= 10000")
        
        # ===== PRECIO UNITARIO =====
        try:
            precio_unitario = float(precio_unitario or 0)
        except (TypeError, ValueError):
            raise ValueError(
                f"Item {idx}: precio inválido: {raw.get('precio_unitario')}"
            )
        
        if precio_unitario < 0:
            raise ValueError(f"Item {idx}: precio no puede ser negativo")
        if precio_unitario > 10000000:
            raise ValueError(
                f"Item {idx}: precio unitario debe ser < $10M"
            )
        
        # ===== SUBTOTAL =====
        subtotal = round(cantidad * precio_unitario, 2)
        
        # ===== COMENTARIO =====
        comentario = _coerce_str(raw.get("comentario")) or None
        if comentario and len(comentario) > 1000:
            comentario = comentario[:1000]
        
        # ===== ARMAR ITEM =====
        item = {
            "codigo": codigo,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio_unitario": round(precio_unitario, 2),
            "subtotal": subtotal,
            "comentario": comentario,
        }
        
        # Unidad de medida
        if con and material:
            item["unidad"] = material.get("unidad_medida", "")
        else:
            unidad = raw.get("unidad") or raw.get("uom")
            if unidad:
                item["unidad"] = _coerce_str(unidad).strip()[:50]
        
        items.append(item)
        total += subtotal
    
    # ===== VALIDACIONES GLOBALES =====
    if len(items) == 0:
        raise ValueError("Mínimo 1 item requerido")
    
    if len(items) > 50:
        raise ValueError(
            f"Máximo 50 items por solicitud (recibido {len(items)})"
        )
    
    max_total = 5_000_000  # $5M
    if total > max_total:
        raise ValueError(
            f"Total ${total:,.2f} excede límite de ${max_total:,.2f}"
        )
    
    return items, round(total, 2)
```

**Verificación:**
```bash
grep -n "def _normalize_items" src/backend/routes/solicitudes.py
```

---

## PASO 4: Agregar Validación de Aprobador

### 4.1 Nueva función: `_get_approver_config()`

Agregar después de `_resolve_approver()` (buscar por línea ~67):

```python
def _get_approver_config(total_monto: float) -> tuple[str, str]:
    """
    Retorna configuración de aprobador basado en monto.
    
    Returns: (campo_usuario, rol_fallback)
    
    Montos:
    - <= $20K: Jefe (JEFE)
    - <= $100K: Gerente Nivel 1 (GERENTE_NIVEL_1)
    - > $100K: Gerente Nivel 2 (GERENTE_NIVEL_2)
    """
    if total_monto <= 20000:
        return "jefe", "JEFE"
    elif total_monto <= 100000:
        return "gerente1", "GERENTE_NIVEL_1"
    else:
        return "gerente2", "GERENTE_NIVEL_2"
```

### 4.2 Nueva función: `_ensure_approver_exists_and_active()`

Agregar después:

```python
def _ensure_approver_exists_and_active(
    con, uid: str | None, total_monto: float = 0.0
) -> str | None:
    """
    Resuelve aprobador con fallback y validación.
    
    Estrategia:
    1. Buscar aprobador específico del usuario por email
    2. Si no existe, buscar por rol
    3. Si no existe, retornar None
    
    Args:
        con: Conexión BD
        uid: ID del usuario solicitante
        total_monto: Monto total (para determinar nivel)
    
    Returns:
        id_spm del aprobador, o None si no disponible
    """
    if not uid:
        return None
    
    user = _fetch_user(con, uid)
    if not user:
        return None
    
    campo_usuario, rol_fallback = _get_approver_config(total_monto)
    
    # ===== OPCIÓN 1: APROBADOR ESPECÍFICO DEL USUARIO =====
    approver_email = _coerce_str(user.get(campo_usuario))
    if approver_email:
        approver = con.execute(
            """
            SELECT id_spm FROM usuarios
            WHERE LOWER(mail) = LOWER(?)
              AND estado = 'activo'
            LIMIT 1
            """,
            (approver_email.lower(),),
        ).fetchone()
        
        if approver:
            return approver["id_spm"]
    
    # ===== OPCIÓN 2: FALLBACK POR ROL =====
    approver = con.execute(
        """
        SELECT id_spm FROM usuarios
        WHERE rol = ?
          AND estado = 'activo'
        ORDER BY RANDOM()
        LIMIT 1
        """,
        (rol_fallback,),
    ).fetchone()
    
    if approver:
        return approver["id_spm"]
    
    # ===== NO HAY APROBADOR =====
    import logging
    logging.warning(
        f"No approver found for user {uid}, "
        f"amount ${total_monto}, looking for: {rol_fallback}"
    )
    
    return None
```

### 4.3 Reemplazar `_resolve_approver()`

BUSCAR:
```python
def _resolve_approver(con, user, total_monto=0.0):
```

REEMPLAZAR por:

```python
def _resolve_approver(
    con, user: dict[str, Any] | None, total_monto: float = 0.0
) -> str | None:
    """
    Resuelve aprobador con validación.
    
    Usa _ensure_approver_exists_and_active() para validación robusta.
    """
    if not user or not isinstance(user, dict):
        return None
    
    uid = _coerce_str(user.get("id_spm"))
    return _ensure_approver_exists_and_active(con, uid, total_monto)
```

**Verificación:**
```bash
grep -n "_ensure_approver_exists_and_active\|_get_approver_config" src/backend/routes/solicitudes.py
```

---

## PASO 5: Agregar Validación de Planificador

### 5.1 Nueva función: `_ensure_planner_exists_and_available()`

Agregar después de las funciones de aprobador:

```python
def _ensure_planner_exists_and_available(
    con, user: dict[str, Any] | None
) -> str | None:
    """
    Resuelve planificador con fallback y validación.
    
    Estrategia:
    1. Buscar planificador específico (gerente2 o gerente1)
    2. Si no existe, buscar usuario con rol PLANIFICADOR
    3. Si no existe, retornar None
    
    Args:
        con: Conexión BD
        user: Dict del usuario solicitante
    
    Returns:
        id_spm del planificador, o None si no disponible
    """
    if not user or not isinstance(user, dict):
        return None
    
    # ===== OPCIÓN 1: PLANIFICADOR ESPECÍFICO DEL USUARIO =====
    for campo in ("gerente2", "gerente1"):
        planner_email = _coerce_str(user.get(campo))
        if planner_email:
            planner = con.execute(
                """
                SELECT id_spm FROM usuarios
                WHERE LOWER(mail) = LOWER(?)
                  AND estado = 'activo'
                LIMIT 1
                """,
                (planner_email.lower(),),
            ).fetchone()
            
            if planner:
                return planner["id_spm"]
    
    # ===== OPCIÓN 2: FALLBACK POR ROL =====
    planner = con.execute(
        """
        SELECT id_spm FROM usuarios
        WHERE LOWER(rol) IN ('planificador', 'planner')
          AND estado = 'activo'
        ORDER BY RANDOM()
        LIMIT 1
        """,
    ).fetchone()
    
    if planner:
        return planner["id_spm"]
    
    # ===== NO HAY PLANIFICADOR =====
    import logging
    logging.warning(
        f"No planner found for user {user.get('id_spm')}"
    )
    
    return None


def _resolve_planner(
    user: dict[str, Any] | None, con=None
) -> str | None:
    """
    Resuelve planificador con opcional validación BD.
    
    Si con=None: Compatible con versión antigua (sin validación)
    Si con=Connection: Validación robusta
    """
    if not user or not isinstance(user, dict):
        return None
    
    if con is None:
        # Modo compatible (sin validación)
        for field in ("gerente2", "gerente1"):
            value = _coerce_str(user.get(field))
            if value:
                return value.lower()
        return None
    
    # Modo con validación
    return _ensure_planner_exists_and_available(con, user)
```

**Verificación:**
```bash
grep -n "_ensure_planner_exists_and_available\|_resolve_planner" src/backend/routes/solicitudes.py
```

---

## PASO 6: Agregar Pre-validación Antes de Aprobar

### 6.1 Nueva función: `_pre_validar_aprobacion()`

Agregar antes de la función `decidir_solicitud()` (buscar por línea ~990):

```python
def _pre_validar_aprobacion(
    con, solicitud: dict[str, Any]
) -> tuple[bool, str | None]:
    """
    Pre-valida que una solicitud puede ser aprobada.
    
    Checks:
    1. Usuario solicitante existe y está activo
    2. Todos los materiales existen en catálogo
    3. Total es consistente
    4. Presupuesto disponible (si existe)
    5. No hay cambios pendientes
    
    Returns:
        (es_valida, error_message)
    """
    try:
        # ===== CHECK 1: USUARIO SOLICITANTE =====
        uid = solicitud.get("id_usuario")
        usuario = _fetch_user(con, uid)
        
        if not usuario:
            return False, f"Usuario solicitante '{uid}' no existe"
        
        if usuario.get("estado") != "activo":
            return False, f"Usuario solicitante no está activo: {usuario.get('estado')}"
        
        # ===== CHECK 2: MATERIALES VÁLIDOS =====
        data = _json_load(solicitud.get("data_json") or "{}")
        items = data.get("items", [])
        
        if not items:
            return False, "Solicitud sin items"
        
        for idx, item in enumerate(items):
            codigo = item.get("codigo")
            if not codigo:
                return False, f"Item {idx}: código vacío"
            
            material = _validar_material_existe(con, codigo)
            if not material:
                return False, f"Item {idx}: Material '{codigo}' no existe"
        
        # ===== CHECK 3: TOTAL CONSISTENTE =====
        total_esperado = sum(i.get("subtotal", 0) for i in items)
        total_registrado = float(solicitud.get("total_monto") or 0)
        
        # Permitir hasta 0.01 de diferencia por redondeo
        if abs(total_esperado - total_registrado) > 0.01:
            return False, (
                f"Total inconsistente: cálculo=${total_esperado:.2f} "
                f"registrado=${total_registrado:.2f}"
            )
        
        # ===== CHECK 4: PRESUPUESTO DISPONIBLE =====
        try:
            centro = solicitud.get("centro")
            centro_costos = solicitud.get("centro_costos")
            
            if centro and centro_costos:
                presupuesto = con.execute(
                    """
                    SELECT disponible FROM presupuestos
                    WHERE centro = ? AND centro_costos = ?
                    LIMIT 1
                    """,
                    (centro, centro_costos),
                ).fetchone()
                
                if presupuesto:
                    disponible = float(presupuesto.get("disponible") or 0)
                    if disponible < total_registrado:
                        return False, (
                            f"Presupuesto insuficiente: "
                            f"disponible=${disponible:,.2f} "
                            f"solicitado=${total_registrado:,.2f}"
                        )
        except Exception as e:
            # Tabla presupuestos no existe, skip
            pass
        
        # ===== CHECK 5: CAMBIOS PENDIENTES =====
        if data.get("cambios_pendientes"):
            return False, "Hay cambios pendientes de revisión"
        
        return True, None
    
    except Exception as e:
        import logging
        logging.exception(f"Error pre-validating solicitud {solicitud.get('id')}: {e}")
        return False, f"Error en pre-validación: {str(e)}"
```

**Verificación:**
```bash
grep -n "_pre_validar_aprobacion" src/backend/routes/solicitudes.py
```

---

## PASO 7: Actualizar Llamadas Existentes

### 7.1 En `_parse_full_payload()`

BUSCAR (línea ~180):
```python
items, total = _normalize_items(raw_items)
```

REEMPLAZAR por:
```python
# Obtener conexión del contexto
con = kwargs.get("con")
items, total = _normalize_items(raw_items, con=con, allow_missing_description=False)
```

### 7.2 En `crear_solicitud()` 

BUSCAR (línea ~747):
```python
items, total = _normalize_items(...)
```

VERIFICAR que tiene `con=con` pasado.

### 7.3 En `decidir_solicitud()`

BUSCAR (línea ~990):
```python
def decidir_solicitud(sol_id: int):
    # ... validación y setup ...
```

AGREGAR después de setup, antes de hacer update:
```python
# ✅ NUEVO: Pre-validación
valida, error_msg = _pre_validar_aprobacion(con, solicitud)
if not valida:
    return _json_error(
        "PRE_VALIDATION_ERROR",
        error_msg or "Pre-validación fallida",
        400
    )
```

---

## PASO 8: Testing

### 8.1 Crear archivo de test
```bash
cat > tests/test_solicitud_validations.py << 'EOF'
"""
Tests para validaciones de solicitud (Fase 1 Fixes)
"""
import pytest
from src.backend.routes.solicitudes import (
    _normalize_items,
    _validate_material_exists,
    _ensure_approver_exists_and_active,
    _ensure_planner_exists_and_available,
    _pre_validar_aprobacion,
)

class TestValidarMaterial:
    """Tests para validación de material en catálogo"""
    
    def test_material_existe(self, con):
        """Material existe en catálogo"""
        result = _validate_material_exists(con, "MAT-001")
        assert result is not None
        assert result["codigo"] == "MAT-001"
    
    def test_material_no_existe(self, con):
        """Material NO existe en catálogo"""
        result = _validate_material_exists(con, "MATERIAL-INEXISTENTE")
        assert result is None
    
    def test_normalize_items_valida_catálogo(self, con):
        """_normalize_items valida contra catálogo si con es pasado"""
        items = [
            {
                "codigo": "MAT-001",
                "descripcion": "Componente A",
                "cantidad": 10,
                "precio_unitario": 100,
            }
        ]
        
        result, total = _normalize_items(items, con=con)
        assert len(result) == 1
        assert result[0]["codigo"] == "MAT-001"
        assert total == 1000
    
    def test_normalize_items_rechaza_material_invalido(self, con):
        """_normalize_items rechaza material que no existe"""
        items = [
            {
                "codigo": "INVALID-MAT",
                "descripcion": "Componente inválido",
                "cantidad": 10,
                "precio_unitario": 100,
            }
        ]
        
        with pytest.raises(ValueError, match="no existe en catálogo"):
            _normalize_items(items, con=con)

class TestAprobador:
    """Tests para validación de aprobador"""
    
    def test_aprobador_existe(self, con, test_user):
        """Aprobador existe y está activo"""
        result = _ensure_approver_exists_and_active(con, test_user["id_spm"], 15000)
        assert result is not None
    
    def test_aprobador_no_existe(self, con):
        """Usuario sin aprobador"""
        result = _ensure_approver_exists_and_active(con, "USER-INVALID", 15000)
        # Debería retornar None, no error
        assert result is None

class TestPlanificador:
    """Tests para validación de planificador"""
    
    def test_planificador_existe(self, con, test_user):
        """Planificador existe y está activo"""
        result = _ensure_planner_exists_and_available(con, test_user)
        assert result is not None
    
    def test_sin_planificador(self, con):
        """Usuario sin planificador"""
        result = _ensure_planner_exists_and_available(con, {"id_spm": "INVALID"})
        # Debería retornar None, no error
        assert result is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF
```

### 8.2 Ejecutar tests
```bash
python -m pytest tests/test_solicitud_validations.py -v
```

---

## PASO 9: Validación Manual

### 9.1 Iniciar servidor
```bash
python run_backend.py
```

### 9.2 Test: Material inválido
```bash
curl -X POST http://localhost:5000/api/solicitudes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "items": [
      {
        "codigo": "MATERIAL-FAKE",
        "cantidad": 10,
        "precio_unitario": 100
      }
    ]
  }'
```

**Esperado:** Error 400 con mensaje "no existe en catálogo"

### 9.3 Test: Material válido
```bash
curl -X POST http://localhost:5000/api/solicitudes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "items": [
      {
        "codigo": "MAT-001",
        "cantidad": 10,
        "precio_unitario": 100
      }
    ]
  }'
```

**Esperado:** Error 201 (si tiene todos los datos)

---

## PASO 10: Commit y Push

```bash
git add src/backend/routes/solicitudes.py
git add tests/test_solicitud_validations.py
git commit -m "fix(validations): Add Phase 1 validation fixes

- Add material catalog validation
- Add approver existence and active status validation
- Add planner existence and availability validation
- Add pre-approval validation checks
- Enhance _normalize_items with catalog checks
- Add fallback strategies for approver/planner resolution

Fixes: #XXX
"

git push origin feature/fix-validaciones-fase1
```

---

## PASO 11: Code Review

Enviar PR con:
- Descripción de cambios
- Link a ANALISIS_5_PROCESOS_CRITICOS.md
- Resultados de tests
- Ejemplos de errores prevenidos

---

## ✅ CHECKLIST FINAL

- [ ] Rama creada y sincronizada
- [ ] Backup del archivo original ✓
- [ ] Fix #1 implementado ✓
- [ ] Fix #2 implementado ✓
- [ ] Fix #3 implementado ✓
- [ ] Fix #4 implementado ✓
- [ ] Tests creados y pasan ✓
- [ ] Testing manual completado ✓
- [ ] Code review pasado ✓
- [ ] Merge a main ✓
- [ ] Deploy a staging ✓
- [ ] Smoke tests en staging ✓
- [ ] Deploy a producción ✓

---

**Documento:** Implementación Paso a Paso - Fase 1  
**Versión:** 1.0  
**Estado:** 🟢 Listo para desarrollador  
**Tiempo Estimado:** 3-4 horas  
