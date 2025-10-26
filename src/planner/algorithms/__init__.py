"""
Módulo de Algoritmos de Optimización por Vía

Componentes:
- base_algorithm.py: Interfaz y arquitectura base
- reserve_dynamic.py: Asignación dinámica de stock local
- release_marginal_cost.py: Liberación de reservas sub-óptimas
- disassembly_knapsack.py: Desensamble optimizado BOM
- substitutes_graph.py: Búsqueda de sustitutos en grafo
- ctp_johnson.py: Scheduling con algoritmo Johnson
- transfer_tdabc.py: Transferencias con TDABC
- expedite_probability.py: Aceleración probabilística
- purchase_multicriterion.py: Compra multi-criterio
"""

from .base_algorithm import (
    AlgorithmType,
    AlgorithmStatus,
    AlgorithmInput,
    AlgorithmOutput,
    BaseAlgorithm,
    AlgorithmRegistry,
    AlgorithmExecutor,
    get_registry,
    get_executor,
    register_algorithm,
    execute_algorithm,
)

from .reserve_dynamic import (
    ReserveDynamicAlgorithm,
    LocalStockAllocation,
    get_reserve_dynamic_algorithm,
)
from .release_marginal_cost import ReleaseMarginalCostAlgorithm
from .disassembly_knapsack import DisassemblyKnapsackAlgorithm
from .substitutes_graph import SubstitutesGraphAlgorithm
from .ctp_johnson import CTPJohnsonAlgorithm
from .transfer_tdabc import TransferTDABCAlgorithm
from .expedite_probability import ExpediteProbabilityAlgorithm
from .purchase_multicriterion import PurchaseMulticriterionAlgorithm

__all__ = [
    # Types
    "AlgorithmType",
    "AlgorithmStatus",
    "AlgorithmInput",
    "AlgorithmOutput",
    
    # Base classes
    "BaseAlgorithm",
    "AlgorithmRegistry",
    "AlgorithmExecutor",
    
    # Functions
    "get_registry",
    "get_executor",
    "register_algorithm",
    "execute_algorithm",
    
    # Algorithm implementations (8 total)
    "ReserveDynamicAlgorithm",
    "ReleaseMarginalCostAlgorithm",
    "DisassemblyKnapsackAlgorithm",
    "SubstitutesGraphAlgorithm",
    "CTPJohnsonAlgorithm",
    "TransferTDABCAlgorithm",
    "ExpediteProbabilityAlgorithm",
    "PurchaseMulticriterionAlgorithm",
    
    # Support
    "LocalStockAllocation",
    "get_reserve_dynamic_algorithm",
]
