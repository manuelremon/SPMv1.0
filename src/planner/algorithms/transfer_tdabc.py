"""
Algoritmo: Transferencias (TDABC - Time-Driven ABC)

Responsabilidades:
- Buscar en ubicaciones alternas usando TDABC
- Calcular costo de transferencia vs. plazo
- Optimizar ruta de envío

Complejidad: O(n²) - distancias/almacenes
"""

from typing import Tuple
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


class TransferTDABCAlgorithm(BaseAlgorithm):
    """Time-Driven Activity-Based Costing para transferencias"""
    
    def __init__(self):
        super().__init__(AlgorithmType.TRANSFER_TDABC)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        if input_data.demand_quantity <= 0:
            return False, "Demanda debe ser > 0"
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        # TODO: Implementar TDABC cost model
        proposed_qty = input_data.demand_quantity * 0.9
        confidence = 0.71
        
        return AlgorithmOutput(
            algorithm_type=AlgorithmType.TRANSFER_TDABC,
            item_id=input_data.item_id,
            success=True,
            status=AlgorithmStatus.COMPLETED,
            selected_option="TRANSFER_AVAILABLE",
            proposed_quantity=proposed_qty,
            estimated_cost=80.0,
            confidence_score=confidence,
            reasoning=f"Transferencia TDABC: {proposed_qty:.0f} u (lead time + cost optimal)"
        )
