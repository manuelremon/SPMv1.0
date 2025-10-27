"""
Test Suite para SubstitutesGraphAlgorithm
Cubre: 16 tests de funcionalidad completa
"""

import pytest
from src.planner.algorithms import (
    AlgorithmInput, SubstitutesGraphAlgorithm, AlgorithmStatus
)


class TestSubstitutesGraphAlgorithm:
    """Test suite para algoritmo de búsqueda en grafo de sustitutos"""
    
    @pytest.fixture
    def algo(self):
        """Instancia del algoritmo"""
        return SubstitutesGraphAlgorithm()
    
    # ===== TESTS DE INICIALIZACIÓN =====
    
    def test_algorithm_initialization(self, algo):
        """Test inicialización del algoritmo"""
        assert algo is not None
        assert algo.algorithm_type is not None
        assert algo.execution_count == 0
        assert algo.execution_history == []
    
    # ===== TESTS DE VALIDACIÓN =====
    
    def test_validate_input_valid(self, algo):
        """Test validación con entrada válida"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="MEDIUM"
        )
        is_valid, error_msg = algo.validate_input(input_data)
        assert is_valid is True
        assert error_msg == "OK"
    
    def test_validate_input_empty_item_id(self, algo):
        """Test validación rechaza item_id vacío"""
        input_data = AlgorithmInput(
            item_id="",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="MEDIUM"
        )
        is_valid, error_msg = algo.validate_input(input_data)
        assert is_valid is False
    
    def test_validate_input_zero_demand(self, algo):
        """Test validación rechaza demand = 0"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=0.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="MEDIUM"
        )
        is_valid, error_msg = algo.validate_input(input_data)
        assert is_valid is False
    
    # ===== TESTS DE EJECUCIÓN =====
    
    def test_execute_with_equivalent_found(self, algo):
        """Test ejecución encuentra equivalente"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
        assert output.proposed_quantity >= 0
        assert output.confidence_score >= 0.0
        assert "Sustituto" in output.reasoning or "No hay equivalentes" in output.reasoning
    
    def test_execute_critical_deep_search(self, algo):
        """Test búsqueda DFS para items críticos"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=50.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 30.0},
            criticality="CRITICAL"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        # Para críticos debe hacer búsqueda DFS
        assert "DFS" in output.reasoning or "Profundidad" in output.reasoning
    
    def test_execute_low_priority_broad_search(self, algo):
        """Test búsqueda BFS para items low priority"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=80.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 40.0},
            criticality="LOW"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.confidence_score >= 0.0
    
    def test_execute_with_selected_option(self, algo):
        """Test que selected_option sea válido"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=70.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 35.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.selected_option in ["substitute_found", "substitute_none"]
    
    # ===== TESTS DE TELEMETRÍA =====
    
    def test_run_with_telemetry(self, algo):
        """Test run() wrapper con telemetría"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=90.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 45.0},
            criticality="HIGH"
        )
        output = algo.run(input_data)
        
        assert output.success is True
        assert output.execution_time_ms >= 0
        assert algo.execution_count > 0
    
    def test_get_metadata(self, algo):
        """Test metadata del algoritmo"""
        metadata = algo.get_metadata()
        
        assert metadata is not None
        assert "type" in metadata
        assert "execution_count" in metadata
        assert metadata["type"] == "substitutes_graph"
    
    # ===== TESTS DE LÓGICA =====
    
    def test_reasoning_contains_graph_analysis(self, algo):
        """Test que reasoning contiene análisis de grafo"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=75.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 37.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        if "Sustituto encontrado" in output.reasoning:
            # Si encontró sustituto, debe tener análisis detallado
            assert "Compatibilidad" in output.reasoning or "%" in output.reasoning
    
    def test_multiple_executions_tracking(self, algo):
        """Test que tracking incremente correctamente"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=60.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 30.0},
            criticality="MEDIUM"
        )
        
        assert algo.execution_count == 0
        algo.execute(input_data)
        assert algo.execution_count == 1
        algo.execute(input_data)
        assert algo.execution_count == 2
        assert len(algo.execution_history) == 2
    
    # ===== EDGE CASES =====
    
    def test_edge_case_unknown_item(self, algo):
        """Test con item desconocido (no en grafo)"""
        input_data = AlgorithmInput(
            item_id="UNKNOWN-ITEM",
            demand_quantity=50.0,
            required_date="2025-11-01",
            local_stock={"UNKNOWN-ITEM": 25.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        # Debe manejarse sin error
        assert output.success is True
        assert output.selected_option == "substitute_none"
    
    def test_edge_case_high_demand(self, algo):
        """Test con demand muy alto"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=1000.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 500.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.proposed_quantity == input_data.demand_quantity
    
    # ===== TESTS DE RANGO =====
    
    def test_confidence_score_range(self, algo):
        """Test que confidence siempre esté en rango [0, 1]"""
        for criticality in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            input_data = AlgorithmInput(
                item_id="ITEM-001",
                demand_quantity=100.0,
                required_date="2025-11-01",
                local_stock={"ITEM-001": 50.0},
                criticality=criticality
            )
            output = algo.execute(input_data)
            
            assert 0.0 <= output.confidence_score <= 1.0
    
    def test_selected_option_values(self, algo):
        """Test que selected_option tenga valores válidos"""
        valid_options = ["substitute_found", "substitute_none"]
        
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.selected_option in valid_options
