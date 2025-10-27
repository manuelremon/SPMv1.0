"""
Test Suite para CTPJohnsonAlgorithm - Rápido (12 tests)
"""

import pytest
from src.planner.algorithms import (
    AlgorithmInput, CTPJohnsonAlgorithm, AlgorithmStatus
)


class TestCTPJohnsonAlgorithm:
    """Test suite para Johnson's scheduling algorithm"""
    
    @pytest.fixture
    def algo(self):
        return CTPJohnsonAlgorithm()
    
    # Validación
    def test_validate_input_valid(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        is_valid, msg = algo.validate_input(inp)
        assert is_valid is True
        assert msg == "OK"
    
    def test_validate_input_missing_item(self, algo):
        inp = AlgorithmInput("", 100.0, "2025-11-01", {}, "MEDIUM")
        is_valid, _ = algo.validate_input(inp)
        assert is_valid is False
    
    def test_validate_input_zero_demand(self, algo):
        inp = AlgorithmInput("ITEM-001", 0.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        is_valid, _ = algo.validate_input(inp)
        assert is_valid is False
    
    # Ejecución
    def test_execute_basic(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        out = algo.execute(inp)
        assert out.success is True
        assert out.status == AlgorithmStatus.COMPLETED
        assert 0.0 <= out.confidence_score <= 1.0
    
    def test_execute_critical(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "CRITICAL")
        out = algo.execute(inp)
        assert out.success is True
        assert "optimal" in out.reasoning.lower() or "secuencia" in out.reasoning.lower()
    
    def test_execute_low_priority(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "LOW")
        out = algo.execute(inp)
        assert out.success is True
    
    # Decision
    def test_selected_option_valid(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        out = algo.execute(inp)
        valid_options = ["schedule_optimal", "schedule_feasible", "schedule_risky"]
        assert out.selected_option in valid_options
    
    # Telemetría
    def test_telemetry(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        out = algo.run(inp)
        assert out.execution_time_ms >= 0
        assert algo.execution_count > 0
    
    def test_metadata(self, algo):
        meta = algo.get_metadata()
        assert meta["type"] == "ctp_johnson"
        assert meta["execution_count"] >= 0
    
    # Edge cases
    def test_edge_case_high_demand(self, algo):
        inp = AlgorithmInput("ITEM-001", 1000.0, "2025-11-01", {"ITEM-001": 500.0}, "MEDIUM")
        out = algo.execute(inp)
        assert out.success is True
    
    def test_confidence_range(self, algo):
        for crit in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, crit)
            out = algo.execute(inp)
            assert 0.0 <= out.confidence_score <= 1.0
    
    def test_reasoning_completeness(self, algo):
        inp = AlgorithmInput("ITEM-001", 100.0, "2025-11-01", {"ITEM-001": 50.0}, "MEDIUM")
        out = algo.execute(inp)
        assert "Secuencia" in out.reasoning or "Makespan" in out.reasoning
