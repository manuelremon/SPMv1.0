# Motor de Scoring Probabilístico (Todo #3)

## 📋 Descripción

Motor de scoring que calcula **CTE (Costo + Tiempo + Riesgo)** para cada opción de abastecimiento. Integra:

1. **BaseScorer**: Calculador de componentes CTE
2. **CriticalityAwareScorer**: Scorer con reglas adaptadas por criticidad del ítem
3. **FeatureExtractor**: Extractor de características para ML

---

## 🎯 Características Principales

### 1. **BaseScorer**

#### Componentes de Scoring:

**CostBreakdown**
- `unit_cost`: Costo unitario
- `transportation_cost`: Transporte
- `customs_duty`: Aranceles
- `handling_cost`: Manejo
- Property: `total_cost_per_unit`

**TimeRiskAssessment**
- `lead_time_mean`: LT promedio (días)
- `lead_time_std`: Desviación estándar
- `on_time_percentage`: % histórico on-time
- Methods:
  - `calculate_probability_on_time(required_date, order_date)`: P(entrega <= required_date) usando distribución normal
  - `calculate_service_level_lead_time(sl_target=0.95)`: LT requerido para SL objetivo
  - Property: `delivery_reliability_score` = on_time × (1 - variability)

**QualityRiskAssessment**
- `quality_acceptance_rate`: % aceptación QC
- `availability_percentage`: Disponibilidad proveedor
- `reliability_score`: Confiabilidad histórica (opcional)
- Property: `integrated_reliability` = quality × availability × reliability

**ScoringContext**
- `required_date`: Fecha requerida
- `order_date`: Fecha de orden
- `item_criticality`: CRITICAL | HIGH | MEDIUM | LOW
- `item_abc`: A | B | C
- `target_service_level`: SL objetivo (default 0.95)
- Methods:
  - `is_urgent`: True si `days_to_deadline <= 5`
  - `is_critical`: True si criticidad es CRITICAL o HIGH

**NormalizedScore**
- `dimension`: COST | TIME | RISK | QUALITY | AVAILABILITY
- `value`: Score 0-1
- `raw_value`: Valor original sin normalizar
- `percentile`: Percentil relativo
- `confidence`: Confianza de medida

**CTEScore** (Output principal)
- `option_id`: ID único
- `cost_score`: NormalizedScore del costo
- `time_score`: NormalizedScore temporal (P on-time)
- `risk_score`: NormalizedScore de riesgo (integrated reliability)
- `cte_value`: CTE integrado (0-1, donde 1 es óptimo)
- `weight_cost`, `weight_time`, `weight_risk`: Pesos (default 0.4, 0.3, 0.3)
- Methods:
  - `get_component_breakdown()`: Dict con componentes ponderados
  - `get_analysis_summary()`: Texto de análisis

#### Métodos principales:

```python
cte = scorer.calculate_cte(
    option_id="OPT-001",
    item_id="MAT-001",
    cost_breakdown=cost,
    time_risk=time_risk,
    quality_risk=quality,
    context=context,
    weights={'cost': 0.4, 'time': 0.3, 'risk': 0.3}
)

top_options = scorer.get_top_options(limit=5)
report = scorer.get_scoring_report()
```

---

### 2. **CriticalityAwareScorer**

Adapta reglas de scoring según **criticidad del ítem**.

#### Reglas predefinidas (DEFAULT_RULES):

| Criticidad | weight_cost | weight_time | weight_risk | min_SL | max_risk | cost_multiplier |
|-----------|------------|------------|-----------|--------|----------|-----------------|
| CRITICAL | 0.2 | 0.5 | 0.3 | 0.99 | 0.01 | 2.0 |
| HIGH | 0.3 | 0.4 | 0.3 | 0.95 | 0.05 | 1.5 |
| MEDIUM | 0.4 | 0.3 | 0.3 | 0.85 | 0.15 | 1.2 |
| LOW | 0.6 | 0.2 | 0.2 | 0.70 | 0.30 | 1.0 |

