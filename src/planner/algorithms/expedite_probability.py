"""Expedición probabilística - aceleración de lead times"""
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)

@dataclass
class ExpediteOption:
    """Opción de expedición"""
    label: str
    lead_days: int
    premium_cost: float
    success_prob: float

@dataclass
class ExpediteAnalysis:
    """Análisis de expedición"""
    selected_option: str
    expedite_qty: float
    lead_days: int
    premium_cost: float
    success_probability: float
    confidence: float
    reasoning: str

class ExpediteProbabilityAlgorithm(BaseAlgorithm):
    """Calcula probabilidad y costo de expedición para acelerar supply"""
    
    def __init__(self):
        super().__init__(AlgorithmType.EXPEDITE_PROBABILITY)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida: item_id, demand_quantity, required_date"""
        if not input_data.item_id:
            return False, "item_id requerido"
        if input_data.demand_quantity <= 0:
            return False, "demand_quantity debe ser > 0"
        if input_data.required_date is None:
            return False, "required_date obligatoria para expedición"
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        7 pasos: (1) build options, (2) calc prob, (3) calc costs,
        (4) select best, (5) confidence, (6) reasoning, (7) return
        """
        try:
            options = self._build_expedite_options(input_data)
            analysis = self._analyze_expedite(input_data, options)
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.EXPEDITE_PROBABILITY,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=analysis.selected_option,
                proposed_quantity=analysis.expedite_qty,
                estimated_cost=analysis.premium_cost,
                confidence_score=analysis.confidence,
                reasoning=analysis.reasoning
            )
        except Exception as e:
            logger.error(f"Error ejecutando ExpediteAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.EXPEDITE_PROBABILITY,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                reasoning=f"Error: {str(e)}"
            )
    
    def _build_expedite_options(self, input_data: AlgorithmInput) -> List[ExpediteOption]:
        """Mock 3 opciones: NONE, PARTIAL, FULL expedición"""
        return [
            ExpediteOption("EXPEDITE_NONE", 14, 0.0, 0.85),
            ExpediteOption("EXPEDITE_PARTIAL", 7, 45.0, 0.78),
            ExpediteOption("EXPEDITE_FULL", 3, 95.0, 0.65),
        ]
    
    def _analyze_expedite(self, input_data: AlgorithmInput, options: List[ExpediteOption]) -> ExpediteAnalysis:
        """Selecciona opción basada en criticidad y margen de tiempo"""
        days_to_required = self._calc_days_to_required(input_data.required_date)
        criticality = input_data.criticality
        
        # Lógica simple: HIGH criticality → EXPEDITE_FULL, MEDIUM → PARTIAL, LOW → NONE
        if criticality == "CRITICAL" and days_to_required <= 5:
            best_option = options[2]  # FULL
            expedite_qty = input_data.demand_quantity * 0.95
        elif criticality in ["HIGH", "MEDIUM"] and days_to_required <= 10:
            best_option = options[1]  # PARTIAL
            expedite_qty = input_data.demand_quantity * 0.70
        else:
            best_option = options[0]  # NONE
            expedite_qty = input_data.demand_quantity * 0.50
        
        confidence = self._calc_confidence(criticality, days_to_required, best_option.success_prob)
        reasoning = self._generate_reasoning(best_option, expedite_qty, days_to_required)
        
        return ExpediteAnalysis(
            selected_option=best_option.label,
            expedite_qty=expedite_qty,
            lead_days=best_option.lead_days,
            premium_cost=best_option.premium_cost,
            success_probability=best_option.success_prob,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _calc_days_to_required(self, required_date: datetime) -> int:
        """Días disponibles hasta fecha requerida"""
        today = datetime.now()
        delta = required_date - today
        return max(0, delta.days)
    
    def _calc_confidence(self, criticality: str, days_available: int, success_prob: float) -> float:
        """Multi-factor: criticality + time pressure + success_prob"""
        crit_factor = {"CRITICAL": 0.95, "HIGH": 0.85, "MEDIUM": 0.75, "LOW": 0.60}.get(criticality, 0.60)
        time_factor = min(1.0, days_available / 14.0)
        return min(0.99, (crit_factor * success_prob * (0.7 + 0.3 * time_factor)))
    
    def _generate_reasoning(self, option: ExpediteOption, qty: float, days: int) -> str:
        """Breve explicación de decisión"""
        return f"{option.label}: {qty:.0f}u, lead={option.lead_days}d, premium=${option.premium_cost:.0f}, prob={option.success_prob:.0%}"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "algorithm_type": self.algorithm_type.value,
            "name": "ExpediteProbabilityAlgorithm",
            "execution_count": self.execution_count,
            "avg_execution_time_ms": (
                sum(self.execution_history) / len(self.execution_history)
                if self.execution_history else 0
            )
        }
