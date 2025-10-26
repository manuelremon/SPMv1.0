"""
Motor base de scoring probabilístico
Calcula CTE (Costo + Atraso + Riesgo) para opciones de abastecimiento
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import math
from scipy import stats
from pydantic import BaseModel, Field, validator


class ScoringDimension(str, Enum):
    """Dimensiones de scoring"""
    COST = "COST"
    TIME = "TIME"
    RISK = "RISK"
    QUALITY = "QUALITY"
    AVAILABILITY = "AVAILABILITY"
    INTEGRATED = "INTEGRATED"


@dataclass
class CostBreakdown:
    """Desglose de costos por opción"""
    unit_cost: float
    transportation_cost: float = 0.0
    customs_duty: float = 0.0
    handling_cost: float = 0.0
    
    @property
    def total_cost_per_unit(self) -> float:
        """Costo total por unidad"""
        return self.unit_cost + self.transportation_cost + self.customs_duty + self.handling_cost
    
    @property
    def total_cost_ratio(self) -> float:
        """Ratio: (unit + transport + customs) / total"""
        return (self.unit_cost + self.transportation_cost + self.customs_duty) / max(self.total_cost_per_unit, 0.01)


@dataclass
class TimeRiskAssessment:
    """Evaluación de riesgo temporal"""
    lead_time_mean: float  # días
    lead_time_std: float   # días
    lead_time_p95: Optional[float] = None  # percentil 95
    on_time_percentage: float = 0.95
    
    def calculate_probability_on_time(self, required_date: datetime, order_date: datetime) -> float:
        """
        Calcular P(entrega <= required_date) usando distribución normal
        
        Args:
            required_date: Fecha requerida
            order_date: Fecha de orden
        
        Returns:
            Probabilidad (0-1)
        """
        available_days = (required_date - order_date).days
        z_score = (available_days - self.lead_time_mean) / max(self.lead_time_std, 0.1)
        return stats.norm.cdf(z_score)  # CDF de normal estándar
    
    def calculate_service_level_lead_time(self, sl_target: float = 0.95) -> float:
        """
        Calcular lead time requerido para alcanzar SL objetivo
        
        Args:
            sl_target: Target de service level (ej: 0.95 para 95%)
        
        Returns:
            Lead time días para cumplir SL
        """
        z_score = stats.norm.ppf(sl_target)  # Inverso de CDF
        return self.lead_time_mean + z_score * max(self.lead_time_std, 0.1)
    
    @property
    def lead_time_variability_index(self) -> float:
        """Índice de variabilidad: std / mean (0-1 normalizado)"""
        if self.lead_time_mean <= 0:
            return 0.0
        return min(self.lead_time_std / self.lead_time_mean, 1.0)
    
    @property
    def delivery_reliability_score(self) -> float:
        """Score 0-1 de confiabilidad: on_time_pct × (1 - variability)"""
        return self.on_time_percentage * (1 - self.lead_time_variability_index)


@dataclass
class QualityRiskAssessment:
    """Evaluación de riesgo de calidad"""
    quality_acceptance_rate: float  # 0-1
    availability_percentage: float = 0.95  # 0-1
    reliability_score: Optional[float] = None  # proveedores histórico
    
    @property
    def quality_risk(self) -> float:
        """Riesgo de rechazo: 1 - acceptance_rate"""
        return 1 - self.quality_acceptance_rate
    
    @property
    def integrated_reliability(self) -> float:
        """Confiabilidad integrada: acceptance × availability × reliability"""
        factors = [self.quality_acceptance_rate, self.availability_percentage]
        if self.reliability_score is not None:
            factors.append(self.reliability_score)
        return math.prod(factors)


@dataclass
class NormalizedScore:
    """Score normalizado (0-1) para una dimensión"""
    dimension: ScoringDimension
    value: float  # 0-1
    raw_value: float  # valor original sin normalizar
    percentile: float = 0.0  # percentil relativo (0-100)
    confidence: float = 1.0  # confianza de la medida
    
    @property
    def is_excellent(self) -> bool:
        return self.value >= 0.8
    
    @property
    def is_good(self) -> bool:
        return 0.6 <= self.value < 0.8
    
    @property
    def is_acceptable(self) -> bool:
        return 0.4 <= self.value < 0.6
    
    @property
    def is_poor(self) -> bool:
        return self.value < 0.4


@dataclass
class CTEScore:
    """CTE Score para una opción (Costo + Tiempo + Riesgo)"""
    option_id: str
    item_id: str
    
    # Componentes del CTE
    cost_score: NormalizedScore
    time_score: NormalizedScore  # P(on-time)
    risk_score: NormalizedScore  # integrated reliability
    
    # CTE integrado (weighted average)
    cte_value: float  # 0-1, donde 1 es óptimo
    
    # Pesos utilizados
    weight_cost: float = 0.4
    weight_time: float = 0.3
    weight_risk: float = 0.3
    
    # Metadata
    sourcing_path: str = ""
    supplier_id: Optional[str] = None
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validar que pesos sumen 1"""
        total_weight = self.weight_cost + self.weight_time + self.weight_risk
        assert abs(total_weight - 1.0) < 0.01, f"Pesos deben sumar 1.0, suman {total_weight}"
    
    @property
    def weighted_cost_component(self) -> float:
        return self.cost_score.value * self.weight_cost
    
    @property
    def weighted_time_component(self) -> float:
        return self.time_score.value * self.weight_time
    
    @property
    def weighted_risk_component(self) -> float:
        return self.risk_score.value * self.weight_risk
    
    def get_component_breakdown(self) -> Dict[str, float]:
        """Desglose de componentes del CTE"""
        return {
            "cost": self.weighted_cost_component,
            "time": self.weighted_time_component,
            "risk": self.weighted_risk_component,
            "total_cte": self.cte_value,
        }
    
    def get_analysis_summary(self) -> str:
        """Análisis textual del CTE"""
        lines = [
            f"Option: {self.option_id}",
            f"CTE Score: {self.cte_value:.3f}",
            f"  └─ Cost: {self.weighted_cost_component:.3f} ({self.cost_score.value:.3f}) - {self.cost_score.raw_value:.2f}",
            f"  └─ Time: {self.weighted_time_component:.3f} ({self.time_score.value:.3f}) - P(on-time)={self.time_score.raw_value:.1%}",
            f"  └─ Risk: {self.weighted_risk_component:.3f} ({self.risk_score.value:.3f}) - Reliability={self.risk_score.raw_value:.1%}",
        ]
        return "\n".join(lines)


