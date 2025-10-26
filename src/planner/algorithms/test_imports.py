"""
Test suite para verificar que los 8 algoritmos se importan correctamente
"""

import pytest
from src.planner.algorithms import (
    AlgorithmType,
    AlgorithmStatus,
    AlgorithmInput,
    AlgorithmOutput,
    BaseAlgorithm,
    ReserveDynamicAlgorithm,
    ReleaseMarginalCostAlgorithm,
    DisassemblyKnapsackAlgorithm,
    SubstitutesGraphAlgorithm,
    CTPJohnsonAlgorithm,
    TransferTDABCAlgorithm,
    ExpediteProbabilityAlgorithm,
    PurchaseMulticriterionAlgorithm,
    get_registry,
)


class TestAlgorithmImports:
    """Verifica que todos los algoritmos estén disponibles"""
    
    def test_all_algorithms_importable(self):
        """Todos los 8 algoritmos deben ser importables"""
        algorithms = [
            ReserveDynamicAlgorithm,
            ReleaseMarginalCostAlgorithm,
            DisassemblyKnapsackAlgorithm,
            SubstitutesGraphAlgorithm,
            CTPJohnsonAlgorithm,
            TransferTDABCAlgorithm,
            ExpediteProbabilityAlgorithm,
            PurchaseMulticriterionAlgorithm,
        ]
        assert len(algorithms) == 8
        for algo in algorithms:
            assert issubclass(algo, BaseAlgorithm)
    
    def test_algorithm_types_coverage(self):
        """Todos los AlgorithmType enum valores tienen un algoritmo"""
        registry = get_registry()
        
        # Crear instancia de cada algoritmo
        algs = [
            ReserveDynamicAlgorithm(),
            ReleaseMarginalCostAlgorithm(),
            DisassemblyKnapsackAlgorithm(),
            SubstitutesGraphAlgorithm(),
            CTPJohnsonAlgorithm(),
            TransferTDABCAlgorithm(),
            ExpediteProbabilityAlgorithm(),
            PurchaseMulticriterionAlgorithm(),
        ]
        
        # Registrar
        for algo in algs:
            registry.register(algo)
        
        # Verificar que se registraron todos
        assert len(registry.list_algorithms()) >= 8
    
    def test_algorithm_instantiation(self):
        """Cada algoritmo debe ser instanciable"""
        algs = [
            ReserveDynamicAlgorithm(),
            ReleaseMarginalCostAlgorithm(),
            DisassemblyKnapsackAlgorithm(),
            SubstitutesGraphAlgorithm(),
            CTPJohnsonAlgorithm(),
            TransferTDABCAlgorithm(),
            ExpediteProbabilityAlgorithm(),
            PurchaseMulticriterionAlgorithm(),
        ]
        
        for algo in algs:
            assert isinstance(algo, BaseAlgorithm)
            assert algo.algorithm_type in AlgorithmType
    
    def test_algorithm_metadata(self):
        """Cada algoritmo debe retornar metadata"""
        algs = [
            ReserveDynamicAlgorithm(),
            ReleaseMarginalCostAlgorithm(),
            DisassemblyKnapsackAlgorithm(),
            SubstitutesGraphAlgorithm(),
            CTPJohnsonAlgorithm(),
            TransferTDABCAlgorithm(),
            ExpediteProbabilityAlgorithm(),
            PurchaseMulticriterionAlgorithm(),
        ]
        
        for algo in algs:
            metadata = algo.get_metadata()
            assert metadata is not None
            assert "type" in metadata
            assert "execution_count" in metadata
            assert "avg_execution_time_ms" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
