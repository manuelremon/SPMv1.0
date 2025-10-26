"""
Tests para ReleaseMarginalCostAlgorithm - VERSIÓN ACTUALIZADA
"""

import pytest
from src.planner.algorithms import (
    AlgorithmInput,
    ReleaseMarginalCostAlgorithm,
    AlgorithmStatus,
)


class TestReleaseMarginalCostAlgorithm:
    """Tests para algoritmo de liberación min-costo"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.algo = ReleaseMarginalCostAlgorithm()
    
    def test_algorithm_initialization(self):
        """Test inicialización del algoritmo"""
        assert self.algo is not None
        assert self.algo.algorithm_type.value == "release_marginal_cost"
        assert self.algo.execution_count == 0
    
    def test_validate_input_valid(self):
        """Test validación con entrada válida"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="HIGH"
        )
        is_valid, msg = self.algo.validate_input(input_data)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_input_zero_demand(self):
        """Test validación rechaza demanda 0"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="HIGH"
        )
        is_valid, msg = self.algo.validate_input(input_data)
        assert is_valid is False
    
    def test_execute_high_marginal_cost(self):
        """Test ejecución con alto ahorro marginal"""
        input_data = AlgorithmInput(
            item_id="ITEM-001",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-001": 50.0},
            criticality="LOW"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert output.status == AlgorithmStatus.COMPLETED
        assert output.proposed_quantity >= 0
        assert output.confidence_score > 0
    
    def test_execute_critical_item_conservative(self):
        """Test ejecución conservadora para items críticos"""
        input_data = AlgorithmInput(
            item_id="ITEM-003",
            demand_quantity=50.0,
            required_date="2025-11-01",
            local_stock={"ITEM-003": 30.0},
            criticality="CRITICAL"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert output.confidence_score < 1.0
    
    def test_run_with_telemetry(self):
        """Test run() wrapper con telemetría"""
        input_data = AlgorithmInput(
            item_id="ITEM-005",
            demand_quantity=120.0,
            required_date="2025-11-10",
            local_stock={"ITEM-005": 60.0},
            criticality="HIGH"
        )
        output = self.algo.run(input_data)
        
        assert output.success is True
        assert output.execution_time_ms >= 0
        assert self.algo.execution_count > 0
    
    def test_get_metadata(self):
        """Test metadata del algoritmo"""
        metadata = self.algo.get_metadata()
        
        assert metadata is not None
        assert "type" in metadata
        assert "execution_count" in metadata
        assert metadata["type"] == "release_marginal_cost"
    
    def test_reasoning_contains_analysis(self):
        """Test que reasoning contiene análisis detallado"""
        input_data = AlgorithmInput(
            item_id="ITEM-010",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-010": 50.0},
            criticality="HIGH"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert "costo" in output.reasoning.lower() or "ahorro" in output.reasoning.lower()
    
    def test_multiple_executions_tracking(self):
        """Test tracking de múltiples ejecuciones"""
        input_data = AlgorithmInput(
            item_id="ITEM-007",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-007": 50.0},
            criticality="HIGH"
        )
        
        count1 = self.algo.execution_count
        output1 = self.algo.run(input_data)
        count2 = self.algo.execution_count
        output2 = self.algo.run(input_data)
        count3 = self.algo.execution_count
        
        assert count2 == count1 + 1
        assert count3 == count2 + 1
        assert output1.success is True
        assert output2.success is True
    
    def test_edge_case_zero_stock(self):
        """Test edge case: stock local es 0"""
        input_data = AlgorithmInput(
            item_id="ITEM-008",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-008": 0.0},
            criticality="HIGH"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert output.proposed_quantity == 0
    
    def test_edge_case_empty_stock_dict(self):
        """Test edge case: diccionario de stock vacío"""
        input_data = AlgorithmInput(
            item_id="ITEM-009",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={},
            criticality="MEDIUM"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert output.proposed_quantity == 0
    
    def test_confidence_score_range(self):
        """Test que confidence score está en rango válido"""
        for criticality in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            input_data = AlgorithmInput(
                item_id=f"ITEM-{criticality}",
                demand_quantity=100.0,
                required_date="2025-11-01",
                local_stock={"ITEM": 50.0},
                criticality=criticality
            )
            output = self.algo.execute(input_data)
            
            assert 0.0 <= output.confidence_score <= 1.0
    
    def test_selected_option_values(self):
        """Test que selected_option tiene valores válidos"""
        input_data = AlgorithmInput(
            item_id="ITEM-011",
            demand_quantity=100.0,
            required_date="2025-11-01",
            local_stock={"ITEM-011": 50.0},
            criticality="MEDIUM"
        )
        output = self.algo.execute(input_data)
        
        assert output.success is True
        assert output.selected_option is not None
        assert "RELEASE" in output.selected_option


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
