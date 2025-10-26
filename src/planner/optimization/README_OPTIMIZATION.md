# 📊 Motor de Optimización MIP/ILP - SPM v1.0

## 📑 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Componentes](#componentes)
4. [API Reference](#api-reference)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Estrategias de Resolución](#estrategias-de-resolución)
7. [Tests](#tests)

---

## 📋 Descripción General

El **motor de optimización MIP/ILP** es el **Nivel 3** del pipeline de SPM (Planner de Materiales).

**Objetivos:**
- Minimizar costo total (CTE) del portafolio
- Respetar restricciones de demanda, capacidad, tiempo, presupuesto
- Generar soluciones factibles en tiempo real

**Formulación matemática:**

```
minimize: Σᵢ CTEᵢ × xᵢ

subject to:
  Σᵢ qtyᵢ × xᵢ ≥ demand           (Demanda)
  Σᵢ inv_iⱼ ≤ cap_j  ∀j           (Capacidad)
  LT_i ≤ LT_max  ∀i               (Lead time)
  SL_i ≥ SL_min  ∀i               (Service level)
  FEFO (First-Expire-First-Out)   (Rotación)
  Σᵢ cost_i × xᵢ ≤ budget         (Presupuesto)
  Σₖ y_ik ≤ 1  ∀i                 (One-in: máx 1 proveedor)
  xᵢ ∈ {0,1}, qty_i ≥ 0           (Dominios)
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│ SolverManager (orquestador principal)                  │
├─────────────────────────────────────────────────────────┤
│ ├─ Estrategia EXACT: PuLP+CBC (óptimo)                │
│ ├─ Estrategia GREEDY: heurística rápida               │
│ └─ Estrategia GREEDY_WITH_REOPT: greedy + local search│
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ConstraintBuilder                                  │ │
│ │ ├─ Demanda, FEFO, Capacidad                       │ │
│ │ ├─ Lead Time, Service Level                       │ │
│ │ └─ Presupuesto, Transferencias, One-in            │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ OptimizationModel (formulation.py)                 │ │
│ │ ├─ Variables: xᵢ (binarias), qtyᵢ (continuas)    │ │
│ │ └─ Solver: PuLP + CBC                             │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ModelAnalyzer (análisis post-opt)                  │ │
│ │ ├─ Viabilidad, Sensibilidad                       │ │
│ │ ├─ Desglose de costos, Robustez                   │ │
│ │ └─ Reportes (JSON, HTML)                          │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes

### **1. constraint_builder.py**

Constructor fluido de restricciones con validación.

**Clases principales:**

| Clase | Propósito | Parámetros |
|-------|-----------|-----------|
| `ConstraintBuilder` | Builder fluido | - |
| `DemandConstraint` | Demanda mínima | item_id, quantity, UoM |
| `FEFOConstraint` | Consumir por vencimiento | item_id, batches |
| `CapacityConstraint` | Límite de inventario | location_id, max_units |
| `LeadTimeConstraint` | Entrega a tiempo | option_id, deadline, LT_mean, LT_std |
| `ServiceLevelConstraint` | Disponibilidad mínima | item_id, min_SL |
| `TransferConstraint` | Transferencias entre centros | from/to, qty, cost |
| `OneInConstraint` | Máximo 1 proveedor | item_id, allowed_suppliers |
| `BudgetConstraint` | Límite presupuestario | total_budget, contingency% |
| `SourcingPreferenceConstraint` | Preferencia de fuente (soft) | item_id, preferred_supplier |

**Método clave:**

```python
builder = ConstraintBuilder()
constraints = (builder
    .add_demand_constraint("SKU001", 100, "unidades")
    .add_capacity_constraint("CDMX", 500, current_inventory=50)
    .add_budget_constraint(50000, currency="USD", contingency_pct=5)
    .add_lead_time_constraint("SUP_A", "2025-10-30", 10, 2)
    .build())
```

### **2. formulation.py**

Formulación MIP/ILP usando PuLP.

**Clases principales:**

| Clase | Responsabilidad |
|-------|-----------------|
| `OptimizationModel` | Construye y resuelve modelo MIP |
| `PortfolioVariable` | Variable de decisión (opción del portafolio) |
| `SolutionAnalyzer` | Análisis de la solución (viabilidad, sensibilidad) |
| `SolverStatus` | Enum de estados |

**Métodos clave:**

```python
model = OptimizationModel(
    item_id="SKU001",
    demand=100,
    required_date="2025-10-30",
    cte_scores=[
        {"option_id": "OPT_A", "cte": 50, "qty": 100},
        {"option_id": "OPT_B", "cte": 45, "qty": 150},
    ],
    constraints=constraints
)

model.build()                       # Construye MIP
success, solution = model.solve()   # Resuelve
```

### **3. solver_manager.py**

Orquestador del solver con múltiples estrategias.

**Clases principales:**

| Clase | Propósito |
|-------|-----------|
| `SolverManager` | Orquestador principal (público) |
| `GreedySolver` | Heurística greedy (rápida) |
| `LocalSearchOptimizer` | Optimización local (2-opt) |
| `SolverConfig` | Configuración del solver |
| `SolverResult` | Resultado de resolución |
| `SolverStrategy` | Enum de estrategias |

**Estrategias:**

1. **EXACT**: PuLP+CBC (optimal, pero lento para instancias grandes)
2. **GREEDY**: Heurística greedy (rápida, aprox. solución)
3. **GREEDY_WITH_REOPT**: Greedy + local search (balance)

**Ejemplo:**

```python
config = SolverConfig(
    strategy=SolverStrategy.GREEDY_WITH_REOPT,
    time_limit_seconds=300,
    gap_tolerance=0.05
)

manager = SolverManager(config)

result = manager.solve(
    item_id="SKU001",
    demand=100,
    required_date="2025-10-30",
    cte_scores=[...],
    constraints=constraints
)

print(f"Éxito: {result.success}")
print(f"Costo: {result.objective_value:.2f}")
print(f"Opciones seleccionadas: {result.solution['selected_options']}")
```

### **4. model_analyzer.py**

Análisis post-optimización y reportes.

**Clases principales:**

| Clase | Propósito |
|-------|-----------|
| `ModelAnalyzer` | Analizador principal |
| `ViabilityReport` | Reporte de viabilidad |
| `CostBreakdownReport` | Desglose de costos |
| `SensitivityAnalysis` | Análisis de sensibilidad |
| `RobustnessAnalyzer` | Análisis de robustez |

**Métodos clave:**

```python
analyzer = ModelAnalyzer()

# Análisis completo
analysis = analyzer.analyze_solution(solver_result, constraints)

# Reportes
report = analyzer.generate_report(
    solver_result=result,
    constraints=constraints,
    include_sensitivity=True
)

# Exportar
analyzer.export_report_json(report, "report.json")
analyzer.export_report_html(report, "report.html")
```

---

## 📘 API Reference

### SolverManager

```python
class SolverManager:
    def __init__(self, config: Optional[SolverConfig] = None)
    
    def solve(
        item_id: str,
        demand: float,
        required_date: str,
        cte_scores: List[Dict],
        constraints: ConstraintSet
    ) -> SolverResult
    
    def batch_solve(
        items: List[Dict],
        constraints: Optional[ConstraintSet] = None
    ) -> List[SolverResult]
    
    def get_portfolio_summary(
        results: List[SolverResult]
    ) -> Dict[str, Any]
```

### ConstraintBuilder

```python
class ConstraintBuilder:
    def add_demand_constraint(...) -> ConstraintBuilder
    def add_fefo_constraint(...) -> ConstraintBuilder
    def add_capacity_constraint(...) -> ConstraintBuilder
    def add_lead_time_constraint(...) -> ConstraintBuilder
    def add_service_level_constraint(...) -> ConstraintBuilder
    def add_transfer_constraint(...) -> ConstraintBuilder
    def add_one_in_constraint(...) -> ConstraintBuilder
    def add_budget_constraint(...) -> ConstraintBuilder
    def add_sourcing_preference_constraint(...) -> ConstraintBuilder
    
    def build() -> Dict[ConstraintType, List]
    def get_constraint_summary() -> Dict[str, int]
    def validate() -> Tuple[bool, List[str]]
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Solución Greedy Simple

```python
from src.planner.optimization import SolverManager, SolverConfig, SolverStrategy, ConstraintBuilder

# Configurar
config = SolverConfig(strategy=SolverStrategy.GREEDY)
manager = SolverManager(config)

# Restricciones
builder = ConstraintBuilder()
constraints = builder.build()

# CTE scores (del módulo scoring)
cte_scores = [
    {"option_id": "SUP_A", "cte": 50.0, "qty": 1, "max_qty": 100},
    {"option_id": "SUP_B", "cte": 48.0, "qty": 1, "max_qty": 150},
]

# Resolver
result = manager.solve(
    item_id="SKU001",
    demand=100.0,
    required_date="2025-10-30",
    cte_scores=cte_scores,
    constraints=constraints
)

# Resultado
if result.success:
    print(f"Costo total: ${result.objective_value:.2f}")
    for option in result.solution["selected_options"]:
        print(f"  - {option['option_id']}: {option['quantity']} unidades")
```

### Ejemplo 2: Solución con Restricciones Complejas

```python
# Construir restricciones
builder = ConstraintBuilder()
constraints = (builder
    .add_demand_constraint("SKU001", 100, "unidades")
    .add_capacity_constraint("CDMX", 500, current_inventory=50)
    .add_capacity_constraint("GUAD", 300)
    .add_budget_constraint(50000, currency="USD", contingency_pct=5)
    .add_lead_time_constraint("OPT_A", "2025-10-30", lead_time_mean_days=10, lead_time_std_days=2)
    .add_service_level_constraint("SKU001", min_service_level=0.95)
    .build())

constraint_set = ConstraintSet(constraints)

# Resolver
result = manager.solve(
    item_id="SKU001",
    demand=100.0,
    required_date="2025-10-30",
    cte_scores=cte_scores,
    constraints=constraint_set
)

# Analizar
analyzer = ModelAnalyzer()
report = analyzer.generate_report(result, constraint_set)
print(report)
```

### Ejemplo 3: Batch Resolve (Múltiples Ítems)

```python
items = [
    {
        "item_id": "SKU001",
        "demand": 100,
        "required_date": "2025-10-30",
        "cte_scores": [
            {"option_id": "SUP_A", "cte": 50, "qty": 1, "max_qty": 100},
        ]
    },
    {
        "item_id": "SKU002",
        "demand": 50,
        "required_date": "2025-10-31",
        "cte_scores": [
            {"option_id": "SUP_B", "cte": 30, "qty": 1, "max_qty": 75},
        ]
    }
]

results = manager.batch_solve(items, constraints)

# Resumen del portafolio
portfolio_summary = manager.get_portfolio_summary(results)
print(f"Costo total portafolio: ${portfolio_summary['total_cost']:.2f}")
print(f"Tasa viabilidad: {portfolio_summary['feasibility_rate']*100:.1f}%")
```

---

## 🎯 Estrategias de Resolución

### 1. EXACT (Óptimo)

**Cuándo usar:**
- Instancias pequeñas (<50 opciones)
- Cuando se requiere solución óptima garantizada
- Plazo lo permite (hasta 5 minutos)

**Ventajas:**
- Garantiza óptimo global
- Análisis de sensibilidad disponible

**Desventajas:**
- Puede ser lento
- No siempre factible en tiempo real

```python
config = SolverConfig(strategy=SolverStrategy.EXACT, time_limit_seconds=300)
```

### 2. GREEDY (Heurística Rápida)

**Cuándo usar:**
- Instancias grandes (>100 opciones)
- Requiere respuesta en <1 segundo
- Acceptable 5-15% de gap vs óptimo

**Ventajas:**
- Muy rápida (O(n log n))
- Siempre produce solución (si factible)

**Desventajas:**
- No garantiza óptimo
- Puede diverger en casos patológicos

```python
config = SolverConfig(strategy=SolverStrategy.GREEDY)
```

### 3. GREEDY_WITH_REOPT (Balance)

**Cuándo usar:**
- DEFAULT - balance entre calidad y velocidad
- Instancias medianas (20-200 opciones)
- 1-2 segundos de respuesta acceptable

**Ventajas:**
- Balance óptimo calidad/velocidad
- Reoptimización local mejora greedy

**Desventajas:**
- Más lenta que greedy puro
- Aún sub-óptima vs exact

```python
config = SolverConfig(strategy=SolverStrategy.GREEDY_WITH_REOPT)  # DEFAULT
```

---

## 🧪 Tests

### test_optimization.py

```bash
python test_optimization.py
```

**Coverage:**

- ✅ Construcción de restricciones
- ✅ Formulación MIP
- ✅ Solver greedy
- ✅ Solver exact
- ✅ Análisis de soluciones
- ✅ Reportes
- ✅ Batch solve

**Ejemplo test:**

```python
def test_greedy_solver():
    config = SolverConfig(strategy=SolverStrategy.GREEDY)
    manager = SolverManager(config)
    
    cte_scores = [
        {"option_id": "A", "cte": 50, "qty": 1, "max_qty": 100},
        {"option_id": "B", "cte": 40, "qty": 1, "max_qty": 100},
    ]
    
    builder = ConstraintBuilder()
    constraints = builder.build()
    
    result = manager.solve(
        item_id="TEST",
        demand=50,
        required_date="2025-10-30",
        cte_scores=cte_scores,
        constraints=ConstraintSet(constraints)
    )
    
    assert result.success
    assert result.objective_value <= 2500  # 50 * 50
```

---

## 📌 Próximos Pasos

1. **Integrar con scoring**: Usar `CTE.calculate()` del módulo `scoring/`
2. **Agregar más restricciones**: Customizaciones por industria/cliente
3. **Optimizar solver**: Ajustar parameters CBC para mejor performance
4. **Dashboard**: Visualizar soluciones en tiempo real
5. **Event-driven**: Reoptimizar ante cambios de demanda/capacidad

---

**Autores:** Manuel Remón  
**Versión:** 1.0.0  
**Última actualización:** 2025-10-26
