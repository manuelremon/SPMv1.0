# Supply Chain Planning Engine (SCPE)

## 📋 Estructura de Modelos Completada (Todo #1)

### 1. **Modelo de Maestro de Ítems** (`models/items.py`)

**Clases implementadas:**

#### `ItemMaster`
Maestro completo de material con:

- **Identificadores**: item_id, sap_code, descripción
- **Clasificación ABC**: A (80% valor), B (15%), C (5%)
- **Criticidad**: CRITICAL, HIGH, MEDIUM, LOW
- **Tipo de abastecimiento**: PURCHASE, MAKE, TRANSFER, IMPORT, VMI
- **Unidades de medida**: Base + alternativas con factores conversión
- **Especificaciones técnicas**: Dict flexible para tensión, RPM, etc.
- **Cumplimiento normativo**:
  - `requires_traceability`: bool
  - `compliance_standards`: ISO, FDA, etc.
  - `shelf_life_days`: None = indefinida
  - `requires_cold_chain`: bool
- **Estructura de producto**:
  - `is_assembly`: bool
  - `bom: List[BOMComponent]` con factores de desperdicio
- **Ítems equivalentes** (`equivalent_items: List[EquivalentItem]`):
  - Conversión técnica
  - Factor de costo diferencial
  - Confiabilidad del proveedor
- **Parámetros de control**:
  - MOQ (Minimum Order Quantity)
  - Order múltiplo (ej: pallets)
  - Días de stock de seguridad
- **Costos**: Standard cost, list price, consumo anual estimado

**Métodos principales:**
```python
get_quantity_in_base_unit(quantity, from_unit) -> float
```

#### `BOMComponent` 
Componente en lista de materiales:
- component_id, quantity, UoM
- Secuencia de ensamble
- scrap_factor (1.05 = 5% desperdicio)

#### `EquivalentItem`
Ítem equivalente:
- Conversión técnica (factor de equivalencia)
- % coincidencia de specs (0-1)
- Diferencial de costo (+5%, -10%)
- Delta de lead time
- Confiabilidad del proveedor

#### `UnitOfMeasure`
Unidad de medida:
- code: "EA", "KG", "M", "LT"
- Categoría: peso, longitud, cantidad
- Factor de conversión a UoM base

---

### 2. **Modelo de Inventario** (`models/inventory.py`)

#### `InventoryLot`
Lote único con trazabilidad completa:

- **Identificación**: lot_number, serial_number, item_id
- **Cantidades**:
  - `quantity_received`: Recibida
  - `quantity_on_hand`: Disponible en almacén
  - `quantity_reserved_hard`: Reservas confirmadas
  - `quantity_reserved_soft`: Reservas tentativas
  - `quantity_allocated`: Asignadas a SO (salidas)
  - **Propiedad**: `quantity_available` = QoH - reservas - allocated
- **Fechas**:
  - receipt_date
  - expiration_date (None = no aplica)
  - shelf_life_days
- **Control de Calidad (QC)**:
  - Status: INSPECTING, APPROVED, CONDITIONAL, REJECTED, QUARANTINE
  - qc_approver, qc_date, qc_notes
- **Ubicación física**: `locations: List[LotLocation]`
  - Warehouse, Zone, Rack, Level, Position
  - Método: `full_location()` → "ALM-1-REC-2-A1"
- **Trazabilidad**:
  - supplier_id, purchase_order, invoice_number
- **Propiedades computed**:
  - `is_expired`: ¿Vencido?
  - `days_to_expiration`: Días para expiración
  - `is_critical_expiration(threshold_days=30)`: ¿Próximo a vencer?

#### `LotLocation`
Ubicación física:
- warehouse_code, zone, rack, level, position
- Método: `full_location()` para ubicación formateada

#### `InventorySnapshot`
Fotografía de inventario en un momento:

- **Totales por almacén e ítem**:
  - total_on_hand
  - total_reserved_hard/soft
  - total_allocated
- **Salud**:
  - expired_quantity
  - critical_expiration_quantity
  - quality_hold_quantity
- **Distribución por lote**: `lots: List[InventoryLot]`
- **Análisis FEFO**:
  - Método: `get_allocation_sequence_fefo()` → Lotes ordenados por expiración FIFO
- **Propiedad**: `quantity_available` = total_on_hand - reservas - expirados - hold

---

### 3. **Modelo de Lead Times** (`models/lead_times.py`)

#### `LeadTimeDistribution`
Distribución probabilística N(μ, σ²):

- **Parámetros**:
  - mean_days (μ)
  - std_dev_days (σ)
  - min_days, max_days (límites realistas)
- **Percentiles**:
  - p50_days (mediana)
  - p95_days (95% servicio)
  - p99_days (peor caso)
