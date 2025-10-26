"""
Scorer especializado con reglas de criticidad
Adapta scoring según criticidad del ítem y contexto
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from .base_scorer import (
    BaseScorer, CTEScore, CostBreakdown, TimeRiskAssessment,
    QualityRiskAssessment, ScoringContext, NormalizedScore, ScoringDimension
)


class CriticalityLevel(str, Enum):
    """Niveles de criticidad"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ScoringRuleSet:
    """Conjunto de reglas de scoring por criticidad"""
    criticality: CriticalityLevel
    weight_cost: float
    weight_time: float
    weight_risk: float
    min_acceptable_service_level: float  # 0-1
    max_acceptable_risk: float  # 0-1
    allow_single_source: bool = False
    cost_threshold_multiplier: float = 1.0  # Castigo si costo > ref × multiplicador


# Reglas predefinidas por criticidad
DEFAULT_RULES: Dict[CriticalityLevel, ScoringRuleSet] = {
    CriticalityLevel.CRITICAL: ScoringRuleSet(
        criticality=CriticalityLevel.CRITICAL,
        weight_cost=0.2,  # Costo menos importante
        weight_time=0.5,  # Tiempo MUY importante
        weight_risk=0.3,  # Riesgo importante
        min_acceptable_service_level=0.99,  # SL muy exigente
        max_acceptable_risk=0.01,  # Muy bajo riesgo tolerado
        allow_single_source=False,
        cost_threshold_multiplier=2.0  # Tolera 2x costo si es necesario
    ),
    CriticalityLevel.HIGH: ScoringRuleSet(
        criticality=CriticalityLevel.HIGH,
        weight_cost=0.3,
        weight_time=0.4,
        weight_risk=0.3,
        min_acceptable_service_level=0.95,
        max_acceptable_risk=0.05,
        allow_single_source=True,
        cost_threshold_multiplier=1.5
    ),
    CriticalityLevel.MEDIUM: ScoringRuleSet(
        criticality=CriticalityLevel.MEDIUM,
        weight_cost=0.4,
        weight_time=0.3,
        weight_risk=0.3,
        min_acceptable_service_level=0.85,
        max_acceptable_risk=0.15,
        allow_single_source=True,
        cost_threshold_multiplier=1.2
    ),
    CriticalityLevel.LOW: ScoringRuleSet(
        criticality=CriticalityLevel.LOW,
        weight_cost=0.6,  # Costo muy importante
        weight_time=0.2,
        weight_risk=0.2,
        min_acceptable_service_level=0.70,
        max_acceptable_risk=0.30,
        allow_single_source=True,
        cost_threshold_multiplier=1.0
    ),
}


@dataclass
class ScoringCutResult:
    """Resultado del cut (aceptado o rechazado)"""
    option_id: str
    accepted: bool
    reason: str = ""
    rejected_by: Optional[str] = None  # Dimensión que causó rechazo
    score: Optional[CTEScore] = None


