# Árbol de Decisión de Abastecimiento SPM

## Descripción General

El **Árbol de Decisión de Abastecimiento (Decision Tree)** es el componente core del motor de planificación SPM que orquesta 12 vías operativas de abastecimiento. Implementa un flujo binary-tree con gates (puertas de decisión) que evalúan contexto de ejecución para determinar la ruta óptima de adquisición de materiales.

### Objetivo

Proporcionar un framework flexible, auditado y multi-criterio para:
- Navegar 12 vías de abastecimiento (Stock → Compra)
- Evaluar viabilidad de cada vía mediante gates contextuales
- Ejecutar batch de solicitudes con optimización paralela
- Comparar y rankear caminos alternativos
- Exportar trazabilidad E2E de decisiones

---

## Arquitectura de 12 Vías

```
┌─────────────────────────────────────────────────────────────────┐
│                  ÁRBOL DE DECISIÓN SPM (12 NODOS)              │
└─────────────────────────────────────────────────────────────────┘

  Node 1: STOCK_LOCAL
    ↓ success [gates: availability, quality, timing]
  Node 2: STOCK_LOCAL_ASSETS
    ↓ success [gates: availability, asset_validation]
  Node 3: DISASSEMBLY (Desarme)
    ↓ success [gates: bom_availability, cost_effective]
  Node 4: SUBSTITUTES (Sustitutos)
    ↓ success [gates: technical_compat, quality]
  Node 5: RECOVERY (Recupero)
    ↓ success [gates: available_scrap, quality]
  Node 6: TRANSFER (Transferencia Inter-almacén)
    ↓ success [gates: transfer_available, timing]
  Node 7: INTERCOMPANY (Compra Inter-compañía)
    ↓ success [gates: relationship, pricing]
  Node 8: VMI (Vendor-Managed Inventory)
    ↓ success [gates: contract_active, supplier_available]
  Node 9: LOAN (Préstamo)
    ↓ success [gates: partner_available, availability]
  Node 10: EXPEDITE (Acelerar)
    ↓ success [gates: budget_available, supplier_willing]
  Node 11: PURCHASE (Compra Estándar)
    ↓ success [gates: supplier_available, lead_time_ok]
  Node 12: FINAL_RESULT
    └─ Registro del resultado final
```

### Flow Logic

```
Inicio → Node 1
  ├─ Si gates OK: Éxito en Node 1 → TERMINA (reserva local)
  ├─ Si gates FAIL: Siguiente → Node 2
  
Node 2
  ├─ Si gates OK: Éxito en Node 2 → TERMINA (assets reutilizables)
  ├─ Si gates FAIL: Siguiente → Node 3
  
... (continuación hasta Node 11)

Node 11 (Compra Estándar)
  ├─ Si gates OK: Éxito → Node 12 (COMPRA)
  ├─ Si gates FAIL: Node 12 (NO COMPRA - escalada manual)
```

---

## Componentes Core

### 1. `decision_tree.py` (450 líneas)

Define el árbol de decisión y sus estructuras.

#### Enums

**SourceRoute** (12 vías operativas)
```python
class SourceRoute(Enum):
    STOCK_LOCAL = 1              # Reserva de stock local
    STOCK_LOCAL_ASSETS = 2       # Stock local + assets reutilizables
    DISASSEMBLY = 3              # Desarme de componentes
    SUBSTITUTES = 4              # Sustitutos técnicos
    RECOVERY = 5                 # Recupero de scrap
    TRANSFER = 6                 # Transferencia inter-almacén
    INTERCOMPANY = 7             # Compra inter-compañía
    VMI = 8                       # Vendor-Managed Inventory
    LOAN = 9                      # Préstamo/comodato
    EXPEDITE = 10                # Acelerar entrega existente
    PURCHASE = 11                # Compra estándar
    FINAL_RESULT = 12            # Nodo terminal
```

