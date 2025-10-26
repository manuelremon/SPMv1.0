# Filtro Técnico-Legal (Nivel 1 - Todo #2) ✅ COMPLETADO

## 🎯 Propósito

Filtrar opciones de abastecimiento rechazando las que **NO cumplen** especificaciones técnicas, normas regulatorias o restricciones operacionales.

**Input:** Ruta con N opciones de abastecimiento + Maestro de material  
**Output:** Conjunto factible Of (opciones viables) + motivos de rechazo

---

## 🔍 Criterios de Filtrado

### 1. **Control de Calidad (QC)**
- ❌ Rechaza lotes con `qc_status = REJECTED`
- ❌ Rechaza lotes con `qc_status = QUARANTINE`
- ❌ Rechaza lotes en inspección si son críticos

### 2. **Vencimiento (Shelf-Life)**
- ❌ Rechaza lotes `expired = True`
- ❌ Rechaza lotes con `days_to_expiration ≤ 7` si hay almacenaje
- ❌ Valida: `shelf_life_days > min_storage_days (14 días recomendado)`

### 3. **Trazabilidad**
- ✅ Si material requiere trazabilidad (`requires_traceability = True`):
  - ✅ Acepta: STOCK_LOCAL (con lot_number)
  - ✅ Acepta: PURCHASE (proveedor documentado)
  - ❌ Rechaza: EQUIVALENT, DISASSEMBLY, RECOVERY (sin garantía)

### 4. **Cumplimiento Normativo**
- Valida contra `compliance_standards` requeridos
- ❌ Rechaza si faltan normas ISO, FDA, ROHS, etc.
- Ejemplo:
  ```
  Item requiere: [ISO-13485, FDA-21-CFR, ROHS]
  Option tiene: [ISO-9001, ISO-13485]
  → RECHAZA (faltan FDA-21-CFR, ROHS)
  ```

### 5. **Restricciones Ambientales**
- ❌ Rechaza rutas prohibidas por regulación
- Ejemplo: `PURCHASE_IMPORT` prohibido para ítems peligrosos
- Configurable por item_id

### 6. **Proveedores**
- ❌ Rechaza proveedores en **lista negra**
- ❌ Rechaza proveedores **suspendidos**
- ✅ Mantiene histórico de restricciones

### 7. **Lead Time**
- ✅ Valida: `LT_mean + σ ≤ required_date`
- ❌ Rechaza si `delivery_date > required_date`

### 8. **Especificación Técnica**
- Para opciones EQUIVALENT: valida `technical_specs_match ≥ 85%`
- ❌ Rechaza si match < umbral

### 9. **Estado del Ítem**
- ❌ Rechaza ítems con `active = False` (obsoletos)

---

## 📚 Clase Principal: `TechnicalLegalFilter`

### Métodos públicos:

#### `register_supplier_as_suspended(supplier_id: str)`
Suspender proveedor temporalmente
```python
filter_obj.register_supplier_as_suspended("SUP-BAD")
```

#### `register_supplier_blacklist(supplier_id: str)`
Agregar proveedor a lista negra permanente
```python
filter_obj.register_supplier_blacklist("SUP-BLOCKED")
```

#### `set_environmental_restriction(item_id: str, sourcing_paths: List[str])`
Establecer rutas prohibidas para un material
```python
filter_obj.set_environmental_restriction(
    "MAT-HAZMAT", 
    ["PURCHASE_IMPORT", "INTERCOMPANY"]
)
```

#### `set_regulatory_requirements(item_id: str, standards: List[str])`
Establecer normas requeridas
```python
filter_obj.set_regulatory_requirements(
    "MAT-MEDICAL",
    ["ISO-13485", "FDA-21-CFR", "CE-MARK"]
)
```

#### `filter_option(option, item, required_date=None, inventory_lot=None) → FilterResult`
**Filtrar una opción individual**

```python
result = filter_obj.filter_option(
    option=option,
    item=item,
    required_date=datetime(2025, 11, 10),
    inventory_lot=lot  # Si es stock
)

# FilterResult:
# .option_id: str
# .feasible: bool
# .reasons: List[FilterReason]
# .rejection_notes: str
# .confidence_level: float
```