@dataclass
class ScoringContext:
    """Contexto para scoring: información de requisiuciones y ítems"""
    required_date: datetime
    order_date: datetime
    item_criticality: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    item_abc: str = "B"  # A, B, C
    demand_quantity: float = 1.0
    
    # Umbrales y parámetros
    target_service_level: float = 0.95
    cost_penalty_multiplier: float = 1.0  # Castigo a atraso
    risk_penalty_multiplier: float = 1.0
    
    @property
    def days_to_deadline(self) -> float:
        return (self.required_date - self.order_date).days
    
    @property
    def is_urgent(self) -> bool:
        return self.days_to_deadline <= 5
    
    @property
    def is_critical(self) -> bool:
        return self.item_criticality in ["CRITICAL", "HIGH"]


class BaseScorer:
    """Calculador base de scores CTE"""
    
    def __init__(self):
        self.scored_options: List[CTEScore] = []
        self.min_cost: float = float('inf')
        self.max_cost: float = 0.0
    
    def normalize_cost(self, cost: float, context: Optional[ScoringContext] = None) -> float:
        """
        Normalizar costo a escala 0-1 (invertida: menor costo = mayor score)
        
        Args:
            cost: Costo por unidad
            context: Contexto de scoring
        
        Returns:
            Score normalizado 0-1
        """
        if self.max_cost <= self.min_cost:
            return 0.5
        
        # Normalizar en rango [min, max]
        normalized = 1 - (cost - self.min_cost) / (self.max_cost - self.min_cost)
        
        # Aplicar castigo si hay contexto con urgencia
        if context and context.is_urgent and context.cost_penalty_multiplier > 1.0:
            normalized *= (1 / context.cost_penalty_multiplier)
        
        return max(0.0, min(normalized, 1.0))
    
    def calculate_time_score(
        self,
        time_risk: TimeRiskAssessment,
        context: ScoringContext
    ) -> float:
        """
        Calcular score temporal basado en P(on-time)
        
        Args:
            time_risk: Evaluación de riesgo temporal
            context: Contexto de scoring
        
        Returns:
            Score 0-1
        """
        prob_on_time = time_risk.calculate_probability_on_time(
            context.required_date,
            context.order_date
        )
        
        # Ajustar por urgencia
        if context.is_urgent:
            # Para urgencias, penalizar más
            return prob_on_time ** 1.5
        
        return prob_on_time
    
    def calculate_risk_score(
        self,
        quality_risk: QualityRiskAssessment
    ) -> float:
        """
        Calcular score de riesgo integrado
        
        Returns:
            Score 0-1 (mayor = menor riesgo)
        """
        return quality_risk.integrated_reliability
    
    def calculate_cte(
        self,
        option_id: str,
        item_id: str,
        cost_breakdown: CostBreakdown,
        time_risk: TimeRiskAssessment,
        quality_risk: QualityRiskAssessment,
        context: ScoringContext,
        sourcing_path: str = "PURCHASE",
        supplier_id: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> CTEScore:
        """
        Calcular CTE (Costo + Tiempo + Riesgo) para una opción
        
        Args:
            option_id: ID único de opción
            item_id: ID del ítem
            cost_breakdown: Desglose de costos
            time_risk: Evaluación temporal
            quality_risk: Evaluación de calidad
            context: Contexto de scoring
            sourcing_path: Tipo de ruta (STOCK_LOCAL, PURCHASE, etc.)
            supplier_id: ID del proveedor
            weights: Pesos personalizados {cost, time, risk}
        
        Returns:
            CTEScore con componentes
        """
        # Actualizar rangos de costo
        total_cost = cost_breakdown.total_cost_per_unit
        self.min_cost = min(self.min_cost, total_cost)
        self.max_cost = max(self.max_cost, total_cost)
        
        # Calcular componentes normalizados
        cost_score = NormalizedScore(
            dimension=ScoringDimension.COST,
            value=self.normalize_cost(total_cost, context),
            raw_value=total_cost,
        )
        
        time_score = NormalizedScore(
            dimension=ScoringDimension.TIME,
            value=self.calculate_time_score(time_risk, context),
            raw_value=time_risk.calculate_probability_on_time(
                context.required_date,
                context.order_date
            ),
        )
        
        risk_score = NormalizedScore(
            dimension=ScoringDimension.RISK,
            value=self.calculate_risk_score(quality_risk),
            raw_value=quality_risk.integrated_reliability,
        )
        
        # Aplicar pesos
        default_weights = {
            "cost": 0.4,
            "time": 0.3,
            "risk": 0.3,
        }
        if weights:
            default_weights.update(weights)
        
        # Calcular CTE integrado
        cte_value = (
            cost_score.value * default_weights["cost"] +
            time_score.value * default_weights["time"] +
            risk_score.value * default_weights["risk"]
        )
        
        # Crear score completo
        cte = CTEScore(
            option_id=option_id,
            item_id=item_id,
            cost_score=cost_score,
            time_score=time_score,
            risk_score=risk_score,
            cte_value=cte_value,
            weight_cost=default_weights["cost"],
            weight_time=default_weights["time"],
            weight_risk=default_weights["risk"],
            sourcing_path=sourcing_path,
            supplier_id=supplier_id,
        )
        
        self.scored_options.append(cte)
        return cte
    
    def get_top_options(self, limit: int = 5) -> List[CTEScore]:
        """Obtener top N opciones ordenadas por CTE"""
        return sorted(
            self.scored_options,
            key=lambda x: x.cte_value,
            reverse=True
        )[:limit]
    
    def get_scoring_report(self) -> str:
        """Generar reporte de scoring"""
        if not self.scored_options:
            return "No options scored yet"
        
        top_options = self.get_top_options(10)
        lines = [
            f"Scoring Report - {len(self.scored_options)} opciones evaluadas",
            f"Top 10 opciones:\n",
        ]
        
        for i, cte in enumerate(top_options, 1):
            lines.append(f"{i}. {cte.get_analysis_summary()}\n")
        
        return "\n".join(lines)