**GateType** (9 tipos de puertas)
```python
class GateType(Enum):
    AVAILABILITY = "availability"      # ¿Hay disponibilidad?
    TIMING = "timing"                  # ¿Lead time suficiente?
    COST = "cost"                      # ¿Costo dentro presupuesto?
    QUALITY = "quality"                # ¿Calidad garantizada?
    RISK = "risk"                      # ¿Riesgo aceptable?
    REGULATORY = "regulatory"          # ¿Cumple normas?
    RELATIONSHIP = "relationship"      # ¿Relación comercial OK?
    FORECAST = "forecast"              # ¿Predictibilidad OK?
    COMPLEX = "complex"                # Lógica compleja custom
```

#### Clases Principales

**Gate**
```python
@dataclass
class Gate:
    gate_id: str                           # ID único
    gate_type: GateType                    # Tipo de puerta
    description: str                       # Descripción
    condition_func: Callable[[ExecutionContext], bool]  # Función evaluadora
    threshold: Optional[float] = None      # Umbral (opcional)
    
    def evaluate(self, context: ExecutionContext) -> bool:
        """Evalúa si la puerta se abre (True) o cierra (False)"""
```

**DecisionNode**
```python
@dataclass
class DecisionNode:
    node_id: str                    # ID único del nodo
    route: SourceRoute              # Vía operativa asociada
    name: str                       # Nombre descriptivo
    description: str                # Descripción
    gates: List[Gate]               # Puertas de decisión
    
    # Métricas estimadas
    estimated_lead_time_days: int
    estimated_cost: float
    estimated_success_rate: float
    
    # Relaciones
    next_on_success: Optional['DecisionNode'] = None
    next_on_failure: Optional['DecisionNode'] = None
    
    def evaluate_gates(self, context) -> Tuple[bool, List[str]]:
        """Evalúa todas las puertas, retorna (todas_abren, ids_fallidas)"""
    
    def set_success_path(self, node: 'DecisionNode') -> 'DecisionNode':
        """Configura nodo siguiente si éxito (fluido)"""
    
    def set_failure_path(self, node: 'DecisionNode') -> 'DecisionNode':
        """Configura nodo siguiente si fallo (fluido)"""
```

**ExecutionPath**
```python
@dataclass
class ExecutionPath:
    path_id: str                              # ID del camino
    item_id: str                              # Ítem
    demand_quantity: float                    # Cantidad demandada
    required_date: datetime                   # Fecha requerida
    
    # Tracking
    visited_nodes: List[str]                  # Nodos visitados
    node_results: Dict[str, Tuple[bool, List[str]]]  # Resultados por nodo
    
    # Resultado
    final_success: bool                       # ¿Éxito?
    final_route: Optional[SourceRoute]        # Vía utilizada
    total_lead_time: int                      # Lead time total
    total_cost: float                         # Costo total
    selected_source: str                      # Fuente seleccionada
    
    def add_node_visit(self, node_id: str, success: bool, failed_gates: List[str]):
        """Registra visita a nodo"""
    
    def set_result(self, success: bool, route: SourceRoute, source: str, lead_time: int, cost: float):
        """Registra resultado final"""
```

**DecisionTreeBuilder**
```python
class DecisionTreeBuilder:
    def create_node(self, node_id: str, route: SourceRoute, name: str, ...) -> DecisionNode:
        """Crea un nodo (fluido)"""
    
    def add_gate_to_node(self, node_id: str, gate_id: str, gate_type: GateType, ...) -> 'DecisionTreeBuilder':
        """Agrega puerta a nodo (fluido)"""
    
    def connect_nodes(self, from_id: str, to_success_id: str, to_failure_id: str) -> 'DecisionTreeBuilder':
        """Conecta nodos (fluido)"""
    
    def build(self) -> DecisionNode:
        """Construye árbol completo"""
    
    def get_node(self, node_id: str) -> Optional[DecisionNode]:
        """Obtiene nodo por ID"""

def create_standard_decision_tree() -> DecisionTreeBuilder:
    """Factory: crea árbol estándar SPM con 12 nodos + gates"""
```

---

### 2. `execution_engine.py` (400 líneas)

Motor de ejecución del árbol.