#### `filter_path(path, item, inventory_lots=None) → SourcingPath`
**Filtrar todas las opciones en una ruta**

```python
# Antes del filtrado:
path.options = [opt1, opt2, opt3, opt4]

# Aplicar filtro
filtered_path = filter_obj.filter_path(path, item)

# Después:
# - opt1.feasible = True
# - opt2.feasible = False (razones en opt2.feasibility_notes)
# - opt3.feasible = True
# - opt4.feasible = False
# - path.has_feasible_solution = True/False
# - path.total_feasible_quantity actualizado
```

#### `get_feasible_options(path: SourcingPath) → List[SourcingOption]`
Obtener solo opciones viables
```python
viable = filter_obj.get_feasible_options(path)
# Retorna lista ordenada por preferencia
```

#### `generate_filter_report(path: SourcingPath) → Dict`
Generar reporte de filtrado
```python
report = filter_obj.generate_filter_report(path)
# {
#   "path_id": "SOL-001:MAT-001",
#   "total_options": 5,
#   "feasible_count": 2,
#   "infeasible_count": 3,
#   "feasibility_rate": 0.4,
#   "has_solution": true,
#   "feasible_options": [...],
#   "rejected_options": [...]
# }
```

---

## 📊 Enum: `FilterReason`

Motivos de rechazo:

```python
class FilterReason(str, Enum):
    SPEC_MISMATCH = "SPEC_MISMATCH"
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    LICENSE_ISSUE = "LICENSE_ISSUE"
    SHELF_LIFE_INSUFFICIENT = "SHELF_LIFE_INSUFFICIENT"
    TRACEABILITY_REQUIRED = "TRACEABILITY_REQUIRED"
    QUALITY_HOLD = "QUALITY_HOLD"
    EXPIRED = "EXPIRED"
    REGULATORY_HOLD = "REGULATORY_HOLD"
    SUPPLIER_SUSPENDED = "SUPPLIER_SUSPENDED"
    ENVIRONMENTAL_RESTRICTION = "ENVIRONMENTAL_RESTRICTION"
    LEAD_TIME_VIOLATION = "LEAD_TIME_VIOLATION"
    OBSOLETE = "OBSOLETE"
    CUSTOM_RULE = "CUSTOM_RULE"
```

---

## 🧪 Ejemplos de Uso

### Ejemplo 1: Filtrar opción de stock expirado
```python
from src.planner.filters import TechnicalLegalFilter
from src.planner.models import ItemMaster, SourcingOption, InventoryLot, QCStatus

filter_obj = TechnicalLegalFilter()

# Lote vencido
expired_lot = InventoryLot(
    lot_number="LOT-001",
    item_id="MAT-001",
    ...
    expiration_date=datetime.utcnow() - timedelta(days=30)
)

# Opción de stock
option = SourcingOption(
    option_id="MAT-001:STOCK_LOCAL:NONE",
    item_id="MAT-001",
    sourcing_path="STOCK_LOCAL",
    quantity_available=100,
    ...
)

# Item
item = ItemMaster(
    item_id="MAT-001",
    sap_code="100001",
    ...
)

# Filtrar
result = filter_obj.filter_option(option, item, inventory_lot=expired_lot)

print(result.feasible)  # False
print(result.reasons)   # [FilterReason.EXPIRED]
print(result.rejection_notes)  # "Lote expirado: 2025-09-27 12:34:56"
```

### Ejemplo 2: Validar requisitos normativos
```python
# Establecer requisitos para material médico
filter_obj.set_regulatory_requirements(
    "MAT-STENT",
    ["ISO-13485", "FDA-21-CFR", "CE-MARK"]
)

# Item que no cumple
item = ItemMaster(
    item_id="MAT-STENT",
    compliance_standards=["ISO-9001"]  # Le falta ISO-13485, FDA-21-CFR, CE-MARK
)

# Filtrar
result = filter_obj.filter_option(option, item)

print(result.feasible)  # False
print(result.reasons)  # [FilterReason.COMPLIANCE_VIOLATION]
print(result.rejection_notes)  # "Normas faltantes: ISO-13485, FDA-21-CFR, CE-MARK"
```