- **Confianza**:
  - confidence_level (0-1)
  - sample_size (# de observaciones)

**Métodos:**
- `calculate_service_level_lead_time(service_level=0.95)`:
  - Retorna LT para nivel de servicio usando Z-score de distribución normal
- `update_with_observation(actual_lead_time_days, weight)`:
  - Actualización bayesiana simplificada de la media

#### `LeadTimeHistory`
Histórico de entregas:

- PO, fecha prometida, fecha real
- Varianza en días (positivo = retraso)
- on_time: bool
- Cantidad entregada vs. short
- Quality issues
- Propiedades computed:
  - `variance_days`: Auto-calculado
  - `on_time`: Auto-validado vs. promised_date

#### `LeadTimeEstimate`
Estimación agregada por ruta/proveedor:

- item_id, supplier_id, sourcing_path (STOCK, PURCHASE, IMPORT, etc.)
- distribution: LeadTimeDistribution
- historical_data: List[LeadTimeHistory]
- on_time_percentage (histórico)
- last_updated

**Métodos:**
- `get_recommended_lead_time(service_level=0.95)`: LT para nivel de servicio
- `add_observation(history)`: Agregar histórico y actualizar distribución

---

### 4. **Modelo de Capacidades** (`models/capacity.py`)

#### `ResourceCapacity`
Capacidad de un recurso (proveedor, almacén, transporte):

- **Identificación**:
  - resource_id, resource_type (SUPPLIER, WAREHOUSE, CUSTOMS)
  - capacity_type (SUPPLIER_CAPACITY, WAREHOUSE_CAPACITY, TRANSPORT_CAPACITY, CASH_FLOW, etc.)
- **Capacidad**:
  - capacity_value (disponible)
  - capacity_unit (kg, piezas, m³, USD, etc.)
- **Ocupación**:
  - reserved_value (reservado)
  - allocated_value (asignado)
  - Propiedad: `available_capacity` = value - reserved - allocated
  - Propiedad: `utilization_percentage` (0-100%)
- **Ventanas de disponibilidad**: available_from, available_until
- **Metadata**: updated_at, notes

**Métodos:**
- `can_allocate(required_value)` → bool
- `allocate(value, is_hard=True)` → bool
- `release(value, is_hard=True)` → None

#### `CapacityConstraint`
Restricción de capacidad en una solicitud:

- solicitud_id, resource_id
- required_value, capacity_unit
- Ventanas: required_by_date, latest_possible_date
- priority (1=crítica, 1000=baja)
- is_satisfied, satisfaction_date
- Método: `mark_satisfied()` → Marcar como cumplida

---

### 5. **Modelo de Opciones de Abastecimiento** (`models/sourcing.py`)

#### `SourcingOption`
Opción única de abastecimiento:

- **Identificación**:
  - option_id: "item_id:path_type:supplier_id"
  - sourcing_path: STOCK_LOCAL, PURCHASE, IMPORT, DISASSEMBLY, EQUIVALENT, TRANSFER, etc.
  - supplier_id (None para stock local)
- **Especificaciones**:
  - quantity_available
  - unit_of_measure
- **Costos**:
  - unit_cost_usd
  - transportation_cost_usd
  - customs_duty_usd
  - handling_cost_usd
  - Propiedad: `total_cost_per_unit` = suma de todos
- **Lead Time**:
  - lead_time_days_mean
  - lead_time_days_std
  - lead_time_days_p95
- **Confiabilidad**:
  - on_time_percentage (0-1)
  - quality_acceptance_rate (0-1)
  - availability_percentage (0-1)
- **Restricciones**:
  - minimum_order_quantity
  - order_multiple
  - maximum_order_quantity
- **Ventanas**:
  - order_deadline
  - delivery_window_start/end
- **Scoring**:
  - competitive_rank (1=mejor)
  - ranking_score (multicriteria, 0-1)
  - feasible: bool
  - feasibility_notes
- **Histórico**:
  - last_used_date
  - success_rate

#### `SourcingPath`
Ruta completa con opciones jerarquizadas:

- path_id: "solicitud_id:material_id"
- solicitud_id, material_id
- required_quantity, required_date
- options: List[SourcingOption] **ordenadas por preferencia**
  - Orden ideal: stock → liberación → ... → compra
- **Resultado**:
  - selected_option_id
  - selected_quantity
  - selected_cost
- **Análisis**:
  - total_feasible_quantity
  - total_feasible_cost
  - has_feasible_solution: bool
- **Timeline**:
  - analyzed_at, optimized_at, executed_at

**Métodos:**
- `add_option(option, rank=None)`: Agregar opción
- `get_next_viable_option(skip_ids=[])`: Próxima opción viable en jerarquía
- `calculate_total_feasible()`: Calcular totales

---

## 📐 Diagrama de Relaciones

```
ItemMaster (1) ──┬─→ (N) BOMComponent
                  ├─→ (N) EquivalentItem
                  ├─→ (N) SourcingPath
                  └─→ (N) LeadTimeEstimate

InventorySnapshot (1) ──→ (N) InventoryLot
                              ├─→ (1) ItemMaster
                              └─→ (N) LotLocation

LeadTimeDistribution ──── LeadTimeEstimate ──→ (N) LeadTimeHistory
                                               │
                                               └─→ ItemMaster + Supplier

SourcingPath (1) ──→ (N) SourcingOption
                      ├─→ ItemMaster
                      ├─→ (0,1) Supplier
                      └─→ LeadTimeEstimate

ResourceCapacity ─── CapacityConstraint
```

---

## 🚀 Próximos Pasos (Todos #2-8)

### ✅ **Todo #1: COMPLETADO**
- Modelos: ItemMaster, BOMComponent, EquivalentItem, UnitOfMeasure
- Modelos: InventoryLot, LotLocation, InventorySnapshot
- Modelos: LeadTimeDistribution, LeadTimeHistory, LeadTimeEstimate
- Modelos: ResourceCapacity, CapacityConstraint
- Modelos: SourcingOption, SourcingPath

### 📋 **Todo #2: Filtro Técnico-Legal**
Implementar función que descarta opciones por:
- Especificación técnica (mismatch vs. requirements)
- Norma de cumplimiento (FDA, ISO, etc.)
- Licencia/Configuración legal
- Shelf-life insuficiente
- Trazabilidad requerida
- Output: Conjunto factible Of

### 📊 **Todo #3: Motor de Scoring**
Calcular CTE (costo + atraso + riesgo):
- Features por opción
- Reglas de corte
- Ranking por criticidad, on-time, costo

### ⚙️ **Todo #4: MIP/ILP**
Formulación de portafolio con PuLP

### 🌳 **Todo #5: Árbol de Decisión**
Gates operacionales: stock → liberación → compra

### 🔧 **Todo #6: Algoritmos por Vía**
Heurísticas especializadas

### 📡 **Todo #7: Event-Driven**
Arquitectura de topics + orquestador

### 📋 **Todo #8: Auditoría**
Trazabilidad E2E + gobernanza

---

## 📦 Estructura de Directorios

```
src/planner/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── items.py              ✅ ItemMaster, BOMComponent, EquivalentItem
│   ├── inventory.py          ✅ InventoryLot, LotLocation, InventorySnapshot
│   ├── lead_times.py         ✅ LeadTimeDistribution, LeadTimeHistory
│   ├── capacity.py           ✅ ResourceCapacity, CapacityConstraint
│   └── sourcing.py           ✅ SourcingOption, SourcingPath
├── filters/
│   └── __init__.py           (📋 Todo #2)
├── scoring/
│   └── __init__.py           (📋 Todo #3)
├── optimization/
│   └── __init__.py           (📋 Todo #4)
├── rules/
│   └── __init__.py           (📋 Todo #5)
└── events/
    └── __init__.py           (📋 Todo #7)
```

---

## 🧪 Ejemplo de Uso (Una vez completados todos los módulos)

```python
from src.planner.models import ItemMaster, InventorySnapshot, SourcingOption, SourcingPath

# 1. Cargar maestro
item = ItemMaster(
    item_id="MAT-001",
    sap_code="100001",
    description="Rodamiento 6208-2Z",
    base_unit="EA",
    standard_cost_usd=12.50,
    abc_class="B",
    criticality="HIGH"
)

# 2. Verificar inventario
inventory = InventorySnapshot(
    warehouse_code="ALM-1",
    item_id="MAT-001",
    total_on_hand=50.0
)

# 3. Crear opciones de abastecimiento
options = [
    SourcingOption(
        option_id="MAT-001:STOCK_LOCAL:NONE",
        item_id="MAT-001",
        sourcing_path="STOCK_LOCAL",
        quantity_available=50.0,
        unit_of_measure="EA",
        unit_cost_usd=0,  # Ya en stock
        lead_time_days_mean=0
    ),
    SourcingOption(
        option_id="MAT-001:PURCHASE:SUP-001",
        item_id="MAT-001",
        sourcing_path="PURCHASE",
        supplier_id="SUP-001",
        quantity_available=500.0,
        unit_of_measure="EA",
        unit_cost_usd=12.50,
        lead_time_days_mean=14.0,
        on_time_percentage=0.96
    )
]

# 4. Crear ruta de abastecimiento
path = SourcingPath(
    path_id="SOL-001:MAT-001",
    solicitud_id="SOL-001",
    material_id="MAT-001",
    required_quantity=100.0,
    required_date=datetime(2025, 11, 10)
)

for opt in options:
    path.add_option(opt)

# 5. Análisis (próximos módulos)
# path = filters.apply_technical_filter(path)
# path = scoring.calculate_cte(path)
# solution = optimization.solve_mip(path)
```

---

## 📚 Referencias

- **Pydantic Validation**: https://docs.pydantic.dev/
- **Lead Time Distributions**: Análisis de serie temporal + distribución normal
- **FEFO Logic**: First Expire, First Out para control de lotes
- **BOM Explosion**: Referencia MRP II (Material Requirements Planning)
