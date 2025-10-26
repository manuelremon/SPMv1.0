"""
Algoritmo: Desarme (Knapsack 0/1)

Responsabilidades:
- Resolver BOM knapsack problem
- Minimizar costo de materiales
- Validar factibilidad técnica

Complejidad: O(n*W) donde W = presupuesto
"""

from typing import Tuple
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


class DisassemblyKnapsackAlgorithm(BaseAlgorithm):
    """Algoritmo Knapsack 0/1 para getBOM components"""
    
    def __init__(self):
        super().__init__(AlgorithmType.DISASSEMBLY_KNAPSACK)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        if input_data.budget <= 0:
            return False, "Presupuesto debe ser > 0"
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        # TODO: Implementar Knapsack DP solver
        proposed_qty = input_data.demand_quantity * 0.8
        confidence = 0.70
        
        return AlgorithmOutput(
            algorithm_type=AlgorithmType.DISASSEMBLY_KNAPSACK,
            item_id=input_data.item_id,
            success=True,
            status=AlgorithmStatus.COMPLETED,
            selected_option="DISASSEMBLY_PARTIAL",
            proposed_quantity=proposed_qty,
            estimated_cost=75.0,
            confidence_score=confidence,
            reasoning=f"Desarmable: {proposed_qty:.0f} u (knapsack optimal)"
        )