### Ejemplo 3: Filtrar ruta completa
```python
# Suspender proveedor
filter_obj.register_supplier_as_suspended("SUP-PROBLEMATIC")

# Crear ruta con 3 opciones
path = SourcingPath(
    path_id="SOL-001:MAT-001",
    solicitud_id="SOL-001",
    material_id="MAT-001",
    required_quantity=100,
    required_date=datetime.utcnow() + timedelta(days=30)
)

# Agregar opciones
opt1 = SourcingOption(...sourcing_path="STOCK_LOCAL"...)  # ✅ Viable
opt2 = SourcingOption(...supplier_id="SUP-PROBLEMATIC"...)  # ❌ Rechazada
opt3 = SourcingOption(...supplier_id="SUP-GOOD"...)  # ✅ Viable

path.add_option(opt1)
path.add_option(opt2)
path.add_option(opt3)

# Filtrar
filtered_path = filter_obj.filter_path(path, item)

# Resultados
viable = filter_obj.get_feasible_options(filtered_path)
print(len(viable))  # 2

report = filter_obj.generate_filter_report(filtered_path)
print(report["feasibility_rate"])  # 0.6667 (2 de 3)
print(report["has_solution"])  # True
```

---

## 🧬 Integración con el Pipeline

```
┌──────────────────┐
│  SourcingPath    │
│  (N opciones)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  NIVEL 1: FILTRO TÉCNICO-LEGAL       │ ◄─── TODO #2 (COMPLETADO)
│  (Elimina opciones no viables)       │
│  Output: Conjunto factible Of        │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  NIVEL 2: SCORING PROBABILÍSTICO     │ ◄─── TODO #3 (Próximo)
│  (Calcula CTE: costo + atraso + riesgo)
│  Output: Ranking de opciones         │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  NIVEL 3: OPTIMIZACIÓN MIP/ILP       │ ◄─── TODO #4
│  (Selecciona portafolio óptimo)      │
│  Output: Solución de abastecimiento  │
└──────────────────────────────────────┘
```

---

## 📈 Estadísticas de Filtrado

El reporte incluye:
- **total_options**: # opciones originales
- **feasible_count**: # opciones viables
- **infeasible_count**: # opciones rechazadas
- **feasibility_rate**: % viable (0-1)
- **has_solution**: ¿Hay al menos 1 opción viable?
- **feasible_options**: Detalles de viables
- **rejected_options**: Detalles de rechazadas

---

## 🔧 Configuración Recomendada

Al inicializar `TechnicalLegalFilter`:

```python
filter_obj = TechnicalLegalFilter()

# 1. Suspender proveedores con problemas
filter_obj.register_supplier_as_suspended("SUP-LATE-DELIVERIES")
filter_obj.register_supplier_as_suspended("SUP-QUALITY-ISSUES")

# 2. Agregar a lista negra proveedores rechazados
filter_obj.register_supplier_blacklist("SUP-FRAUD")

# 3. Establecer restricciones ambientales
filter_obj.set_environmental_restriction("MAT-HAZMAT-001", ["IMPORT"])
filter_obj.set_environmental_restriction("MAT-BATTERY", ["INTERCOMPANY", "EXPEDITE"])

# 4. Configurar requisitos normativos
filter_obj.set_regulatory_requirements(
    "MAT-PHARMA-001",
    ["ISO-13485", "FDA-21-CFR", "ROHS"]
)

# Ahora está listo para filtrar
```

---

## 📋 Checklist de Verificación

- ✅ Filtro rechaza lotes vencidos
- ✅ Filtro valida trazabilidad requerida
- ✅ Filtro verifica cumplimiento normativo
- ✅ Filtro detecta proveedores suspendidos
- ✅ Filtro valida lead time vs. fecha requerida
- ✅ Filtro genera reportes detallados
- ✅ Tests unitarios completos
- ✅ Documentación completa

---

## 🚀 Próximo: TODO #3

**Motor de Scoring Probabilístico (Nivel 2)**
- Calcular CTE (costo total esperado)
- Features: costo, μ_LT, σ_LT, confiabilidad, riesgo
- Ranking multicriteria
- Reglas de corte por criticidad