#### Reglas de corte (Cuts):

1. **Time Cut**: Si `P(on-time) < min_acceptable_SL` → Rechaza
2. **Risk Cut**: Si `risk > max_acceptable_risk` → Rechaza
3. **Cost Cut**: Si `cost > reference × multiplier` → Rechaza

#### ScoringCutResult:

```python
@dataclass
class ScoringCutResult:
    option_id: str
    accepted: bool
    reason: str
    rejected_by: Optional[str]  # TIME, RISK, COST
    score: Optional[CTEScore]
```

#### Métodos:

```python
crit_scorer = CriticalityAwareScorer()
crit_scorer.set_reference_cost("MAT-001", 50.0)

accepted_ctes, cut_results = crit_scorer.score_and_cut(
    options_data=[
        {
            'option_id': 'OPT-001',
            'item_id': 'MAT-001',
            'cost': 50.0,
            'transport': 10.0,
            'lead_time_mean': 5,
            'lead_time_std': 2,
            'on_time_pct': 0.95,
            'quality_rate': 0.99,
            'availability': 0.95,
            ...
        },
        ...
    ],
    context=context
)

feasible = crit_scorer.get_feasible_set()
rejected = crit_scorer.get_rejected_set()
report = crit_scorer.get_cut_report()
```

---

### 3. **FeatureExtractor**

Extrae características técnicas, económicas y de riesgo para **machine learning**.

#### Categorías de Features:

| Categoría | Features |
|-----------|----------|
| **ECONOMIC** | total_cost, logistics_ratio |
| **TEMPORAL** | lead_time_mean, variability, on_time% |
| **RELIABILITY** | quality_rate, availability, integrated |
| **OPERATIONAL** | urgency_flag, criticality_score, demand, abc_value |
| **CONTEXTUAL** | feature_vector_dimension |

#### Ejemplo de extracción:

```python
extractor = FeatureExtractor()

fv = extractor.extract_features(
    option_id="OPT-001",
    item_id="MAT-001",
    cost_data={'unit': 50.0, 'transportation': 10.0, 'customs': 5.0, 'handling': 2.0},
    time_data={'mean': 5, 'std': 2, 'on_time_pct': 0.95},
    reliability_data={'quality': 0.99, 'availability': 0.95, 'reliability': 0.92},
    context_data={'days_to_deadline': 10, 'criticality': 'HIGH', 'abc_class': 'A'}
)

# FeatureVector
fv.features  # List[Feature]
fv.get_feature_by_name("total_cost_per_unit")
fv.get_by_category(FeatureCategory.ECONOMIC)
fv.to_ml_vector()  # (names: List[str], values: List[float])

# Estadísticas
stats = extractor.calculate_statistics("total_cost_per_unit")
stats.mean, stats.std_dev, stats.percentile_95
stats.coefficient_variation  # CV = std / mean
```

---

## 🔧 Métodos Base

### BaseScorer

```python
scorer = BaseScorer()

# Calcular CTE
cte = scorer.calculate_cte(
    option_id: str,
    item_id: str,
    cost_breakdown: CostBreakdown,
    time_risk: TimeRiskAssessment,
    quality_risk: QualityRiskAssessment,
    context: ScoringContext,
    sourcing_path: str = "PURCHASE",
    supplier_id: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None,
) -> CTEScore

# Top opciones ordenadas por CTE
top = scorer.get_top_options(limit=5)

# Reporte
report = scorer.get_scoring_report()
```

### CriticalityAwareScorer

```python
crit_scorer = CriticalityAwareScorer(custom_rules=None)

# Establecer costo de referencia
crit_scorer.set_reference_cost(item_id, cost)

# Obtener reglas para criticidad
rules = crit_scorer.get_rules_for_criticality("HIGH")

# Aplicar cut a un CTE
cut_result = crit_scorer.apply_criticality_cut(cte, context)

# Scoring y cut completo
accepted, cuts = crit_scorer.score_and_cut(options_data, context)

# Conjuntos
feasible = crit_scorer.get_feasible_set()
rejected = crit_scorer.get_rejected_set()

# Reporte
report = crit_scorer.get_cut_report()
```

