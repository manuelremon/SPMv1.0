"""
Algoritmos de optimización para el módulo Planner.

Exporta:
- Arquitectura base (BaseAlgorithm, AlgorithmRegistry, etc.)
- Algoritmos implementados (Reserve Dynamic, Purchase Multi-criterion, etc.)
"""

from .base_algorithm import (
    # Enums
    AlgorithmType,
    AlgorithmStatus,
    
    # DTOs
    AlgorithmInput,
    AlgorithmOutput,
    
    # Classes
    BaseAlgorithm,
    AlgorithmRegistry,
    AlgorithmExecutor,
    
    # Global instances
    get_registry,
    get_executor,
    register_algorithm,
    execute_algorithm
)

from .reserve_dynamic import (
    ReserveDynamicAlgorithm,
    get_reserve_dynamic_algorithm
)

from .purchase_multicriterion import (
    PurchaseMulticriterionAlgorithm,
    get_purchase_multicriterion_algorithm
)

from .release_marginal_cost import (
    ReleaseMarginalCostAlgorithm,
    get_release_marginal_algorithm
)

from .disassembly_knapsack import (
    DisassemblyKnapsackAlgorithm,
    get_disassembly_knapsack_algorithm
)

from .substitutes_graph import (
    SubstitutesGraphAlgorithm,
    get_substitutes_graph_algorithm
)

from .ctp_johnson import (
    CTPJohnsonAlgorithm,
    get_ctp_johnson_algorithm
)

from .transfer_tdabc import (
    TransferTDABCAlgorithm,
    get_transfer_tdabc_algorithm
)

from .expedite_probability import (
    ExpediteProbabilityAlgorithm,
    get_expedite_probability_algorithm
)

__all__ = [
    # Base
    "AlgorithmType",
    "AlgorithmStatus",
    "AlgorithmInput",
    "AlgorithmOutput",
    "BaseAlgorithm",
    "AlgorithmRegistry",
    "AlgorithmExecutor",
    "get_registry",
    "get_executor",
    "register_algorithm",
    "execute_algorithm",
    
    # Algorithms (8 total)
    "ReserveDynamicAlgorithm",
    "get_reserve_dynamic_algorithm",
    "PurchaseMulticriterionAlgorithm",
    "get_purchase_multicriterion_algorithm",
    "ReleaseMarginalCostAlgorithm",
    "get_release_marginal_algorithm",
    "DisassemblyKnapsackAlgorithm",
    "get_disassembly_knapsack_algorithm",
    "SubstitutesGraphAlgorithm",
    "get_substitutes_graph_algorithm",
    "CTPJohnsonAlgorithm",
    "get_ctp_johnson_algorithm",
    "TransferTDABCAlgorithm",
    "get_transfer_tdabc_algorithm",
    "ExpediteProbabilityAlgorithm",
    "get_expedite_probability_algorithm",
]
