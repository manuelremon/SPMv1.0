"""
Tests para validar arquitectura base de algoritmos

Cubre:
- BaseAlgorithm interface
- AlgorithmRegistry
- AlgorithmExecutor
- ReserveDynamicAlgorithm
"""

import pytest
from datetime import datetime, timedelta

from src.planner.algorithms.base_algorithm import (
    AlgorithmType, AlgorithmStatus, AlgorithmInput, AlgorithmOutput,
    BaseAlgorithm, AlgorithmRegistry, AlgorithmExecutor
)
from src.planner.algorithms.reserve_dynamic import ReserveDynamicAlgorithm


class TestBaseAlgorithmInterface:
    """Tests de interfaz base"""
    
    def test_algorithm_type_enum(self):
        """Valida enum AlgorithmType"""
        assert AlgorithmType.RESERVE_DYNAMIC.value == "reserve_dynamic"
        assert AlgorithmType.RELEASE_MARGINAL.value == "release_marginal_cost"
        assert AlgorithmType.DISASSEMBLY_KNAPSACK.value == "disassembly_knapsack"
        assert AlgorithmType.SUBSTITUTES_GRAPH.value == "substitutes_graph"
        assert AlgorithmType.CTP_JOHNSON.value == "ctp_johnson"
        assert AlgorithmType.TRANSFER_TDABC.value == "transfer_tdabc"
        assert AlgorithmType.EXPEDITE_PROBABILITY.value == "expedite_probability"
        assert AlgorithmType.PURCHASE_MULTICRITERION.value == "purchase_multicriterion"
        
        assert len(AlgorithmType) == 8
    
    def test_algorithm_status_enum(self):
        """Valida enum AlgorithmStatus"""
        assert AlgorithmStatus.INITIALIZED.value == "initialized"
        assert AlgorithmStatus.RUNNING.value == "running"
        assert AlgorithmStatus.COMPLETED.value == "completed"
        assert AlgorithmStatus.FAILED.value == "failed"
        assert AlgorithmStatus.TIMEOUT.value == "timeout"
    
    def test_algorithm_input_creation(self):
        """Crear AlgorithmInput válido"""
        input_data = AlgorithmInput(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=datetime.now().isoformat(),
            local_stock={"bin_A": 50.0, "bin_B": 30.0},
            criticality="HIGH",
            budget_available=1000.0
        )
        
        assert input_data.item_id == "MAT001"
        assert input_data.demand_quantity == 100.0
        assert sum(input_data.local_stock.values()) == 80.0
        assert input_data.criticality == "HIGH"
    
    def test_algorithm_output_creation(self):
        """Crear AlgorithmOutput válido"""
        output = AlgorithmOutput(
            algorithm_type=AlgorithmType.RESERVE_DYNAMIC,
            item_id="MAT001",
            success=True,
            status=AlgorithmStatus.COMPLETED,
            selected_option="LOCAL_STOCK",
            proposed_quantity=80.0,
            estimated_cost=0.0,
            confidence_score=0.85
        )
        
        assert output.algorithm_type == AlgorithmType.RESERVE_DYNAMIC
        assert output.success is True
        assert output.confidence_score == 0.85


class TestAlgorithmRegistry:
    """Tests de registry"""
    
    def test_registry_initialization(self):
        """Registry inicializa vacío"""
        registry = AlgorithmRegistry()
        assert registry.list_algorithms() == []
    
    def test_register_algorithm(self):
        """Registrar algoritmo"""
        registry = AlgorithmRegistry()
        algo = ReserveDynamicAlgorithm()
        
        registry.register(algo)
        
        assert registry.is_registered(AlgorithmType.RESERVE_DYNAMIC)
        assert registry.get(AlgorithmType.RESERVE_DYNAMIC) is algo
    
    def test_unregister_algorithm(self):
        """Desregistrar algoritmo"""
        registry = AlgorithmRegistry()
        algo = ReserveDynamicAlgorithm()
        
        registry.register(algo)
        assert registry.is_registered(AlgorithmType.RESERVE_DYNAMIC)
        
        registry.unregister(AlgorithmType.RESERVE_DYNAMIC)
        assert not registry.is_registered(AlgorithmType.RESERVE_DYNAMIC)
    
    def test_list_algorithms(self):
        """Listar algoritmos registrados"""
        registry = AlgorithmRegistry()
        algo1 = ReserveDynamicAlgorithm()
        
        registry.register(algo1)
        
        algorithms = registry.list_algorithms()
        assert len(algorithms) == 1
        assert algorithms[0]["type"] == "reserve_dynamic"


