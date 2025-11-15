"""
Servicio de Planificación de Abastecimiento

Implementa PlannerPort para orquestar algoritmos de optimización
y proporcionar recomendaciones de abastecimiento.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from enum import Enum

from core.ports.planner_port import (
    PlannerPort,
    SourcingPath,
    OptimizationStrategy
)

# FASE 5.2: Importar algoritmos reales
# FASE 5.3: Importar 6 algoritmos restantes
from services.planner.algorithms import (
    AlgorithmType,
    AlgorithmInput,
    get_registry,
    get_executor,
    register_algorithm,
    get_reserve_dynamic_algorithm,
    get_purchase_multicriterion_algorithm,
    get_release_marginal_algorithm,
    get_disassembly_knapsack_algorithm,
    get_substitutes_graph_algorithm,
    get_ctp_johnson_algorithm,
    get_transfer_tdabc_algorithm,
    get_expedite_probability_algorithm
)

logger = logging.getLogger(__name__)


class PlannerService(PlannerPort):
    """
    Servicio de planificación que implementa algoritmos de optimización
    para sugerencias de abastecimiento.
    
    FASE 5.1: Implementación inicial con lógica básica.
    FASE 5.2: Integración con 2 algoritmos de ejemplo (Reserve, Purchase)
    FASE 5.3: Integración con 6 algoritmos restantes (Release, Disassembly, Substitutes, CTP, Transfer, Expedite)
    """
    
    def __init__(self):
        """Inicializa el servicio de planificación"""
        self.algorithms_cache = {}
        
        # FASE 5.2: Registrar algoritmos disponibles
        self.registry = get_registry()
        self.executor = get_executor()
        
        # Registrar algoritmos implementados (8 total)
        register_algorithm(get_reserve_dynamic_algorithm())
        register_algorithm(get_purchase_multicriterion_algorithm())
        
        # FASE 5.3: Registrar 6 algoritmos restantes
        register_algorithm(get_release_marginal_algorithm())
        register_algorithm(get_disassembly_knapsack_algorithm())
        register_algorithm(get_substitutes_graph_algorithm())
        register_algorithm(get_ctp_johnson_algorithm())
        register_algorithm(get_transfer_tdabc_algorithm())
        register_algorithm(get_expedite_probability_algorithm())
        
        logger.info(f"PlannerService inicializado con {len(self.registry.list_algorithms())} algoritmos")

    
    def optimize_sourcing_options(
        self,
        item_id: str,
        required_quantity: float,
        required_date: datetime,
        criticality: str = "MEDIUM",
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimiza opciones de abastecimiento para un material.
        
        FASE 5.1: Implementación simplificada con vías básicas.
        """
        start_time = datetime.now()
        constraints = constraints or {}
        
        try:
            # Generar opciones de abastecimiento
            options = self._generate_sourcing_options(
                item_id=item_id,
                required_quantity=required_quantity,
                required_date=required_date,
                criticality=criticality,
                strategy=strategy,
                constraints=constraints
            )
            
            # Rankear opciones según estrategia
            ranked_options = self._rank_options(options, strategy)
            
            # Seleccionar opción recomendada
            recommended = ranked_options[0] if ranked_options else None
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "options": ranked_options,
                "recommended_option": recommended,
                "total_cost": recommended.get("total_cost", 0.0) if recommended else 0.0,
                "total_lead_time": recommended.get("lead_time_days", 0) if recommended else 0,
                "confidence_score": recommended.get("confidence_score", 0.0) if recommended else 0.0,
                "execution_time_ms": execution_time,
                "metadata": {
                    "item_id": item_id,
                    "criticality": criticality,
                    "strategy": strategy.value,
                    "options_evaluated": len(ranked_options)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en optimize_sourcing_options: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "success": False,
                "options": [],
                "recommended_option": None,
                "total_cost": 0.0,
                "total_lead_time": 0,
                "confidence_score": 0.0,
                "execution_time_ms": execution_time,
                "metadata": {"error": str(e)}
            }
    
    def calculate_lead_times(
        self,
        item_id: str,
        supplier_id: Optional[str] = None,
        sourcing_path: Optional[SourcingPath] = None,
        service_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calcula lead times para un material según ruta de abastecimiento.
        
        FASE 5.1: Implementación con valores estimados.
        FASE 5.2: Integración con históricos reales.
        """
        # Lead times base por vía de abastecimiento (días)
        base_lead_times = {
            SourcingPath.STOCK_LOCAL: 1,
            SourcingPath.RELEASE: 2,
            SourcingPath.DISASSEMBLY: 5,
            SourcingPath.SUBSTITUTE: 3,
            SourcingPath.CTP: 7,
            SourcingPath.TRANSFER: 10,
            SourcingPath.EXPEDITE: 14,
            SourcingPath.PURCHASE: 30
        }
        
        # Determinar lead time base
        if sourcing_path:
            mean_days = base_lead_times.get(sourcing_path, 30)
        else:
            mean_days = 30  # Default: compra
        
        # Calcular variabilidad (20% del mean)
        std_dev_days = mean_days * 0.2
        
        # Calcular percentiles usando distribución normal simplificada
        # P50 = mediana ≈ mean
        p50_days = int(mean_days)
        
        # P95 ≈ mean + 1.645 * std_dev
        p95_days = int(mean_days + 1.645 * std_dev_days)
        
        # P99 ≈ mean + 2.326 * std_dev
        p99_days = int(mean_days + 2.326 * std_dev_days)
        
        return {
            "item_id": item_id,
            "mean_days": mean_days,
            "std_dev_days": std_dev_days,
            "p50_days": p50_days,
            "p95_days": p95_days,
            "p99_days": p99_days,
            "confidence_level": 0.85,  # Estimado por falta de históricos
            "sample_size": 10,  # Simulado
            "last_updated": datetime.now()
        }
    
    def suggest_suppliers(
        self,
        item_id: str,
        required_quantity: float,
        max_suppliers: int = 5,
        ranking_criteria: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Sugiere proveedores para un material basado en múltiples criterios.
        
        FASE 5.1: Proveedores simulados.
        FASE 5.2: Integración con catálogo real de proveedores.
        """
        # Proveedores simulados (FASE 5.1)
        suppliers = [
            {
                "supplier_id": "PROV-001",
                "supplier_name": "Proveedor Local A",
                "unit_cost": 100.0,
                "lead_time_days": 30,
                "on_time_percentage": 0.95,
                "quality_acceptance_rate": 0.98,
                "ranking_score": 0.92,
                "competitive_rank": 1
            },
            {
                "supplier_id": "PROV-002",
                "supplier_name": "Proveedor Regional B",
                "unit_cost": 95.0,
                "lead_time_days": 35,
                "on_time_percentage": 0.90,
                "quality_acceptance_rate": 0.96,
                "ranking_score": 0.88,
                "competitive_rank": 2
            },
            {
                "supplier_id": "PROV-003",
                "supplier_name": "Proveedor Internacional C",
                "unit_cost": 85.0,
                "lead_time_days": 45,
                "on_time_percentage": 0.85,
                "quality_acceptance_rate": 0.94,
                "ranking_score": 0.82,
                "competitive_rank": 3
            }
        ]
        
        # Filtrar por criterios de ranking si se especifican
        if ranking_criteria:
            # FASE 5.2: Implementar lógica de filtrado
            pass
        
        # Retornar top N proveedores
        return suppliers[:max_suppliers]
    
    def check_inventory_availability(
        self,
        item_id: str,
        required_quantity: float,
        warehouse_id: Optional[str] = None,
        include_reserved: bool = False,
        check_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidad de inventario para un material.
        
        FASE 5.1: Inventario simulado.
        FASE 5.2: Integración con sistema de inventario real.
        """
        # Simulación de inventario (FASE 5.1)
        quantity_on_hand = 1000.0
        quantity_reserved = 200.0
        quantity_allocated = 150.0
        quantity_available = quantity_on_hand - quantity_reserved - quantity_allocated
        
        available = quantity_available >= required_quantity
        
        return {
            "available": available,
            "quantity_on_hand": quantity_on_hand,
            "quantity_available": quantity_available,
            "quantity_reserved": quantity_reserved,
            "quantity_allocated": quantity_allocated,
            "warehouse_distribution": [
                {
                    "warehouse_id": warehouse_id or "ALM-01",
                    "quantity": quantity_on_hand
                }
            ],
            "lots": [
                {
                    "lot_number": "LOT-2025-001",
                    "quantity": quantity_on_hand,
                    "expiration_date": (datetime.now() + timedelta(days=180)).isoformat()
                }
            ],
            "expiration_alerts": []
        }
    
    def evaluate_substitutes(
        self,
        item_id: str,
        required_quantity: float,
        max_substitutes: int = 3,
        min_technical_match: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Evalúa materiales sustitutos para un ítem.
        
        FASE 5.1: Sustitutos simulados.
        FASE 5.2: Integración con catálogo de equivalencias.
        """
        # Sustitutos simulados (FASE 5.1)
        substitutes = [
            {
                "substitute_id": f"SUB-{item_id}-001",
                "substitute_code": f"ALT-{item_id}",
                "technical_match": 0.95,
                "conversion_factor": 1.0,
                "cost_differential": 0.05,  # +5% más caro
                "availability": {
                    "available": True,
                    "quantity": 500.0
                },
                "recommendation_score": 0.90
            },
            {
                "substitute_id": f"SUB-{item_id}-002",
                "substitute_code": f"ALT2-{item_id}",
                "technical_match": 0.85,
                "conversion_factor": 1.1,
                "cost_differential": -0.10,  # -10% más barato
                "availability": {
                    "available": True,
                    "quantity": 300.0
                },
                "recommendation_score": 0.82
            }
        ]
        
        # Filtrar por coincidencia técnica mínima
        filtered = [s for s in substitutes if s["technical_match"] >= min_technical_match]
        
        # Retornar top N sustitutos
        return filtered[:max_substitutes]
    
    def run_algorithm(
        self,
        algorithm_type: str,
        input_data: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un algoritmo específico de optimización.
        
        FASE 5.1: Algoritmos básicos.
        FASE 5.2+: Integración con algoritmos de v1.0
        """
        start_time = datetime.now()
        parameters = parameters or {}
        
        try:
            # Mapeo de algoritmos (FASE 5.1: simplificado)
            if algorithm_type == "reserve_dynamic":
                result = self._run_reserve_dynamic(input_data, parameters)
            elif algorithm_type == "release_marginal_cost":
                result = self._run_release_marginal(input_data, parameters)
            elif algorithm_type == "purchase_multicriterion":
                result = self._run_purchase_multicriterion(input_data, parameters)
            else:
                result = {"error": f"Algoritmo desconocido: {algorithm_type}"}
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "algorithm_type": algorithm_type,
                "success": "error" not in result,
                "status": "completed" if "error" not in result else "failed",
                "result": result,
                "execution_time_ms": execution_time,
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando algoritmo {algorithm_type}: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "algorithm_type": algorithm_type,
                "success": False,
                "status": "failed",
                "result": {"error": str(e)},
                "execution_time_ms": execution_time,
                "metadata": {}
            }
    
    def calculate_total_cost(
        self,
        sourcing_options: List[Dict[str, Any]],
        include_transportation: bool = True,
        include_customs: bool = True,
        include_handling: bool = True
    ) -> Dict[str, float]:
        """
        Calcula costo total de opciones de abastecimiento.
        
        FASE 5.1: Cálculo simplificado.
        """
        if not sourcing_options:
            return {
                "unit_cost": 0.0,
                "transportation_cost": 0.0,
                "customs_cost": 0.0,
                "handling_cost": 0.0,
                "total_cost_per_unit": 0.0,
                "total_cost": 0.0
            }
        
        # Tomar primera opción para cálculo
        option = sourcing_options[0]
        
        unit_cost = option.get("unit_cost", 0.0)
        transportation_cost = option.get("transportation_cost", 0.0) if include_transportation else 0.0
        customs_cost = option.get("customs_cost", 0.0) if include_customs else 0.0
        handling_cost = option.get("handling_cost", 0.0) if include_handling else 0.0
        
        total_cost_per_unit = unit_cost + transportation_cost + customs_cost + handling_cost
        quantity = option.get("quantity", 1.0)
        total_cost = total_cost_per_unit * quantity
        
        return {
            "unit_cost": unit_cost,
            "transportation_cost": transportation_cost,
            "customs_cost": customs_cost,
            "handling_cost": handling_cost,
            "total_cost_per_unit": total_cost_per_unit,
            "total_cost": total_cost
        }
    
    def validate_capacity_constraints(
        self,
        resource_id: str,
        required_capacity: float,
        capacity_type: str,
        time_window_start: datetime,
        time_window_end: datetime
    ) -> Dict[str, Any]:
        """
        Valida restricciones de capacidad de un recurso.
        
        FASE 5.1: Validación simulada.
        FASE 5.2: Integración con sistema de capacidades real.
        """
        # Capacidad simulada (FASE 5.1)
        total_capacity = 10000.0
        reserved_capacity = 3000.0
        available_capacity = total_capacity - reserved_capacity
        
        constraint_satisfied = available_capacity >= required_capacity
        utilization_percentage = (reserved_capacity / total_capacity) * 100
        
        return {
            "constraint_satisfied": constraint_satisfied,
            "available_capacity": available_capacity,
            "reserved_capacity": reserved_capacity,
            "utilization_percentage": utilization_percentage,
            "earliest_available_date": time_window_start if constraint_satisfied else time_window_end + timedelta(days=7),
            "recommendation": "Capacidad suficiente" if constraint_satisfied else "Considerar proveedor alternativo"
        }
    
    # ===================== MÉTODOS PRIVADOS =====================
    
    def _generate_sourcing_options(
        self,
        item_id: str,
        required_quantity: float,
        required_date: datetime,
        criticality: str,
        strategy: OptimizationStrategy,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Genera opciones de abastecimiento usando algoritmos reales.
        
        FASE 5.2: Integración con ReserveDynamic y PurchaseMulticriterion
        """
        options = []
        
        # Preparar input común para algoritmos
        algorithm_input = AlgorithmInput(
            item_id=item_id,
            demand_quantity=required_quantity,
            required_date=required_date.isoformat(),
            criticality=criticality,
            budget_available=constraints.get("max_budget", float('inf')),
            max_acceptable_cost=constraints.get("max_cost", float('inf'))
        )
        
        # 1. Intentar RESERVA DE STOCK LOCAL (si hay disponibilidad)
        inventory = self.check_inventory_availability(item_id, required_quantity)
        if inventory["available"]:
            # Agregar contexto de stock local al input
            algorithm_input.local_stock = {
                "warehouse_main": inventory["quantity_available"]
            }
            
            # Ejecutar algoritmo Reserve Dynamic
            try:
                reserve_output = self.executor.execute(
                    AlgorithmType.RESERVE_DYNAMIC,
                    algorithm_input
                )
                
                if reserve_output.success:
                    options.append({
                        "option_id": f"{item_id}:stock_local",
                        "sourcing_path": SourcingPath.STOCK_LOCAL.value,
                        "supplier_id": None,
                        "quantity": reserve_output.proposed_quantity,
                        "unit_cost": 0.0,  # Ya en inventario
                        "transportation_cost": 0.0,
                        "customs_cost": 0.0,
                        "handling_cost": 5.0,
                        "total_cost": 5.0 * reserve_output.proposed_quantity,
                        "lead_time_days": reserve_output.estimated_lead_time,
                        "on_time_percentage": 0.99,
                        "confidence_score": reserve_output.confidence_score,
                        "feasible": True,
                        "algorithm_output": {
                            "reasoning": reserve_output.reasoning,
                            "execution_time_ms": reserve_output.execution_time_ms
                        }
                    })
            except Exception as e:
                logger.warning(f"Reserve Dynamic falló: {e}")
        
        # 2. COMPRA A PROVEEDORES (siempre evaluar)
        try:
            purchase_output = self.executor.execute(
                AlgorithmType.PURCHASE_MULTICRITERION,
                algorithm_input
            )
            
            if purchase_output.success:
                options.append({
                    "option_id": f"{item_id}:purchase",
                    "sourcing_path": SourcingPath.PURCHASE.value,
                    "supplier_id": purchase_output.selected_option,
                    "quantity": purchase_output.proposed_quantity,
                    "unit_cost": purchase_output.estimated_cost / purchase_output.proposed_quantity if purchase_output.proposed_quantity > 0 else 0,
                    "transportation_cost": 10.0,
                    "customs_cost": 5.0,
                    "handling_cost": 8.0,
                    "total_cost": purchase_output.estimated_cost + (10.0 + 5.0 + 8.0) * purchase_output.proposed_quantity,
                    "lead_time_days": purchase_output.estimated_lead_time,
                    "on_time_percentage": 0.90,
                    "confidence_score": purchase_output.confidence_score,
                    "feasible": True,
                    "algorithm_output": {
                        "reasoning": purchase_output.reasoning,
                        "alternatives": purchase_output.alternatives_considered,
                        "execution_time_ms": purchase_output.execution_time_ms
                    }
                })
        except Exception as e:
            logger.warning(f"Purchase Multicriterion falló: {e}")
        
        # 3. SUSTITUTOS (FASE 5.3 - por ahora lógica simplificada)
        substitutes = self.evaluate_substitutes(item_id, required_quantity, max_substitutes=1)
        for substitute in substitutes:
            if substitute["availability"]["available"]:
                base_cost = 100.0 * (1 + substitute["cost_differential"])
                options.append({
                    "option_id": f"{item_id}:substitute:{substitute['substitute_id']}",
                    "sourcing_path": SourcingPath.SUBSTITUTE.value,
                    "supplier_id": None,
                    "substitute_id": substitute["substitute_id"],
                    "quantity": required_quantity * substitute["conversion_factor"],
                    "unit_cost": base_cost,
                    "transportation_cost": 0.0,
                    "customs_cost": 0.0,
                    "handling_cost": 5.0,
                    "total_cost": (base_cost + 5.0) * required_quantity * substitute["conversion_factor"],
                    "lead_time_days": 3,
                    "on_time_percentage": 0.95,
                    "confidence_score": substitute["recommendation_score"],
                    "feasible": True
                })
        
        return options
    
    def _rank_options(
        self,
        options: List[Dict[str, Any]],
        strategy: OptimizationStrategy
    ) -> List[Dict[str, Any]]:
        """Rankea opciones según estrategia de optimización"""
        if not options:
            return []
        
        if strategy == OptimizationStrategy.COST_MINIMIZATION:
            # Ordenar por costo total (menor primero)
            return sorted(options, key=lambda x: x["total_cost"])
        
        elif strategy == OptimizationStrategy.TIME_MINIMIZATION:
            # Ordenar por lead time (menor primero)
            return sorted(options, key=lambda x: x["lead_time_days"])
        
        elif strategy == OptimizationStrategy.BALANCED:
            # Score balanceado: (1 - norm_cost) * 0.5 + (1 - norm_time) * 0.3 + confidence * 0.2
            max_cost = max(o["total_cost"] for o in options)
            max_time = max(o["lead_time_days"] for o in options)
            
            for option in options:
                norm_cost = option["total_cost"] / max_cost if max_cost > 0 else 0
                norm_time = option["lead_time_days"] / max_time if max_time > 0 else 0
                option["balanced_score"] = (
                    (1 - norm_cost) * 0.5 +
                    (1 - norm_time) * 0.3 +
                    option["confidence_score"] * 0.2
                )
            
            return sorted(options, key=lambda x: x.get("balanced_score", 0), reverse=True)
        
        else:
            # Default: por confidence_score
            return sorted(options, key=lambda x: x["confidence_score"], reverse=True)
    
    def _run_reserve_dynamic(
        self,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Algoritmo de reserva dinámica de stock local"""
        item_id = input_data.get("item_id")
        required_quantity = input_data.get("required_quantity", 0.0)
        
        inventory = self.check_inventory_availability(item_id, required_quantity)
        
        return {
            "recommended_action": "reserve" if inventory["available"] else "escalate",
            "quantity_to_reserve": min(required_quantity, inventory["quantity_available"]),
            "confidence": 0.95 if inventory["available"] else 0.5,
            "inventory_snapshot": inventory
        }
    
    def _run_release_marginal(
        self,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Algoritmo de liberación de stock basado en costo marginal"""
        item_id = input_data.get("item_id")
        required_quantity = input_data.get("required_quantity", 0.0)
        
        # Simulación: costo de oportunidad de liberar vs. mantener
        marginal_cost_release = 50.0
        marginal_cost_maintain = 60.0
        
        return {
            "recommended_action": "release" if marginal_cost_release < marginal_cost_maintain else "maintain",
            "quantity_to_release": required_quantity if marginal_cost_release < marginal_cost_maintain else 0.0,
            "marginal_cost_release": marginal_cost_release,
            "marginal_cost_maintain": marginal_cost_maintain,
            "confidence": 0.85
        }
    
    def _run_purchase_multicriterion(
        self,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Algoritmo de compra multicriterio"""
        item_id = input_data.get("item_id")
        required_quantity = input_data.get("required_quantity", 0.0)
        
        suppliers = self.suggest_suppliers(item_id, required_quantity, max_suppliers=3)
        
        if not suppliers:
            return {"error": "No hay proveedores disponibles"}
        
        # Seleccionar mejor proveedor (ya rankeado)
        best_supplier = suppliers[0]
        
        return {
            "recommended_supplier": best_supplier["supplier_id"],
            "supplier_name": best_supplier["supplier_name"],
            "quantity_to_purchase": required_quantity,
            "estimated_cost": best_supplier["unit_cost"] * required_quantity,
            "estimated_lead_time": best_supplier["lead_time_days"],
            "confidence": best_supplier["ranking_score"],
            "alternative_suppliers": suppliers[1:] if len(suppliers) > 1 else []
        }


# Instancia singleton del servicio
_planner_service_instance = None


def get_planner_service() -> PlannerService:
    """
    Retorna instancia singleton del servicio de planificación.
    
    Returns:
        PlannerService: Instancia del servicio
    """
    global _planner_service_instance
    if _planner_service_instance is None:
        _planner_service_instance = PlannerService()
    return _planner_service_instance