#### ExecutionContext
```python
@dataclass
class ExecutionContext:
    """Estado de ejecución con datos del sistema"""
    
    # Item & demand
    item_id: str
    demand_quantity: float
    required_date: datetime
    
    # Inventory status
    local_stock_available: float
    local_assets_available: float
    bom_components: Dict[str, float]           # {component_id: available_qty}
    substitutes: List[str]                     # IDs de sustitutos disponibles
    
    # Transfer options
    transfer_centers_available: Dict[str, float]  # {center_id: qty}
    intercompany_available: bool
    vmi_contract_active: bool
    loan_partner_available: bool
    
    # Timing
    days_to_deadline: int
    can_expedite: bool
    expedite_budget_available: float
    
    # Sourcing
    supplier_available: bool
    supplier_lead_time_days: int
    
    # Constraints
    criticality: str                           # "low", "medium", "high", "critical"
    budget_available: float
    max_acceptable_cost: float
    
    def get_gates_evaluation(self) -> Dict[str, Any]:
        """Pre-evalúa contexto para gates"""
```

#### DecisionTreeExecutor
```python
class DecisionTreeExecutor:
    def __init__(self, builder: DecisionTreeBuilder = None):
        """Inicializa con DecisionTreeBuilder (default: árbol estándar)"""
    
    def execute(self, context: ExecutionContext, max_depth: int = 12) -> ExecutionPath:
        """
        Ejecuta árbol: navega desde root hasta nodo terminal
        
        Algoritmo:
        1. Iniciar en nodo raíz
        2. Evaluar gates del nodo actual
        3. Si todos gates OK: marcar éxito, seguir por next_on_success
        4. Si algún gate falla: seguir por next_on_failure
        5. Repetir hasta nodo 12 (FINAL_RESULT) o max_depth
        6. Registrar ExecutionPath con resultado
        
        Returns:
            ExecutionPath con trazabilidad completa
        """
    
    def execute_batch(self, contexts: List[ExecutionContext]) -> List[ExecutionPath]:
        """Ejecuta múltiples contextos (paralelo ready)"""
    
    def get_execution_statistics(self, paths: List[ExecutionPath]) -> Dict[str, Any]:
        """
        Retorna estadísticas de ejecución:
        {
            'total': N,
            'successful': M,
            'failed': N-M,
            'success_rate': M/N,
            'avg_lead_time': X days,
            'avg_cost': $Y,
            'routes_used': {SourceRoute.X: count, ...}
        }
        """
    
    def export_execution_log(self, paths: List[ExecutionPath], file_path: str, format: str = 'json') -> bool:
        """Exporta log de ejecución a JSON o CSV"""
```

---

### 3. `path_evaluator.py` (350 líneas)

Evaluador de viabilidad y ranking de caminos.

#### FeasibilityScore
```python
@dataclass
class FeasibilityScore:
    path_id: str
    
    # Métricas booleanas
    metrics: Dict[FeasibilityMetric, bool]  # {SUCCESS, LEAD_TIME, COST, ...}
    
    # Scores normalizados [0, 1]
    lead_time_score: float      # 1.0 si within deadline, decrece con atraso
    cost_score: float           # 1.0 si within budget, decrece con exceso
    success_score: float        # Tasa éxito de la ruta
    risk_score: float           # 1.0 - risk
    quality_score: float        # Probabilidad calidad OK
    
    # Score composite
    composite_score: float      # Weighted sum
    feasibility_level: str      # "FULL" / "PARTIAL" / "MARGINAL" / "INFEASIBLE"
    
    # Detalle
    failed_metrics: List[str]
    notes: List[str]
    evaluation_timestamp: str
```

#### RouteScoringProfile
```python
@dataclass
class RouteScoringProfile:
    """Perfil de scoring específico por SourceRoute"""
    route: SourceRoute
    
    # Probabilidades base
    base_success_rate: float = 0.8
    cost_volatility: float = 0.1
    lead_time_variability: float = 2.0
    
    # Pesos (normalizados a 1.0)
    weight_success: float = 0.25
    weight_lead_time: float = 0.35
    weight_cost: float = 0.25
    weight_risk: float = 0.15
    
    # Thresholds
    acceptable_cost_premium: float = 0.2      # 20% sobre mínimo
    critical_lead_time_margin: float = 2.0    # ±2 días críticos
    min_quality_acceptable: float = 0.95
    
    # Contextos óptimos
    optimal_for: List[str]  # ["high_criticality", "short_lead_time", ...]
```