class CriticalityAwareScorer(BaseScorer):
    """Scorer que adapta reglas según criticidad del ítem"""
    
    def __init__(self, custom_rules: Optional[Dict[CriticalityLevel, ScoringRuleSet]] = None):
        super().__init__()
        self.rules = custom_rules or DEFAULT_RULES
        self.cut_results: List[ScoringCutResult] = []
        self.reference_costs: Dict[str, float] = {}  # cost reference por ítem
    
    def set_reference_cost(self, item_id: str, cost: float):
        """Establecer costo de referencia para comparaciones"""
        self.reference_costs[item_id] = cost
    
    def get_rules_for_criticality(self, criticality: str) -> ScoringRuleSet:
        """Obtener reglas para un nivel de criticidad"""
        level = CriticalityLevel[criticality.upper()] if criticality.upper() in CriticalityLevel.__members__ else CriticalityLevel.MEDIUM
        return self.rules.get(level, self.rules[CriticalityLevel.MEDIUM])
    
    def apply_criticality_cut(
        self,
        cte: CTEScore,
        context: ScoringContext,
    ) -> ScoringCutResult:
        """
        Aplicar reglas de corte según criticidad
        
        Args:
            cte: Score calculado
            context: Contexto de scoring
        
        Returns:
            ScoringCutResult con aceptación/rechazo
        """
        rules = self.get_rules_for_criticality(context.item_criticality)
        
        # Cut 1: Service level mínimo
        if cte.time_score.raw_value < rules.min_acceptable_service_level:
            result = ScoringCutResult(
                option_id=cte.option_id,
                accepted=False,
                reason=f"Time/SL insuficiente: {cte.time_score.raw_value:.1%} < {rules.min_acceptable_service_level:.1%}",
                rejected_by="TIME",
                score=cte
            )
            self.cut_results.append(result)
            return result
        
        # Cut 2: Riesgo máximo
        if cte.risk_score.raw_value < (1 - rules.max_acceptable_risk):
            result = ScoringCutResult(
                option_id=cte.option_id,
                accepted=False,
                reason=f"Riesgo demasiado alto: {1 - cte.risk_score.raw_value:.1%} > {rules.max_acceptable_risk:.1%}",
                rejected_by="RISK",
                score=cte
            )
            self.cut_results.append(result)
            return result
        
        # Cut 3: Costo excesivo
        if cte.item_id in self.reference_costs:
            ref_cost = self.reference_costs[cte.item_id]
            max_allowed_cost = ref_cost * rules.cost_threshold_multiplier
            actual_cost = cte.cost_score.raw_value
            
            if actual_cost > max_allowed_cost:
                result = ScoringCutResult(
                    option_id=cte.option_id,
                    accepted=False,
                    reason=f"Costo excesivo: ${actual_cost:.2f} > ${max_allowed_cost:.2f}",
                    rejected_by="COST",
                    score=cte
                )
                self.cut_results.append(result)
                return result
        
        # Todas las pruebas pasaron
        result = ScoringCutResult(
            option_id=cte.option_id,
            accepted=True,
            reason=f"Aceptado (CTE={cte.cte_value:.3f})",
            score=cte
        )
        self.cut_results.append(result)
        return result
    
    def score_and_cut(
        self,
        options_data: List[Dict[str, Any]],
        context: ScoringContext,
    ) -> tuple[List[CTEScore], List[ScoringCutResult]]:
        """
        Scorer completo: calcular CTE + aplicar reglas de corte
        
        Args:
            options_data: Lista de opciones con datos de costo/tiempo/riesgo
            context: Contexto de scoring
        
        Returns:
            (opciones_aceptadas, resultados_cut)
        
        Format de cada opción en options_data:
            {
                'option_id': str,
                'item_id': str,
                'cost': float,
                'transport': float,
                'customs': float,
                'handling': float,
                'lead_time_mean': float,
                'lead_time_std': float,
                'quality_rate': float,
                'availability': float,
                'reliability': float,
                'sourcing_path': str,
                'supplier_id': str,
            }
        """
        accepted_ctes = []
        
        for opt_data in options_data:
            # Construir objetos de evaluación
            cost_breakdown = CostBreakdown(
                unit_cost=opt_data.get('cost', 0.0),
                transportation_cost=opt_data.get('transport', 0.0),
                customs_duty=opt_data.get('customs', 0.0),
                handling_cost=opt_data.get('handling', 0.0),
            )
            
            time_risk = TimeRiskAssessment(
                lead_time_mean=opt_data.get('lead_time_mean', 0.0),
                lead_time_std=opt_data.get('lead_time_std', 0.0),
                on_time_percentage=opt_data.get('on_time_pct', 0.95),
            )
            
            quality_risk = QualityRiskAssessment(
                quality_acceptance_rate=opt_data.get('quality_rate', 0.99),
                availability_percentage=opt_data.get('availability', 0.95),
                reliability_score=opt_data.get('reliability', None),
            )
            
            # Calcular CTE
            rules = self.get_rules_for_criticality(context.item_criticality)
            cte = self.calculate_cte(
                option_id=opt_data['option_id'],
                item_id=opt_data['item_id'],
                cost_breakdown=cost_breakdown,
                time_risk=time_risk,
                quality_risk=quality_risk,
                context=context,
                sourcing_path=opt_data.get('sourcing_path', 'PURCHASE'),
                supplier_id=opt_data.get('supplier_id'),
                weights={
                    'cost': rules.weight_cost,
                    'time': rules.weight_time,
                    'risk': rules.weight_risk,
                }
            )
            
            # Aplicar cut
            cut_result = self.apply_criticality_cut(cte, context)
            
            if cut_result.accepted:
                accepted_ctes.append(cte)
        
        return accepted_ctes, self.cut_results
    
    def get_feasible_set(self) -> List[CTEScore]:
        """Obtener conjunto factible (aceptadas)"""
        return [c.score for c in self.cut_results if c.score and c.accepted]
    
    def get_rejected_set(self) -> List[ScoringCutResult]:
        """Obtener rechazadas"""
        return [c for c in self.cut_results if not c.accepted]
    
    def get_cut_report(self) -> str:
        """Generar reporte de cuts"""
        if not self.cut_results:
            return "No cut results yet"
        
        accepted = [c for c in self.cut_results if c.accepted]
        rejected = [c for c in self.cut_results if not c.accepted]
        
        lines = [
            f"Cut Report - Criticidad: {len(accepted)} aceptadas, {len(rejected)} rechazadas",
            f"\nRECHAZADAS ({len(rejected)}):",
        ]
        
        for cut in rejected:
            lines.append(f"  ❌ {cut.option_id} ({cut.rejected_by}): {cut.reason}")
        
        lines.append(f"\nACEPTADAS ({len(accepted)}):")
        
        # Ordenar aceptadas por CTE
        accepted_sorted = sorted(accepted, key=lambda c: c.score.cte_value if c.score else 0, reverse=True)
        
        for cut in accepted_sorted[:10]:  # Top 10
            if cut.score:
                lines.append(f"  ✅ {cut.option_id}: CTE={cut.score.cte_value:.3f}")
        
        return "\n".join(lines)
