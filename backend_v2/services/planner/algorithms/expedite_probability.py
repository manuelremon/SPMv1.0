"""
Algoritmo: Expedición Probabilística

Responsabilidades:
- Calcular probabilidad y costo de expedición para acelerar supply
- Evaluar trade-off entre lead time y premium cost
- Minimizar riesgo considerando éxito probabilístico

Complejidad: O(n) - evaluación de opciones
Estrategia: Multi-criterio basado en criticidad y tiempo disponible
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging
from datetime import datetime

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
            # 1. Construir opciones de expedición
            if input_data.db_session:
                options = self._fetch_expedite_options_from_db(
                    input_data.db_session,
                    input_data.item_id
                )
            else:
                options = self._build_expedite_options(input_data)
            
            # 2-6. Analizar y seleccionar mejor opción
            analysis = self._analyze_expedite(input_data, options)
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.EXPEDITE_PROBABILITY,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=analysis.selected_option,
                proposed_quantity=analysis.expedite_qty,
                estimated_cost=analysis.premium_cost,
                estimated_lead_time=analysis.lead_days,
                confidence_score=analysis.confidence,
                reasoning=analysis.reasoning
            )
        
        except Exception as e:
            logger.error(f"Error en ExpediteProbabilityAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.EXPEDITE_PROBABILITY,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                proposed_quantity=0.0,
                estimated_cost=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    def _fetch_expedite_options_from_db(self, session, item_id: str) -> List[ExpediteOption]:
        """Consulta proveedores reales y genera opciones de expedición"""
        try:
            from services.planner.repositories import SupplierRepository
            
            repo = SupplierRepository(session)
            agreements = repo.get_price_agreements(item_id, valid_only=True)
            
            if not agreements:
                return self._build_expedite_options_simulated()
            
            # Generar opciones basadas en lead times de proveedores
            options = []
            
            # NONE: Lead time normal del mejor proveedor
            best_normal = min(agreements, key=lambda a: a.supplier.lead_time_days)
            options.append(ExpediteOption(
                "EXPEDITE_NONE",
                best_normal.supplier.lead_time_days,
                0.0,
                0.90
            ))
            
            # PARTIAL: Reducir 50% lead time con premium 40%
            partial_days = max(3, best_normal.supplier.lead_time_days // 2)
            partial_cost = float(best_normal.unit_price_usd) * 0.40
            options.append(ExpediteOption(
                "EXPEDITE_PARTIAL",
                partial_days,
                partial_cost,
                0.80
            ))
            
            # FULL: Reducir 75% lead time con premium 90%
            full_days = max(2, best_normal.supplier.lead_time_days // 4)
            full_cost = float(best_normal.unit_price_usd) * 0.90
            options.append(ExpediteOption(
                "EXPEDITE_FULL",
                full_days,
                full_cost,
                0.70
            ))
            
            return options
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch expedite options from DB: {e}")
            return self._build_expedite_options_simulated()
    
    def _build_expedite_options_simulated(self) -> List[ExpediteOption]:
        """Opciones simuladas para backward compatibility"""
        return [
            ExpediteOption("EXPEDITE_NONE", 14, 0.0, 0.85),
            ExpediteOption("EXPEDITE_PARTIAL", 7, 45.0, 0.78),
            ExpediteOption("EXPEDITE_FULL", 3, 95.0, 0.65),
        ]
    
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
    
    def _calc_days_to_required(self, required_date: str) -> int:
        """Días disponibles hasta fecha requerida"""
        try:
            # Convertir string ISO a datetime
            if isinstance(required_date, str):
                req_dt = datetime.fromisoformat(required_date.replace('Z', '+00:00'))
            else:
                req_dt = required_date
            
            today = datetime.now(req_dt.tzinfo) if req_dt.tzinfo else datetime.now()
            delta = req_dt - today
            return max(0, delta.days)
        except Exception:
            return 7  # Fallback: 7 días por defecto
    
    def _calc_confidence(self, criticality: str, days_available: int, success_prob: float) -> float:
        """Multi-factor: criticality + time pressure + success_prob"""
        crit_factor = {"CRITICAL": 0.95, "HIGH": 0.85, "MEDIUM": 0.75, "LOW": 0.60}.get(criticality, 0.60)
        time_factor = min(1.0, days_available / 14.0)
        return min(0.99, (crit_factor * success_prob * (0.7 + 0.3 * time_factor)))
    
    def _generate_reasoning(self, option: ExpediteOption, qty: float, days: int) -> str:
        """Breve explicación de decisión"""
        return (
            f"{option.label}: {qty:.0f}u, lead={option.lead_days}d, "
            f"premium=${option.premium_cost:.0f}, prob={option.success_prob:.0%}, "
            f"días disponibles={days}"
        )


# Factory function
def get_expedite_probability_algorithm() -> ExpediteProbabilityAlgorithm:
    """Obtiene instancia del algoritmo Expedite Probability"""
    return ExpediteProbabilityAlgorithm()
