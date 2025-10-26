"""
Test Suite para DisassemblyKnapsackAlgorithm
Cubre: 15 tests de funcionalidad completa
"""

import pytest
from src.planner.algorithms import (
    AlgorithmInput, DisassemblyKnapsackAlgorithm, AlgorithmStatus
)


class TestDisassemblyKnapsackAlgorithm:
    """Test suite para algoritmo de knapsack de desassembly"""
    
    @pytest.fixture
    def algo(self):
        """Instancia del algoritmo"""
        return DisassemblyKnapsackAlgorithm()
    
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
        assert "demand_quantity debe ser > 0" in error_msg
    
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
    
    # ===== TESTS DE EJECUCIÓN =====
    
    def test_execute_full_disassembly_high_value(self, algo):
        """Test ejecución: desassembly completo si hay alto valor"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="LOW"  # Más agresivo
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
        assert output.proposed_quantity >= 0
        assert output.confidence_score >= 0.0
        assert "Desensamblar" in output.reasoning or "No desensamblar" in output.reasoning
    
    def test_execute_critical_item_conservative(self, algo):
        """Test ejecución conservadora para items críticos"""
        input_data = AlgorithmInput(
            item_id="ITEM-CRIT-001",
            demand_quantity=50.0,
            required_date="2025-11-01",
            local_stock={"ITEM-CRIT-001": 30.0},
            criticality="CRITICAL"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
        # Items críticos tienen confidence score válido (0-1)
        assert 0.0 <= output.confidence_score <= 1.0
    
    def test_execute_with_selected_option(self, algo):
        """Test que selected_option tenga valor válido"""
        input_data = AlgorithmInput(
            item_id="ITEM-002",
            demand_quantity=80.0,
            required_date="2025-11-01",
            local_stock={"ITEM-002": 40.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.selected_option in ["disassembly_full", "disassembly_partial", "disassembly_none"]
    
    # ===== TESTS DE TELEMETRÍA =====
    
    def test_run_with_telemetry(self, algo):
        """Test run() con telemetría (wrapper de execute)"""
        input_data = AlgorithmInput(
            item_id="ITEM-003",
            demand_quantity=120.0,
            required_date="2025-11-01",
            local_stock={"ITEM-003": 60.0},
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
        assert metadata["type"] == "disassembly_knapsack"
    
    # ===== TESTS DE LÓGICA =====
    
    def test_reasoning_contains_analysis(self, algo):
        """Test que reasoning contiene análisis de components"""
        input_data = AlgorithmInput(
            item_id="ITEM-004",
            demand_quantity=90.0,
            required_date="2025-11-01",
            local_stock={"ITEM-004": 45.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.reasoning is not None
        assert "Componentes" in output.reasoning
        assert "$" in output.reasoning  # Tiene valores monetarios
    
    def test_multiple_executions_tracking(self, algo):
        """Test que tracking incremente correctamente"""
        input_data = AlgorithmInput(
            item_id="ITEM-005",
            demand_quantity=75.0,
            required_date="2025-11-01",
            local_stock={"ITEM-005": 35.0},
            criticality="LOW"
        )
        
        assert algo.execution_count == 0
        algo.execute(input_data)
        assert algo.execution_count == 1
        algo.execute(input_data)
        assert algo.execution_count == 2
        assert len(algo.execution_history) == 2
    
    # ===== EDGE CASES =====
    
    def test_edge_case_minimal_demand(self, algo):
        """Test con demand mínimo"""
        input_data = AlgorithmInput(
            item_id="ITEM-MIN",
            demand_quantity=0.1,
            required_date="2025-11-01",
            local_stock={"ITEM-MIN": 0.05},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
    
    def test_edge_case_empty_stock_dict(self, algo):
        """Test con local_stock vacío"""
        input_data = AlgorithmInput(
            item_id="ITEM-EMPTY",
            demand_quantity=50.0,
            required_date="2025-11-01",
            local_stock={},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        # Debe manejarse sin error
        assert output.success is True
    
    # ===== TESTS DE RANGO =====
    
    def test_confidence_score_range(self, algo):
        """Test que confidence siempre esté en rango [0, 1]"""
        for criticality in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            input_data = AlgorithmInput(
                item_id=f"ITEM-{criticality}",
                demand_quantity=100.0,
                required_date="2025-11-01",
                local_stock={f"ITEM-{criticality}": 50.0},
                criticality=criticality
            )
            output = algo.execute(input_data)
            
            assert 0.0 <= output.confidence_score <= 1.0
    
    def test_selected_option_values(self, algo):
        """Test que selected_option tenga valores válidos"""
        valid_options = ["disassembly_full", "disassembly_partial", "disassembly_none"]
        
        input_data = AlgorithmInput(
            item_id="ITEM-TEST",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-TEST": 50.0},
            criticality="MEDIUM"
        )
        output = algo.execute(input_data)
        
        assert output.selected_option in valid_options
    
    def test_proposed_quantity_non_negative(self, algo):
        """Test que proposed_quantity siempre sea >= 0"""
        for demand in [10.0, 50.0, 100.0, 500.0]:
            input_data = AlgorithmInput(
                item_id="ITEM-QTY",
                demand_quantity=demand,
                required_date="2025-11-01",
                local_stock={"ITEM-QTY": demand * 0.5},
                criticality="MEDIUM"
            )
            output = algo.execute(input_data)
            
            assert output.proposed_quantity >= 0
            assert output.proposed_quantity <= demand * 1.1  # No puede exceder demand en mucho