#### PathEvaluator
```python
class PathEvaluator:
    def __init__(self):
        """Inicializa con perfiles de 12 rutas estándar"""
    
    def evaluate_path(self, path: ExecutionPath, required_date: datetime, 
                     max_budget: float, criticality: str) -> FeasibilityScore:
        """
        Evalúa viabilidad detallada de un camino
        
        Evaluaciones:
        1. ¿Éxito? (path alcanzó nodo final OK)
        2. ¿Lead time OK? (dentro plazo, score decae con atraso)
        3. ¿Costo OK? (within budget, score decae con exceso)
        4. ¿Criticidad match? (ruta compatible con nivel)
        5. ¿Disponibilidad? (confirmed)
        6. ¿Riesgo? (inverso, penalización por criticidad)
        7. ¿Calidad? (garantizada por ruta)
        
        Returns:
            FeasibilityScore con evaluación multi-criterio
        """
    
    def compare_paths(self, paths: List[ExecutionPath], required_date: datetime,
                     max_budget: float, criticality: str, 
                     weights: Dict[str, float] = None) -> Tuple[ExecutionPath, float, List[FeasibilityScore]]:
        """
        Compara múltiples caminos y selecciona el mejor
        
        Pesos default: {composite: 0.5, lead_time: 0.25, cost: 0.25}
        
        Returns:
            (best_path, best_score, all_scores)
        """
    
    def rank_paths(self, paths: List[ExecutionPath], required_date: datetime,
                  max_budget: float, criticality: str) -> List[Tuple[ExecutionPath, FeasibilityScore, int]]:
        """
        Rankea caminos descendente por viabilidad
        
        Returns:
            [(path1, score1, rank=1), (path2, score2, rank=2), ...]
        """
    
    def export_feasibility_report(self, scores: List[FeasibilityScore], file_path: str, format: str = 'json') -> bool:
        """Exporta reporte de viabilidad"""
```

---

### 4. `gate_manager.py` (300 líneas)

Manager centralizado de gates.

#### GateEvaluation
```python
@dataclass
class GateEvaluation:
    gate_id: str
    gate_type: GateType
    state: GateState  # OPEN, CLOSED, CONDITION_MET, CONDITION_NOT_MET
    
    # Resultado
    condition_result: bool
    threshold_value: Optional[float]
    actual_value: Optional[float]
    
    # Metadata
    evaluation_time_ms: float
    notes: List[str]
    timestamp: str
    evaluator_id: str
```

#### GateConfiguration
```python
@dataclass
class GateConfiguration:
    gate_id: str
    gate_type: GateType
    
    # Control
    enabled: bool = True
    severity: str = "normal"  # "critical", "normal", "warning"
    
    # Reglas
    rule_type: str = "simple"  # "simple", "compound", "statistical"
    custom_condition: Optional[Callable] = None
    parameters: Dict[str, Any] = {}
    
    # Contextos
    applicable_contexts: List[str] = []     # empty = aplicable a todos
    not_applicable_contexts: List[str] = []
    
    # Histórico
    evaluations: List[GateEvaluation] = []
    pass_rate: float = 1.0
```