### FeatureExtractor

```python
extractor = FeatureExtractor()

# Extraer features
fv = extractor.extract_features(
    option_id, item_id, cost_data, time_data, reliability_data, context_data
) -> FeatureVector

# Estadísticas
stats = extractor.calculate_statistics("feature_name") -> Optional[FeatureStatistics]

# Normalizar feature
normalized = extractor.normalize_feature(feature, stats=None) -> float

# Reporte
report = extractor.generate_feature_report()
```

---

## 📊 Flujo de Uso

```
1. Crear ScoringContext (requerido, orden, criticidad, etc.)
2. Para cada opción de abastecimiento:
   a) Crear CostBreakdown, TimeRiskAssessment, QualityRiskAssessment
   b) BaseScorer.calculate_cte() → CTEScore
3. CriticalityAwareScorer.apply_criticality_cut() a cada CTE
4. Obtener conjunto factible (accepted)
5. FeatureExtractor.extract_features() para ML (opcional)
```

---

## 📈 Ejemplo Completo

```python
from src.planner.scoring import *
from datetime import datetime, timedelta, timezone

# Context
context = ScoringContext(
    required_date=datetime.now(timezone.utc) + timedelta(days=10),
    order_date=datetime.now(timezone.utc),
    item_criticality="HIGH",
    item_abc="A",
    target_service_level=0.95
)

# Opción 1: Compra local rápida
cost1 = CostBreakdown(unit_cost=50, transportation=5)
time1 = TimeRiskAssessment(lead_time_mean=3, lead_time_std=1, on_time_percentage=0.95)
quality1 = QualityRiskAssessment(quality_acceptance_rate=0.99, availability_percentage=0.95)

cte1 = scorer.calculate_cte(
    option_id="OPT-LOCAL",
    item_id="MAT-001",
    cost_breakdown=cost1,
    time_risk=time1,
    quality_risk=quality1,
    context=context
)

# Opción 2: Compra importada barata
cost2 = CostBreakdown(unit_cost=40, transportation=15, customs=5)
time2 = TimeRiskAssessment(lead_time_mean=20, lead_time_std=5, on_time_percentage=0.80)
quality2 = QualityRiskAssessment(quality_acceptance_rate=0.95, availability_percentage=0.90)

cte2 = scorer.calculate_cte(...)

# Aplicar cortes por criticidad
crit_scorer = CriticalityAwareScorer()
cut1 = crit_scorer.apply_criticality_cut(cte1, context)
cut2 = crit_scorer.apply_criticality_cut(cte2, context)

# Seleccionar mejor opción factible
if cut1.accepted:
    print(f"Usar OPT-LOCAL: CTE={cte1.cte_value:.3f}")
elif cut2.accepted:
    print(f"Usar OPT-IMPORT: CTE={cte2.cte_value:.3f}")
```

---

## 🧪 Tests

Ver `test_scoring.py` para tests completos de:
- BaseScorer
- CriticalityAwareScorer
- FeatureExtractor

Tests validan:
- Cálculo de probabilidades normales
- Aplicación de reglas por criticidad
- Extracción y estadísticas de features
- Reportes

---

## 📦 Dependencias

- `scipy.stats`: Distribuciones normales (CDF, percentiles)
- `dataclasses`: Para estructuras de datos
- `enum`: Para enumeraciones
- `pydantic`: Para validación (BaseModel)

---

## 🚀 Próximos Pasos (Todos #4-8)

1. **Todo #4**: MIP/ILP de portafolio (usar PuLP)
2. **Todo #5**: Árbol de decisión con gates
3. **Todo #6**: Algoritmos especializados por vía
4. **Todo #7**: Event-driven con topics y reoptimización
5. **Todo #8**: Auditoría E2E y gobernanza