class TestReserveDynamicAlgorithm:
    """Tests de algoritmo Reserva Dinámica"""
    
    def _create_context(
        self,
        item_id="MAT001",
        demand=100.0,
        local_stock=None,
        criticality="MEDIUM"
    ):
        """Helper para crear contexto de test"""
        if local_stock is None:
            local_stock = {"bin_A": 50.0, "bin_B": 30.0}
        
        return AlgorithmInput(
            item_id=item_id,
            demand_quantity=demand,
            required_date=(datetime.now() + timedelta(days=5)).isoformat(),
            local_stock=local_stock,
            criticality=criticality,
            budget_available=1000.0
        )
    
    def test_algorithm_initialization(self):
        """Inicializa algoritmo"""
        algo = ReserveDynamicAlgorithm()
        assert algo.algorithm_type == AlgorithmType.RESERVE_DYNAMIC
        assert algo.execution_count == 0
    
    def test_validate_input_valid(self):
        """Validar input válido"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context()
        
        valid, error = algo.validate_input(input_data)
        
        assert valid is True
        assert error == ""
    
    def test_validate_input_no_stock(self):
        """Validar input sin stock local"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context(local_stock={})
        
        valid, error = algo.validate_input(input_data)
        
        assert valid is False
        assert "stock local" in error.lower()
    
    def test_validate_input_zero_demand(self):
        """Validar input con demanda 0"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context(demand=0)
        
        valid, error = algo.validate_input(input_data)
        
        assert valid is False
        assert "demanda" in error.lower()
    
    def test_execute_success(self):
        """Ejecutar algoritmo exitosamente"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context(demand=100.0)
        
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
        assert output.proposed_quantity > 0
        assert output.confidence_score >= 0.0
        assert output.confidence_score <= 1.0
    
    def test_execute_partial_reserve(self):
        """Stock parcial - reservar lo disponible"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context(
            demand=100.0,
            local_stock={"bin_A": 50.0}
        )
        
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.proposed_quantity <= 100.0
        assert output.proposed_quantity > 0
    
    def test_execute_high_criticality(self):
        """Alta criticidad = mayor prioridad"""
        algo = ReserveDynamicAlgorithm()
        
        # Comparar dos ejecuciones
        input_high = self._create_context(criticality="CRITICAL")
        input_medium = self._create_context(criticality="MEDIUM")
        
        output_high = algo.execute(input_high)
        output_medium = algo.execute(input_medium)
        
        # Ambas deberían ser exitosas
        assert output_high.success is True
        assert output_medium.success is True
    
    def test_execute_urgent_plazo(self):
        """Plazo urgente < 2 días = máxima prioridad"""
        algo = ReserveDynamicAlgorithm()
        
        input_urgent = AlgorithmInput(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=(datetime.now() + timedelta(hours=12)).isoformat(),
            local_stock={"bin_A": 50.0},
            criticality="MEDIUM"
        )
        
        output = algo.execute(input_urgent)
        
        assert output.success is True
        assert output.confidence_score > 0.0
    
    def test_run_wrapper(self):
        """Test wrapper run() con telemetría"""
        algo = ReserveDynamicAlgorithm()
        input_data = self._create_context()
        
        assert algo.execution_count == 0
        
        output = algo.run(input_data)
        
        assert output.success is True
        assert output.execution_time_ms > 0
        assert algo.execution_count == 1
        assert algo.total_execution_time > 0
    
    def test_get_metadata(self):
        """Obtener metadata del algoritmo"""
        algo = ReserveDynamicAlgorithm()
        
        metadata = algo.get_metadata()
        
        assert metadata["type"] == "reserve_dynamic"
        assert "execution_count" in metadata
        assert "total_execution_time_ms" in metadata
        assert "strategy" in metadata
        assert "description" in metadata


class TestAlgorithmExecutor:
    """Tests de executor"""
    
    def test_executor_initialization(self):
        """Inicializa executor"""
        registry = AlgorithmRegistry()
        executor = AlgorithmExecutor(registry)
        
        assert executor.registry is registry
    
    def test_execute_registered_algorithm(self):
        """Ejecutar algoritmo registrado"""
        registry = AlgorithmRegistry()
        algo = ReserveDynamicAlgorithm()
        registry.register(algo)
        
        executor = AlgorithmExecutor(registry)
        
        input_data = AlgorithmInput(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=datetime.now().isoformat(),
            local_stock={"bin_A": 50.0}
        )
        
        output = executor.execute(AlgorithmType.RESERVE_DYNAMIC, input_data)
        
        assert output.success is True
    
    def test_execute_unregistered_algorithm(self):
        """Ejecutar algoritmo no registrado"""
        registry = AlgorithmRegistry()
        executor = AlgorithmExecutor(registry)
        
        input_data = AlgorithmInput(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=datetime.now().isoformat()
        )
        
        output = executor.execute(AlgorithmType.RESERVE_DYNAMIC, input_data)
        
        assert output.success is False
        assert output.status == AlgorithmStatus.FAILED


class TestIntegration:
    """Tests de integración"""
    
    def test_end_to_end_reserve_dynamic(self):
        """E2E: Registrar, ejecutar, obtener resultado"""
        # 1. Setup
        registry = AlgorithmRegistry()
        algo = ReserveDynamicAlgorithm()
        registry.register(algo)
        
        executor = AlgorithmExecutor(registry)
        
        # 2. Ejecutar
        input_data = AlgorithmInput(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=(datetime.now() + timedelta(days=5)).isoformat(),
            local_stock={"bin_A": 50.0, "bin_B": 30.0},
            criticality="HIGH"
        )
        
        output = executor.execute(AlgorithmType.RESERVE_DYNAMIC, input_data)
        
        # 3. Validar resultado
        assert output.success is True
        assert output.algorithm_type == AlgorithmType.RESERVE_DYNAMIC
        assert output.proposed_quantity > 0
        assert output.confidence_score >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