#### GateManager
```python
class GateManager:
    def __init__(self, max_cache_size: int = 1000):
        """Inicializa manager con caching"""
    
    def register_gate(self, gate: Gate, config: Optional[GateConfiguration] = None) -> None:
        """Registra una puerta"""
    
    def register_global_rule(self, rule_name: str, rule_func: Callable) -> None:
        """Registra regla global aplicable a múltiples gates"""
    
    def evaluate_gate(self, gate_id: str, context: ExecutionContext, 
                     use_cache: bool = True) -> Tuple[bool, GateEvaluation]:
        """
        Evalúa una puerta individual
        
        Features:
        - Caching de evaluaciones
        - Bypass si gate deshabilitado
        - Auditoría completa
        
        Returns:
            (resultado_bool, GateEvaluation)
        """
    
    def evaluate_gates_batch(self, gate_ids: List[str], context: ExecutionContext,
                            stop_on_fail: bool = False) -> Tuple[bool, List[GateEvaluation]]:
        """Evalúa múltiples puertas"""
    
    def evaluate_with_fallback(self, gate_id: str, context: ExecutionContext,
                              fallback_gate_id: Optional[str] = None) -> Tuple[bool, Dict[str, GateEvaluation]]:
        """Evalúa con fallback si primera puerta falla"""
    
    def apply_global_rule(self, rule_name: str, gate_ids: List[str],
                         context: ExecutionContext) -> Tuple[bool, List[GateEvaluation]]:
        """Aplica regla global a múltiples puertas"""
    
    def get_gate_statistics(self, gate_id: str) -> Dict[str, Any]:
        """Retorna estadísticas de una puerta"""
    
    def export_audit_log(self, file_path: str, format: str = 'json') -> bool:
        """Exporta log de auditoría de evaluaciones"""
    
    def clear_cache(self) -> None:
        """Limpia cache"""
```

#### AdvancedGateEvaluator
```python
class AdvancedGateEvaluator:
    def evaluate_with_context_adaptation(self, gate_ids: List[str], 
                                        context: ExecutionContext,
                                        context_type: str) -> Tuple[bool, List[GateEvaluation]]:
        """Evalúa adaptando thresholds según tipo de contexto"""
    
    def evaluate_with_severity_levels(self, gate_configs: Dict[str, GateConfiguration],
                                     context: ExecutionContext) -> Tuple[bool, Dict[str, Any]]:
        """Evalúa considerando niveles de severidad"""
```

---

## API Reference

### Uso Básico: Crear Árbol

```python
from src.planner.decision_tree.decision_tree import create_standard_decision_tree

# Crear árbol estándar SPM
builder = create_standard_decision_tree()
root_node = builder.build()
```

### Uso: Ejecutar Solicitud Individual

```python
from src.planner.decision_tree.execution_engine import DecisionTreeExecutor, ExecutionContext
from datetime import datetime, timedelta

# Crear contexto de ejecución
context = ExecutionContext(
    item_id="MAT001",
    demand_quantity=100.0,
    required_date=datetime.now() + timedelta(days=5),
    local_stock_available=50.0,
    local_assets_available=20.0,
    bom_components={"COMP1": 30, "COMP2": 25},
    substitutes=["MAT002", "MAT003"],
    transfer_centers_available={"CENTER1": 40},
    intercompany_available=True,
    vmi_contract_active=True,
    loan_partner_available=True,
    days_to_deadline=5,
    can_expedite=True,
    expedite_budget_available=500.0,
    supplier_available=True,
    supplier_lead_time_days=7,
    criticality="high",
    budget_available=2000.0,
    max_acceptable_cost=1800.0
)

# Ejecutar
executor = DecisionTreeExecutor()
path = executor.execute(context)

# Resultado
print(f"Éxito: {path.final_success}")
print(f"Vía: {path.final_route.name}")
print(f"Lead time: {path.total_lead_time} días")
print(f"Costo: ${path.total_cost}")
print(f"Nodos visitados: {path.visited_nodes}")
```

### Uso: Batch de Solicitudes

```python
# Ejecutar múltiples contextos
contexts = [context1, context2, context3, ...]
paths = executor.execute_batch(contexts)

# Estadísticas
stats = executor.get_execution_statistics(paths)
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Avg lead time: {stats['avg_lead_time']} days")
print(f"Routes used: {stats['routes_used']}")

# Exportar log
executor.export_execution_log(paths, "execution_log.json", format="json")
```

### Uso: Comparar Caminos

