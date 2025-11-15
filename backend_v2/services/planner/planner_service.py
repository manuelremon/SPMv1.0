"""
Backend v2.0 - Planner Service
Orquesta múltiples algoritmos para generar recomendaciones de aprovisionamiento
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from services.planner.algorithms import (
    get_reserve_dynamic_algorithm,
    get_purchase_multicriterion_algorithm,
    get_release_marginal_algorithm,  # Nombre correcto
    get_transfer_tdabc_algorithm,
    get_ctp_johnson_algorithm,
    get_disassembly_knapsack_algorithm,
    get_expedite_probability_algorithm,
    get_substitutes_graph_algorithm
)
from services.planner.algorithms.base_algorithm import (
    AlgorithmInput,
    AlgorithmOutput,
    AlgorithmType
)


class PlannerService:
    """
    Servicio principal del módulo planner.
    
    Responsabilidades:
    1. Ejecutar múltiples algoritmos de aprovisionamiento
    2. Consolidar recomendaciones
    3. Calcular scoring y confianza
    4. Generar plan de acción
    """
    
    def __init__(self):
        """Inicializa servicio con todos los algoritmos"""
        self.algorithms = {
            AlgorithmType.RESERVE_DYNAMIC: get_reserve_dynamic_algorithm(),
            AlgorithmType.PURCHASE_MULTICRITERION: get_purchase_multicriterion_algorithm(),
            AlgorithmType.RELEASE_MARGINAL_COST: get_release_marginal_algorithm(),  # Liberación
            AlgorithmType.TRANSFER_TDABC: get_transfer_tdabc_algorithm(),
            AlgorithmType.CTP_JOHNSON: get_ctp_johnson_algorithm(),
            AlgorithmType.DISASSEMBLY_KNAPSACK: get_disassembly_knapsack_algorithm(),
            AlgorithmType.EXPEDITE_PROBABILITY: get_expedite_probability_algorithm(),
            AlgorithmType.SUBSTITUTES_GRAPH: get_substitutes_graph_algorithm()
        }
    
    def analyze_sourcing_options(
        self,
        item_id: str,
        demand_quantity: float,
        required_date: datetime,
        criticality: str = "MEDIUM",
        budget_limit: Optional[float] = None,
        db_session: Optional[Session] = None
    ) -> Dict:
        """
        Analiza opciones de aprovisionamiento para un item.
        
        Args:
            item_id: ID del item a aprovisionar
            demand_quantity: Cantidad demandada
            required_date: Fecha requerida
            criticality: Nivel de criticidad (CRITICAL, HIGH, MEDIUM, LOW)
            budget_limit: Límite presupuestario opcional
            db_session: Sesión de base de datos (None = usar datos simulados)
        
        Returns:
            Dict con:
                - recommendations: List[Dict] de recomendaciones por algoritmo
                - best_option: Dict con mejor opción
                - total_cost_range: Dict con rango de costos
                - execution_time: float segundos
        """
        start_time = datetime.now()
        
        # Crear input común para todos los algoritmos
        algorithm_input = AlgorithmInput(
            item_id=item_id,
            demand_quantity=demand_quantity,
            required_date=required_date,
            criticality=criticality,
            budget_available=budget_limit if budget_limit is not None else float('inf'),
            db_session=db_session
        )
        
        # Ejecutar todos los algoritmos
        results = []
        for algo_type, algorithm in self.algorithms.items():
            output = algorithm.execute(algorithm_input)
            # Incluir todos los resultados, incluso los fallidos
            results.append({
                "algorithm": algo_type.value,
                "proposed_quantity": output.proposed_quantity,
                "estimated_cost": output.estimated_cost,
                "confidence_score": output.confidence_score if output.success else 0.0,
                "reasoning": output.reasoning,
                "selected_option": output.selected_option,
                "status": output.status.value
            })
        
        # Determinar mejor opción (mayor confidence_score)
        best_option = max(results, key=lambda x: x["confidence_score"]) if results else None
        
        # Calcular rango de costos
        costs = [r["estimated_cost"] for r in results if r["estimated_cost"] > 0]
        cost_range = {
            "min": min(costs) if costs else 0.0,
            "max": max(costs) if costs else 0.0,
            "avg": sum(costs) / len(costs) if costs else 0.0
        }
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "item_id": item_id,
            "demand_quantity": demand_quantity,
            "required_date": required_date.isoformat(),
            "criticality": criticality,
            "recommendations": results,
            "best_option": best_option,
            "total_cost_range": cost_range,
            "algorithms_executed": len(results),
            "execution_time_seconds": round(execution_time, 3),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_single_algorithm(
        self,
        algorithm_type: AlgorithmType,
        item_id: str,
        demand_quantity: float,
        required_date: datetime,
        criticality: str = "MEDIUM",
        db_session: Optional[Session] = None
    ) -> AlgorithmOutput:
        """
        Ejecuta un algoritmo específico.
        
        Args:
            algorithm_type: Tipo de algoritmo a ejecutar
            item_id: ID del item
            demand_quantity: Cantidad demandada
            required_date: Fecha requerida
            criticality: Nivel de criticidad
            db_session: Sesión de DB opcional
        
        Returns:
            AlgorithmOutput con resultado del algoritmo
        """
        if algorithm_type not in self.algorithms:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
        
        algorithm_input = AlgorithmInput(
            item_id=item_id,
            demand_quantity=demand_quantity,
            required_date=required_date,
            criticality=criticality,
            db_session=db_session
        )
        
        return self.algorithms[algorithm_type].execute(algorithm_input)
    
    def get_available_algorithms(self) -> List[str]:
        """Retorna lista de algoritmos disponibles"""
        return [algo_type.name for algo_type in self.algorithms.keys()]


def get_planner_service() -> PlannerService:
    """Factory function para obtener instancia del servicio"""
    return PlannerService()
