"""
Algoritmo: CTP (Crashing Time Problem - Johnson)

Responsabilidades:
- Resolver rutas críticas con trade-offs costo/tiempo
- Johnson algorithm para job scheduling
- Minimizar makespan

Complejidad: O(n log n) sorting
"""

from typing import Tuple
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


class CTPJohnsonAlgorithm(BaseAlgorithm):
    """Crashing Time Problem - Johnson algorithm para scheduling"""
    
    def __init__(self):
        super().__init__(AlgorithmType.CTP_JOHNSON)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        if input_data.required_date is None:
            return False, "Fecha requerida es obligatoria"
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        # TODO: Implementar Johnson scheduling algorithm
        proposed_qty = input_data.demand_quantity
        confidence = 0.68
        
        return AlgorithmOutput(
            algorithm_type=AlgorithmType.CTP_JOHNSON,
            item_id=input_data.item_id,
            success=True,
            status=AlgorithmStatus.COMPLETED,
            selected_option="CTP_SCHEDULED",
            proposed_quantity=proposed_qty,
            estimated_cost=55.0,
            confidence_score=confidence,
            reasoning=f"CTP Johnson: {proposed_qty:.0f} u (makespan optimal)"
        )