```python
from src.planner.decision_tree.path_evaluator import PathEvaluator

# Evaluar viabilidad
evaluator = PathEvaluator()
scores = [
    evaluator.evaluate_path(path, required_date, max_budget, "high")
    for path in paths
]

# Rankear
ranked = evaluator.rank_paths(paths, required_date, max_budget, "high")
for path, score, rank in ranked:
    print(f"Rank {rank}: {path.final_route.name} - score={score.composite_score:.2f}")

# Encontrar mejor
best_path, best_score, all_scores = evaluator.compare_paths(
    paths, required_date, max_budget, "high",
    weights={"composite": 0.5, "lead_time": 0.25, "cost": 0.25}
)
```

### Uso: Gate Manager

```python
from src.planner.decision_tree.gate_manager import GateManager, GateConfiguration

# Crear manager
manager = GateManager()

# Registrar gates desde árbol
for node_id, node in builder.get_all_nodes().items():
    for gate in node.gates:
        manager.register_gate(gate)

# Evaluar
result, evaluation = manager.evaluate_gate("gate_001", context)

# Batch
all_pass, evaluations = manager.evaluate_gates_batch(
    ["gate_001", "gate_002", "gate_003"],
    context,
    stop_on_fail=False
)

# Estadísticas
stats = manager.get_all_statistics()
for s in stats:
    print(f"{s['gate_id']}: {s['pass_rate']:.1%} pass rate")

# Auditoría
manager.export_audit_log("gate_audit.json", format="json")
```

---

## Integración con Módulos Anteriores

### → Scoring (Todo #3)

ExecutionContext utiliza probabilidades y estimaciones calculadas por **src/planner/scoring/**:
- `lead_time_score`: Basada en distribuciones probabilísticas
- `success_score`: Tasa éxito por ruta
- `cost_score`: Costo estimado por vía

### → Optimization (Todo #4)

ExecutionPath integra resultados de **src/planner/optimization/**:
- Reserva local: validada por `ReservationOptimizer`
- Compra: respeta restricciones MIP/ILP
- Transfer: optimiza TDABC

---

## Tests & Validación

Véase `test_decision_tree.py` para:
- Tests de creación de nodos
- Tests de evaluación de gates
- Tests de ejecución de árbol
- Tests de batch execution
- Tests de path evaluation
- Tests de gate manager
- Integration tests

---

## Diagramas

### Flujo de Decisión (Nodo Típico)

```
┌──────────────────────┐
│  Node N (Vía N)      │
│  - Gates: [A, B, C]  │
└──────────┬───────────┘
           │
      ┌────┴─────┐
      │ Evaluar  │
      │ gates    │
      └────┬─────┘
           │
        ┌──┴──┐
   PASS │     │ FAIL
        │     │
    ┌───▼──┐ ┌──▼────┐
    │ Node │ │ Node  │
    │ +1   │ │ -1    │
    └──────┘ └───────┘
```

### Scoring Multi-Criterio

```
FeasibilityScore
├─ success_score: 0.85
├─ lead_time_score: 0.90
├─ cost_score: 0.75
├─ risk_score: 0.80
└─ composite_score: weights-based ← selector
```

---

## FAQ

**P: ¿Qué pasa si múltiples nodos tienen éxito?**
R: Se elige el primero en orden (Node 1 > Node 2 > ...). Customizable en DecisionTreeBuilder.

**P: ¿Cómo se calculan los scores?**
R: Cada SourceRoute tiene RouteScoringProfile con pesos + fórmulas específicas.

**P: ¿Se puede agregar una ruta nueva?**
R: Sí, extender SourceRoute enum + agregar perfil en PathEvaluator + crear nodos en builder.

**P: ¿Es determinístico?**
R: Sí, dado el mismo ExecutionContext retorna siempre el mismo path.

**P: ¿Soporta escalabilidad?**
R: Sí, execute_batch() está preparado para paralelización. GateManager soporta caching.

---

## Próximos Pasos (Todos #6-8)

1. **Todo #6**: Algoritmos por vía (knapsack, grafo, TDABC, Johnson)
2. **Todo #7**: Event-driven + rolling horizon
3. **Todo #8**: Auditoría + gobernanza

