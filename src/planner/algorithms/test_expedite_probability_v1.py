"""Tests para ExpediteProbabilityAlgorithm (10 tests mínimales)"""
import pytest
from datetime import datetime, timedelta
from .expedite_probability import ExpediteProbabilityAlgorithm
from .base_algorithm import AlgorithmInput, AlgorithmStatus

@pytest.fixture
def algo():
    return ExpediteProbabilityAlgorithm()

@pytest.fixture
def valid_input():
    return AlgorithmInput(
        item_id="ITEM-001",
        demand_quantity=100,
        current_stock=20,
        required_date=datetime.now() + timedelta(days=5),
        criticality="HIGH"
    )

class TestExpediteProbability:
    
    def test_validate_missing_item_id(self, algo):
        inp = AlgorithmInput(item_id="", demand_quantity=100, required_date=datetime.now())
        valid, msg = algo.validate_input(inp)
        assert not valid
    
    def test_validate_negative_demand(self, algo):
        inp = AlgorithmInput(item_id="ITEM", demand_quantity=-5, required_date=datetime.now())
        valid, msg = algo.validate_input(inp)
        assert not valid
    
    def test_validate_missing_required_date(self, algo):
        inp = AlgorithmInput(item_id="ITEM", demand_quantity=100, required_date=None)
        valid, msg = algo.validate_input(inp)
        assert not valid
    
    def test_validate_valid_input(self, algo, valid_input):
        valid, msg = algo.validate_input(valid_input)
        assert valid
    
    def test_execute_critical_high(self, algo, valid_input):
        valid_input.criticality = "CRITICAL"
        output = algo.execute(valid_input)
        assert output.success
        assert output.status == AlgorithmStatus.COMPLETED
        assert output.selected_option == "EXPEDITE_FULL"
        assert output.proposed_quantity > 0
    
    def test_execute_medium_priority(self, algo, valid_input):
        valid_input.criticality = "MEDIUM"
        valid_input.required_date = datetime.now() + timedelta(days=8)
        output = algo.execute(valid_input)
        assert output.success
        assert output.selected_option == "EXPEDITE_PARTIAL"
    
    def test_execute_low_priority(self, algo, valid_input):
        valid_input.criticality = "LOW"
        output = algo.execute(valid_input)
        assert output.success
        assert output.selected_option == "EXPEDITE_NONE"
    
    def test_confidence_range(self, algo, valid_input):
        output = algo.execute(valid_input)
        assert 0.0 <= output.confidence_score <= 1.0
    
    def test_execution_history(self, algo, valid_input):
        algo.execute(valid_input)
        assert algo.execution_count >= 1
    
    def test_metadata(self, algo):
        metadata = algo.get_metadata()
        assert "algorithm_type" in metadata
        assert "name" in metadata
        assert metadata["name"] == "ExpediteProbabilityAlgorithm"
