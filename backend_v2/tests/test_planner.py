"""
Tests unitarios para el servicio de planificación (PlannerService).

Verifica la funcionalidad de optimización de abastecimiento,
cálculo de lead times, sugerencias de proveedores, etc.
"""

import pytest
from datetime import datetime, timedelta
from services.planner_service import (
    PlannerService,
    get_planner_service
)
from core.ports.planner_port import (
    SourcingPath,
    OptimizationStrategy
)


class TestPlannerService:
    """Tests para PlannerService"""
    
    @pytest.fixture
    def planner_service(self):
        """Fixture que provee una instancia del servicio"""
        return PlannerService()
    
    # ==================== OPTIMIZE SOURCING OPTIONS ====================
    
    def test_optimize_sourcing_cost_strategy(self, planner_service):
        """Test optimización con estrategia de minimización de costos"""
        result = planner_service.optimize_sourcing_options(
            item_id="MAT-001",
            required_quantity=100.0,
            required_date=datetime.now() + timedelta(days=30),
            criticality="HIGH",
            strategy=OptimizationStrategy.COST_MINIMIZATION
        )
        
        assert result["success"] is True
        assert len(result["options"]) > 0
        assert result["recommended_option"] is not None
        assert "total_cost" in result
        assert "total_lead_time" in result
        assert "confidence_score" in result
        assert result["execution_time_ms"] > 0
        
        # Verificar que está ordenado por costo (menor primero)
        options = result["options"]
        if len(options) > 1:
            assert options[0]["total_cost"] <= options[1]["total_cost"]
    
    def test_optimize_sourcing_time_strategy(self, planner_service):
        """Test optimización con estrategia de minimización de tiempo"""
        result = planner_service.optimize_sourcing_options(
            item_id="MAT-002",
            required_quantity=50.0,
            required_date=datetime.now() + timedelta(days=7),
            criticality="CRITICAL",
            strategy=OptimizationStrategy.TIME_MINIMIZATION
        )
        
        assert result["success"] is True
        assert len(result["options"]) > 0
        
        # Verificar que está ordenado por lead time (menor primero)
        options = result["options"]
        if len(options) > 1:
            assert options[0]["lead_time_days"] <= options[1]["lead_time_days"]
    
    def test_optimize_sourcing_balanced_strategy(self, planner_service):
        """Test optimización con estrategia balanceada"""
        result = planner_service.optimize_sourcing_options(
            item_id="MAT-003",
            required_quantity=200.0,
            required_date=datetime.now() + timedelta(days=15),
            strategy=OptimizationStrategy.BALANCED
        )
        
        assert result["success"] is True
        assert len(result["options"]) > 0
        
        # Verificar que tiene balanced_score
        options = result["options"]
        if len(options) > 0:
            assert "balanced_score" in options[0]
    
    def test_optimize_sourcing_with_constraints(self, planner_service):
        """Test optimización con restricciones"""
        result = planner_service.optimize_sourcing_options(
            item_id="MAT-004",
            required_quantity=75.0,
            required_date=datetime.now() + timedelta(days=20),
            constraints={
                "max_cost": 10000.0,
                "max_lead_time": 30
            }
        )
        
        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"]["item_id"] == "MAT-004"
    
    # ==================== CALCULATE LEAD TIMES ====================
    
    def test_calculate_lead_times_stock_local(self, planner_service):
        """Test cálculo de lead times para stock local"""
        result = planner_service.calculate_lead_times(
            item_id="MAT-001",
            sourcing_path=SourcingPath.STOCK_LOCAL,
            service_level=0.95
        )
        
        assert "mean_days" in result
        assert "std_dev_days" in result
        assert "p50_days" in result
        assert "p95_days" in result
        assert "p99_days" in result
        assert result["mean_days"] <= 2  # Stock local es rápido
        assert result["p95_days"] >= result["p50_days"]
        assert result["p99_days"] >= result["p95_days"]
    
    def test_calculate_lead_times_purchase(self, planner_service):
        """Test cálculo de lead times para compra"""
        result = planner_service.calculate_lead_times(
            item_id="MAT-002",
            sourcing_path=SourcingPath.PURCHASE,
            service_level=0.95
        )
        
        assert result["mean_days"] >= 20  # Compra es más lento
        assert result["confidence_level"] > 0
        assert result["sample_size"] > 0
        assert "last_updated" in result
    
    def test_calculate_lead_times_default_path(self, planner_service):
        """Test cálculo de lead times sin especificar ruta"""
        result = planner_service.calculate_lead_times(
            item_id="MAT-003",
            service_level=0.99
        )
        
        assert result["mean_days"] > 0
        assert result["std_dev_days"] > 0
    
    # ==================== SUGGEST SUPPLIERS ====================
    
    def test_suggest_suppliers_success(self, planner_service):
        """Test sugerencia de proveedores exitosa"""
        result = planner_service.suggest_suppliers(
            item_id="MAT-001",
            required_quantity=100.0,
            max_suppliers=3
        )
        
        assert len(result) > 0
        assert len(result) <= 3
        
        # Verificar estructura de cada proveedor
        supplier = result[0]
        assert "supplier_id" in supplier
        assert "supplier_name" in supplier
        assert "unit_cost" in supplier
        assert "lead_time_days" in supplier
        assert "on_time_percentage" in supplier
        assert "quality_acceptance_rate" in supplier
        assert "ranking_score" in supplier
        assert "competitive_rank" in supplier
        
        # Verificar que está rankeado (rank 1 primero)
        assert supplier["competitive_rank"] == 1
    
    def test_suggest_suppliers_max_limit(self, planner_service):
        """Test que respeta el límite máximo de proveedores"""
        result = planner_service.suggest_suppliers(
            item_id="MAT-002",
            required_quantity=50.0,
            max_suppliers=2
        )
        
        assert len(result) <= 2
    
    def test_suggest_suppliers_ranking_criteria(self, planner_service):
        """Test sugerencia con criterios de ranking"""
        result = planner_service.suggest_suppliers(
            item_id="MAT-003",
            required_quantity=200.0,
            ranking_criteria=["cost", "lead_time", "quality"]
        )
        
        assert len(result) > 0
        # FASE 5.1: Criterios no implementados aún, solo verifica que no rompe
    
    # ==================== CHECK INVENTORY AVAILABILITY ====================
    
    def test_check_inventory_available(self, planner_service):
        """Test verificación de inventario disponible"""
        result = planner_service.check_inventory_availability(
            item_id="MAT-001",
            required_quantity=500.0
        )
        
        assert "available" in result
        assert result["available"] is True  # Simulación tiene 650 disponibles
        assert result["quantity_on_hand"] > 0
        assert result["quantity_available"] >= 500.0
        assert "warehouse_distribution" in result
        assert len(result["warehouse_distribution"]) > 0
        assert "lots" in result
        assert len(result["lots"]) > 0
    
    def test_check_inventory_insufficient(self, planner_service):
        """Test verificación con inventario insuficiente"""
        result = planner_service.check_inventory_availability(
            item_id="MAT-002",
            required_quantity=2000.0  # Más de lo disponible (650)
        )
        
        assert result["available"] is False
    
    def test_check_inventory_specific_warehouse(self, planner_service):
        """Test verificación en almacén específico"""
        result = planner_service.check_inventory_availability(
            item_id="MAT-003",
            required_quantity=100.0,
            warehouse_id="ALM-02"
        )
        
        assert "warehouse_distribution" in result
        warehouses = result["warehouse_distribution"]
        if len(warehouses) > 0:
            assert warehouses[0]["warehouse_id"] == "ALM-02"
    
    def test_check_inventory_with_quality_check(self, planner_service):
        """Test verificación con control de calidad"""
        result = planner_service.check_inventory_availability(
            item_id="MAT-004",
            required_quantity=100.0,
            check_quality=True
        )
        
        assert "lots" in result
        assert "expiration_alerts" in result
    
    # ==================== EVALUATE SUBSTITUTES ====================
    
    def test_evaluate_substitutes_success(self, planner_service):
        """Test evaluación de sustitutos exitosa"""
        result = planner_service.evaluate_substitutes(
            item_id="MAT-001",
            required_quantity=100.0,
            max_substitutes=2
        )
        
        assert len(result) > 0
        assert len(result) <= 2
        
        # Verificar estructura de cada sustituto
        substitute = result[0]
        assert "substitute_id" in substitute
        assert "substitute_code" in substitute
        assert "technical_match" in substitute
        assert "conversion_factor" in substitute
        assert "cost_differential" in substitute
        assert "availability" in substitute
        assert "recommendation_score" in substitute
    
    def test_evaluate_substitutes_min_technical_match(self, planner_service):
        """Test filtrado por coincidencia técnica mínima"""
        result = planner_service.evaluate_substitutes(
            item_id="MAT-002",
            required_quantity=50.0,
            min_technical_match=0.9
        )
        
        # Verificar que todos cumplen el mínimo
        for substitute in result:
            assert substitute["technical_match"] >= 0.9
    
    def test_evaluate_substitutes_no_results(self, planner_service):
        """Test cuando no hay sustitutos que cumplan criterios"""
        result = planner_service.evaluate_substitutes(
            item_id="MAT-003",
            required_quantity=100.0,
            min_technical_match=0.99  # Muy alto, filtra todos
        )
        
        # En simulación, ninguno supera 0.95, debería retornar vacío
        assert len(result) == 0
    
    # ==================== RUN ALGORITHM ====================
    
    def test_run_algorithm_reserve_dynamic(self, planner_service):
        """Test ejecución de algoritmo de reserva dinámica"""
        result = planner_service.run_algorithm(
            algorithm_type="reserve_dynamic",
            input_data={
                "item_id": "MAT-001",
                "required_quantity": 100.0
            }
        )
        
        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["algorithm_type"] == "reserve_dynamic"
        assert "result" in result
        assert "recommended_action" in result["result"]
        assert result["execution_time_ms"] > 0
    
    def test_run_algorithm_release_marginal(self, planner_service):
        """Test ejecución de algoritmo de liberación marginal"""
        result = planner_service.run_algorithm(
            algorithm_type="release_marginal_cost",
            input_data={
                "item_id": "MAT-002",
                "required_quantity": 50.0
            }
        )
        
        assert result["success"] is True
        assert result["status"] == "completed"
        assert "marginal_cost_release" in result["result"]
        assert "marginal_cost_maintain" in result["result"]
    
    def test_run_algorithm_purchase_multicriterion(self, planner_service):
        """Test ejecución de algoritmo de compra multicriterio"""
        result = planner_service.run_algorithm(
            algorithm_type="purchase_multicriterion",
            input_data={
                "item_id": "MAT-003",
                "required_quantity": 200.0
            }
        )
        
        assert result["success"] is True
        assert "recommended_supplier" in result["result"]
        assert "estimated_cost" in result["result"]
        assert "estimated_lead_time" in result["result"]
    
    def test_run_algorithm_unknown(self, planner_service):
        """Test ejecución de algoritmo desconocido"""
        result = planner_service.run_algorithm(
            algorithm_type="unknown_algorithm",
            input_data={"item_id": "MAT-004"}
        )
        
        assert result["success"] is False
        assert result["status"] == "failed"
        assert "error" in result["result"]
    
    # ==================== CALCULATE TOTAL COST ====================
    
    def test_calculate_total_cost_success(self, planner_service):
        """Test cálculo de costo total exitoso"""
        options = [
            {
                "unit_cost": 100.0,
                "transportation_cost": 10.0,
                "customs_cost": 5.0,
                "handling_cost": 8.0,
                "quantity": 50.0
            }
        ]
        
        result = planner_service.calculate_total_cost(
            sourcing_options=options,
            include_transportation=True,
            include_customs=True,
            include_handling=True
        )
        
        assert result["unit_cost"] == 100.0
        assert result["transportation_cost"] == 10.0
        assert result["customs_cost"] == 5.0
        assert result["handling_cost"] == 8.0
        assert result["total_cost_per_unit"] == 123.0
        assert result["total_cost"] == 123.0 * 50.0
    
    def test_calculate_total_cost_exclude_transportation(self, planner_service):
        """Test cálculo excluyendo transporte"""
        options = [
            {
                "unit_cost": 100.0,
                "transportation_cost": 10.0,
                "customs_cost": 5.0,
                "handling_cost": 8.0,
                "quantity": 10.0
            }
        ]
        
        result = planner_service.calculate_total_cost(
            sourcing_options=options,
            include_transportation=False
        )
        
        assert result["transportation_cost"] == 0.0
        assert result["total_cost_per_unit"] == 113.0  # Sin transporte
    
    def test_calculate_total_cost_empty_options(self, planner_service):
        """Test cálculo con lista vacía de opciones"""
        result = planner_service.calculate_total_cost(
            sourcing_options=[]
        )
        
        assert result["total_cost"] == 0.0
        assert result["unit_cost"] == 0.0
    
    # ==================== VALIDATE CAPACITY CONSTRAINTS ====================
    
    def test_validate_capacity_sufficient(self, planner_service):
        """Test validación de capacidad suficiente"""
        result = planner_service.validate_capacity_constraints(
            resource_id="PROV-001",
            required_capacity=5000.0,
            capacity_type="SUPPLIER_CAPACITY",
            time_window_start=datetime.now(),
            time_window_end=datetime.now() + timedelta(days=30)
        )
        
        assert result["constraint_satisfied"] is True
        assert result["available_capacity"] >= 5000.0
        assert 0 <= result["utilization_percentage"] <= 100
        assert "recommendation" in result
    
    def test_validate_capacity_insufficient(self, planner_service):
        """Test validación de capacidad insuficiente"""
        result = planner_service.validate_capacity_constraints(
            resource_id="PROV-002",
            required_capacity=15000.0,  # Más de 7000 disponibles
            capacity_type="WAREHOUSE_CAPACITY",
            time_window_start=datetime.now(),
            time_window_end=datetime.now() + timedelta(days=15)
        )
        
        assert result["constraint_satisfied"] is False
        assert result["available_capacity"] < 15000.0
        assert "earliest_available_date" in result
    
    def test_validate_capacity_utilization(self, planner_service):
        """Test cálculo de utilización de capacidad"""
        result = planner_service.validate_capacity_constraints(
            resource_id="PROV-003",
            required_capacity=1000.0,
            capacity_type="TRANSPORT_CAPACITY",
            time_window_start=datetime.now(),
            time_window_end=datetime.now() + timedelta(days=7)
        )
        
        assert "utilization_percentage" in result
        assert 0 <= result["utilization_percentage"] <= 100
    
    # ==================== SINGLETON ====================
    
    def test_get_planner_service_singleton(self):
        """Test que get_planner_service retorna singleton"""
        service1 = get_planner_service()
        service2 = get_planner_service()
        
        assert service1 is service2
        assert isinstance(service1, PlannerService)
