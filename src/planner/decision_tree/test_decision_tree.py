"""
test_decision_tree.py
Test suite para Árbol de Decisión de Abastecimiento

Tests:
- Creación y estructura de nodos
- Evaluación de gates
- Ejecución de árbol (individual y batch)
- Evaluación de caminos
- Gate manager
- Integration tests
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.planner.decision_tree.decision_tree import (
    SourceRoute, GateType, Gate, DecisionNode, ExecutionPath,
    DecisionTreeBuilder, create_standard_decision_tree
)
from src.planner.decision_tree.execution_engine import (
    ExecutionContext, DecisionTreeExecutor
)
from src.planner.decision_tree.path_evaluator import PathEvaluator, FeasibilityMetric
from src.planner.decision_tree.gate_manager import GateManager, GateConfiguration, GateState


class TestDecisionTreeBasics:
    """Tests de estructura básica del árbol"""
    
    def test_source_route_enum(self):
        """Verifica que existan 12 rutas operativas"""
        routes = [r for r in SourceRoute]
        assert len(routes) == 12
        assert SourceRoute.STOCK_LOCAL.value == 1
        assert SourceRoute.FINAL_RESULT.value == 12
    
    def test_gate_type_enum(self):
        """Verifica que existan 9 tipos de gates"""
        types = [t for t in GateType]
        assert len(types) == 9
        assert GateType.AVAILABILITY in GateType
        assert GateType.COMPLEX in GateType
    
    def test_gate_creation(self):
        """Crea una puerta y verifica estructura"""
        def test_condition(ctx):
            return ctx.local_stock_available > 0
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test gate",
            condition_func=test_condition,
            threshold=0.0
        )
        
        assert gate.gate_id == "gate_001"
        assert gate.gate_type == GateType.AVAILABILITY
        assert gate.threshold == 0.0
    
    def test_decision_node_creation(self):
        """Crea nodo de decisión y verifica estructura"""
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=lambda ctx: True
        )
        
        node = DecisionNode(
            node_id="node_001",
            route=SourceRoute.STOCK_LOCAL,
            name="Stock Local",
            description="Reserva stock local",
            gates=[gate],
            estimated_lead_time_days=1,
            estimated_cost=0.0,
            estimated_success_rate=0.95
        )
        
        assert node.node_id == "node_001"
        assert node.route == SourceRoute.STOCK_LOCAL
        assert len(node.gates) == 1
        assert node.estimated_lead_time_days == 1
    
    def test_execution_path_creation(self):
        """Crea execution path y verifica estructura"""
        path = ExecutionPath(
            path_id="path_001",
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=datetime.now() + timedelta(days=5)
        )
        
        assert path.path_id == "path_001"
        assert path.item_id == "MAT001"
        assert path.demand_quantity == 100.0
        assert len(path.visited_nodes) == 0
        assert path.final_success is False


class TestGateEvaluation:
    """Tests de evaluación de gates"""
    
    def _create_context(self, **kwargs) -> ExecutionContext:
        """Helper para crear contexto con defaults"""
        defaults = {
            "item_id": "MAT001",
            "demand_quantity": 100.0,
            "required_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "local_stock_available": 50.0,
            "local_assets_available": 0.0,
            "bom_components_available": {},
            "substitutes_available": [],
            "transfer_centers_available": {},
            "intercompany_available": False,
            "vmi_contract_active": False,
            "loan_partner_available": False,
            "days_to_deadline": 5,
            "can_expedite": False,
            "expedite_budget_available": 0.0,
            "supplier_available": True,
            "supplier_lead_time_days": 10,
            "criticality": "MEDIUM",
            "budget_available": 1000.0,
            "max_acceptable_cost": 900.0
        }
        defaults.update(kwargs)
        return ExecutionContext(**defaults)
    
    def test_gate_evaluate_true(self):
        """Evalúa gate que retorna True"""
        def condition(ctx):
            return ctx.local_stock_available > 0
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=condition
        )
        
        context = self._create_context(local_stock_available=50.0)
        result = gate.evaluate(context)
        
        assert result is True
    
    def test_gate_evaluate_false(self):
        """Evalúa gate que retorna False"""
        def condition(ctx):
            return ctx.local_stock_available > 100
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=condition
        )
        
        context = self._create_context(local_stock_available=50.0)
        result = gate.evaluate(context)
        
        assert result is False
    
    def test_node_evaluate_gates_all_pass(self):
        """Evalúa nodo con múltiples gates que pasan"""
        gates = [
            Gate(
                gate_id="gate_001",
                gate_type=GateType.AVAILABILITY,
                description="Availability",
                condition_func=lambda ctx: ctx.local_stock_available > 0
            ),
            Gate(
                gate_id="gate_002",
                gate_type=GateType.COST,
                description="Cost",
                condition_func=lambda ctx: ctx.budget_available > 500
            )
        ]
        
        node = DecisionNode(
            node_id="node_001",
            route=SourceRoute.STOCK_LOCAL,
            name="Stock Local",
            description="Test",
            gates=gates,
            estimated_lead_time_days=1,
            estimated_cost=0.0,
            estimated_success_rate=0.95
        )
        
        context = self._create_context(
            local_stock_available=50.0,
            budget_available=1000.0
        )
        
        all_pass, failed_ids = node.evaluate_gates(context)
        
        assert all_pass is True
        assert len(failed_ids) == 0
    
    def test_node_evaluate_gates_some_fail(self):
        """Evalúa nodo con algún gate que falla"""
        gates = [
            Gate(
                gate_id="gate_001",
                gate_type=GateType.AVAILABILITY,
                description="Availability",
                condition_func=lambda ctx: ctx.local_stock_available > 100  # Fail
            ),
            Gate(
                gate_id="gate_002",
                gate_type=GateType.COST,
                description="Cost",
                condition_func=lambda ctx: ctx.budget_available > 500  # Pass
            )
        ]
        
        node = DecisionNode(
            node_id="node_001",
            route=SourceRoute.STOCK_LOCAL,
            name="Stock Local",
            description="Test",
            gates=gates,
            estimated_lead_time_days=1,
            estimated_cost=0.0,
            estimated_success_rate=0.95
        )
        
        context = self._create_context(
            local_stock_available=50.0,
            budget_available=1000.0
        )
        
        all_pass, failed_ids = node.evaluate_gates(context)
        
        assert all_pass is False
        assert "gate_001" in failed_ids
        assert "gate_002" not in failed_ids


class TestDecisionTreeBuilder:
    """Tests del constructor de árbol"""
    
    def test_create_standard_tree(self):
        """Crea árbol estándar y verifica estructura"""
        builder = create_standard_decision_tree()
        root = builder.build()
        
        assert root is not None
        assert root.node_id == "node_1"
        assert root.route == SourceRoute.STOCK_LOCAL
        
        # Verificar que está conectado
        assert root.next_on_success is not None or root.next_on_failure is not None
    
    def test_standard_tree_12_nodes(self):
        """Verifica que árbol estándar tiene 12 nodos"""
        builder = create_standard_decision_tree()
        all_nodes = builder.get_all_nodes()
        
        assert len(all_nodes) == 12
        
        # Verificar IDs
        for i in range(1, 13):
            assert f"node_{i}" in all_nodes
    
    def test_tree_navigation(self):
        """Navega árbol desde raíz hasta terminal"""
        builder = create_standard_decision_tree()
        root = builder.build()
        
        current = root
        visited_routes = [current.route]
        
        # Navegar hasta nodo 12
        depth = 0
        while current and depth < 12:
            if current.next_on_success:
                current = current.next_on_success
            elif current.next_on_failure:
                current = current.next_on_failure
            else:
                break
            
            visited_routes.append(current.route)
            depth += 1
        
        assert SourceRoute.FINAL_RESULT in visited_routes
        assert len(visited_routes) > 1


class TestExecutionEngine:
    """Tests del motor de ejecución"""
    
    def _create_context(self, **kwargs) -> ExecutionContext:
        """Helper para crear contexto con defaults"""
        defaults = {
            "item_id": "MAT001",
            "demand_quantity": 100.0,
            "required_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "local_stock_available": 50.0,
            "local_assets_available": 0.0,
            "bom_components_available": {},
            "substitutes_available": [],
            "transfer_centers_available": {},
            "intercompany_available": False,
            "vmi_contract_active": False,
            "loan_partner_available": False,
            "days_to_deadline": 5,
            "can_expedite": False,
            "expedite_budget_available": 0.0,
            "supplier_available": True,
            "supplier_lead_time_days": 10,
            "criticality": "MEDIUM",
            "budget_available": 1000.0,
            "max_acceptable_cost": 900.0
        }
        defaults.update(kwargs)
        return ExecutionContext(**defaults)
    
    def test_executor_initialize(self):
        """Inicializa executor con árbol estándar"""
        executor = DecisionTreeExecutor()
        assert executor is not None
    
    def test_execute_single_context(self):
        """Ejecuta árbol con un contexto"""
        executor = DecisionTreeExecutor()
        context = self._create_context(local_stock_available=100.0)
        
        path = executor.execute(context)
        
        assert path is not None
        assert path.item_id == "MAT001"
        assert len(path.visited_nodes) > 0
        assert path.final_route is not None
    
    def test_execute_batch(self):
        """Ejecuta batch de contextos"""
        executor = DecisionTreeExecutor()
        contexts = [
            self._create_context(item_id=f"MAT{i:03d}", local_stock_available=50+i)
            for i in range(5)
        ]
        
        paths = executor.execute_batch(contexts)
        
        assert len(paths) == 5
        assert all(p.final_route is not None for p in paths)
    
    def test_execution_statistics(self):
        """Calcula estadísticas de ejecución"""
        executor = DecisionTreeExecutor()
        contexts = [
            self._create_context(item_id=f"MAT{i:03d}", local_stock_available=50+i)
            for i in range(10)
        ]
        paths = executor.execute_batch(contexts)
        
        stats = executor.get_execution_statistics(paths)
        
        assert stats['total_executions'] == 10
        assert 'success_rate' in stats
        assert 'avg_lead_time' in stats
        assert 'avg_cost' in stats
        assert 'routes_used' in stats


class TestPathEvaluator:
    """Tests del evaluador de caminos"""
    
    def test_evaluator_initialize(self):
        """Inicializa evaluador con perfiles estándar"""
        evaluator = PathEvaluator()
        assert evaluator is not None
        assert len(evaluator.route_profiles) == 12
    
    def test_evaluate_path_full_feasibility(self):
        """Evalúa camino con viabilidad completa"""
        evaluator = PathEvaluator()
        
        path = ExecutionPath(
            path_id="path_001",
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=datetime.now() + timedelta(days=5),
            final_success=True,
            final_route=SourceRoute.STOCK_LOCAL,
            total_lead_time=2,
            total_cost=500.0,
            selected_source="LOCAL"
        )
        
        score = evaluator.evaluate_path(
            path,
            required_date=datetime.now() + timedelta(days=5),
            max_budget=1000.0,
            criticality="medium"
        )
        
        assert score.composite_score >= 0.0
        assert score.composite_score <= 1.0
        assert score.feasibility_level in ["FULL", "PARTIAL", "MARGINAL", "INFEASIBLE"]
    
    def test_compare_paths(self):
        """Compara múltiples caminos"""
        evaluator = PathEvaluator()
        
        paths = [
            ExecutionPath(
                path_id="path_001",
                item_id="MAT001",
                demand_quantity=100.0,
                required_date=datetime.now() + timedelta(days=5),
                final_success=True,
                final_route=SourceRoute.STOCK_LOCAL,
                total_lead_time=1,
                total_cost=400.0,
                selected_source="LOCAL"
            ),
            ExecutionPath(
                path_id="path_002",
                item_id="MAT001",
                demand_quantity=100.0,
                required_date=datetime.now() + timedelta(days=5),
                final_success=True,
                final_route=SourceRoute.PURCHASE,
                total_lead_time=7,
                total_cost=600.0,
                selected_source="SUPPLIER"
            )
        ]
        
        best_path, best_score, all_scores = evaluator.compare_paths(
            paths,
            required_date=datetime.now() + timedelta(days=5),
            max_budget=1000.0,
            criticality="medium"
        )
        
        assert best_path is not None
        assert best_score >= 0.0
        assert len(all_scores) == 2
    
    def test_rank_paths(self):
        """Rankea múltiples caminos"""
        evaluator = PathEvaluator()
        
        paths = [
            ExecutionPath(
                path_id=f"path_{i:03d}",
                item_id="MAT001",
                demand_quantity=100.0,
                required_date=datetime.now() + timedelta(days=5),
                final_success=True,
                final_route=SourceRoute.STOCK_LOCAL,
                total_lead_time=i,
                total_cost=400.0 + i*50,
                selected_source="LOCAL"
            )
            for i in range(5)
        ]
        
        ranked = evaluator.rank_paths(
            paths,
            required_date=datetime.now() + timedelta(days=5),
            max_budget=1500.0,
            criticality="medium"
        )
        
        assert len(ranked) == 5
        assert ranked[0][2] == 1  # First rank
        assert ranked[-1][2] == 5  # Last rank


class TestGateManager:
    """Tests del manager de gates"""
    
    def test_manager_initialize(self):
        """Inicializa manager de gates"""
        manager = GateManager()
        assert manager is not None
        assert len(manager.gates) == 0
    
    def test_register_gate(self):
        """Registra una puerta"""
        manager = GateManager()
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=lambda ctx: True
        )
        
        manager.register_gate(gate)
        
        assert "gate_001" in manager.gates
        assert "gate_001" in manager.configurations
    
    def test_evaluate_gate(self):
        """Evalúa una puerta a través del manager"""
        manager = GateManager()
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=lambda ctx: ctx.local_stock_available > 0
        )
        
        manager.register_gate(gate)
        
        context = ExecutionContext(
            item_id="MAT001",
            demand_quantity=100.0,
            required_date=(datetime.now() + timedelta(days=5)).isoformat(),
            local_stock_available=50.0,
            local_assets_available=0.0,
            bom_components_available={},
            substitutes_available=[],
            transfer_centers_available={},
            intercompany_available=False,
            vmi_contract_active=False,
            loan_partner_available=False,
            days_to_deadline=5,
            can_expedite=False,
            expedite_budget_available=0.0,
            supplier_available=True,
            supplier_lead_time_days=10,
            criticality="MEDIUM",
            budget_available=1000.0,
            max_acceptable_cost=900.0
        )
        
        result, evaluation = manager.evaluate_gate("gate_001", context)
        
        assert result is True
        assert evaluation.gate_id == "gate_001"
        assert evaluation.state == GateState.OPEN
    
    def test_get_gate_statistics(self):
        """Obtiene estadísticas de un gate"""
        manager = GateManager()
        
        gate = Gate(
            gate_id="gate_001",
            gate_type=GateType.AVAILABILITY,
            description="Test",
            condition_func=lambda ctx: ctx.local_stock_available > 0
        )
        
        manager.register_gate(gate)
        
        stats = manager.get_gate_statistics("gate_001")
        
        assert stats['gate_id'] == "gate_001"
        assert 'pass_rate' in stats
        assert 'total_evaluations' in stats


class TestIntegration:
    """Tests de integración entre componentes"""
    
    def test_end_to_end_execution(self):
        """Test E2E: Crear árbol → Ejecutar → Evaluar → Rankear"""
        # 1. Crear árbol
        builder = create_standard_decision_tree()
        
        # 2. Crear executor
        executor = DecisionTreeExecutor(builder)
        
        # 3. Ejecutar batch
        contexts = [
            ExecutionContext(
                item_id=f"MAT{i:03d}",
                demand_quantity=100.0,
                required_date=(datetime.now() + timedelta(days=5)).isoformat(),
                local_stock_available=50.0 + i*10,
                local_assets_available=0.0,
                bom_components_available={},
                substitutes_available=[],
                transfer_centers_available={},
                intercompany_available=False,
                vmi_contract_active=False,
                loan_partner_available=False,
                days_to_deadline=5,
                can_expedite=False,
                expedite_budget_available=0.0,
                supplier_available=True,
                supplier_lead_time_days=10,
                criticality="MEDIUM",
                budget_available=1000.0,
                max_acceptable_cost=900.0
            )
            for i in range(5)
        ]
        
        paths = executor.execute_batch(contexts)
        
        # 4. Evaluar
        evaluator = PathEvaluator()
        ranked = evaluator.rank_paths(
            paths,
            datetime.now() + timedelta(days=5),
            1000.0,
            "medium"
        )
        
        assert len(ranked) == 5
        assert ranked[0][2] == 1


class TestSmokeTests:
    """Smoke tests - verificaciones rápidas"""
    
    def test_imports(self):
        """Verifica que todos los imports funcionan"""
        from src.planner.decision_tree.decision_tree import (
            SourceRoute, GateType, Gate, DecisionNode, ExecutionPath,
            DecisionTreeBuilder, create_standard_decision_tree
        )
        from src.planner.decision_tree.execution_engine import (
            ExecutionContext, DecisionTreeExecutor
        )
        from src.planner.decision_tree.path_evaluator import (
            PathEvaluator, FeasibilityScore
        )
        from src.planner.decision_tree.gate_manager import (
            GateManager, GateConfiguration
        )
        assert True
    
    def test_standard_tree_creates(self):
        """Verifica que árbol estándar se crea sin errores"""
        builder = create_standard_decision_tree()
        root = builder.build()
        assert root is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
