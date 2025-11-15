"""
Algoritmo: Transferencias (TDABC - Time-Driven ABC)

Responsabilidades:
- Buscar en ubicaciones alternas usando TDABC
- Calcular costo de transferencia dinámico por actividad
- Optimizar ruta considerando lead time vs. costo

Complejidad: O(n) - actividades y almacenes
Estrategia: Time-driven costing: tiempo × rate por actividad
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


@dataclass
class Warehouse:
    """Almacén alternativo para transferencia"""
    warehouse_id: str
    location: str
    available_qty: float
    distance_km: float
    lead_time_days: float
    stock_reliability: float


@dataclass
class Activity:
    """Actividad en proceso de transferencia"""
    activity_name: str
    duration_hours: float
    cost_per_hour: float


@dataclass
class TransferAnalysis:
    """Análisis de alternativas de transferencia"""
    selected_warehouse: str
    transfer_quantity: float
    total_transfer_cost: float
    lead_time: float
    cost_per_unit: float
    reliability_score: float
    total_activity_cost: float


class TransferTDABCAlgorithm(BaseAlgorithm):
    """Time-Driven ABC para optimizar transferencias
    
    Costo = Σ(tiempo_actividad × rate_actividad)
    Decisión: basada en trade-off costo vs. lead time
    """
    
    def __init__(self):
        super().__init__(AlgorithmType.TRANSFER_TDABC)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida entrada de transferencia"""
        if not input_data.item_id:
            return False, "item_id requerido"
        if input_data.demand_quantity <= 0:
            return False, "demand_quantity debe ser > 0"
        return True, "OK"
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """Ejecuta análisis TDABC (7 pasos)"""
        try:
            # 1. Construir lista de almacenes disponibles
            if input_data.db_session:
                warehouses = self._fetch_warehouses_from_db(
                    input_data.db_session,
                    input_data.item_id,
                    input_data.demand_quantity
                )
            else:
                warehouses = self._build_warehouse_network(input_data)
            
            # 2. Definir actividades de transferencia (TDABC)
            activities = self._define_transfer_activities(input_data.criticality)
            
            # 3. Evaluar cada alternativa
            best_transfer = self._evaluate_transfer_options(
                warehouses, activities, input_data.demand_quantity
            )
            
            # 4. Calcular costo TDABC detallado
            analysis = self._calculate_tdabc_analysis(best_transfer, activities)
            
            # 5. Determinar decisión
            transfer_decision = self._determine_transfer_decision(analysis)
            
            # 6. Generar reasoning
            reasoning = self._generate_reasoning(analysis, transfer_decision)
            
            # 7. Calcular confidence
            confidence = min(
                analysis.reliability_score * 0.5 +
                (1.0 - min(analysis.lead_time / 10.0, 1.0)) * 0.3 +
                (100.0 - min(analysis.cost_per_unit / 50.0 * 100, 100.0)) / 100.0 * 0.2,
                1.0
            )
            confidence = max(0.0, confidence)
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.TRANSFER_TDABC,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=transfer_decision,
                proposed_quantity=analysis.transfer_quantity,
                estimated_cost=analysis.total_transfer_cost,
                confidence_score=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error en TransferTDABCAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.TRANSFER_TDABC,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                selected_option="transfer_error",
                proposed_quantity=0.0,
                estimated_cost=0.0,
                confidence_score=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    def _build_warehouse_network(self, input_data: AlgorithmInput) -> List[Warehouse]:
        """Mock red de almacenes disponibles"""
        criticality_mult = {"CRITICAL": 1.2, "HIGH": 1.1, "MEDIUM": 1.0, "LOW": 0.8}.get(
            input_data.criticality, 1.0
        )
        
        return [
            Warehouse("WH-001", "Center", input_data.demand_quantity * 0.8, 50.0, 2.0 * criticality_mult, 0.95),
            Warehouse("WH-002", "South", input_data.demand_quantity * 0.6, 150.0, 4.0 * criticality_mult, 0.85),
            Warehouse("WH-003", "North", input_data.demand_quantity * 0.7, 100.0, 3.0 * criticality_mult, 0.90),
        ]
    
    def _define_transfer_activities(self, criticality: str) -> List[Activity]:
        """Actividades TDABC: picking, packing, shipping"""
        time_mult = {"CRITICAL": 1.2, "HIGH": 1.1, "MEDIUM": 1.0, "LOW": 0.8}.get(criticality, 1.0)
        
        return [
            Activity("Picking", 1.5 * time_mult, 25.0),
            Activity("Packing", 1.0 * time_mult, 20.0),
            Activity("Shipping", 2.0 * time_mult, 35.0),
            Activity("Coordination", 0.5 * time_mult, 40.0),
        ]
    
    def _evaluate_transfer_options(
        self, 
        warehouses: List[Warehouse], 
        activities: List[Activity],
        demand: float
    ) -> Warehouse:
        """Selecciona mejor almacén por TDABC cost"""
        best_wh = warehouses[0]
        best_score = float('inf')
        
        for wh in warehouses:
            if wh.available_qty >= demand * 0.9:
                # Costo TDABC = Σ(tiempo × rate)
                activity_cost = sum(
                    (a.duration_hours / 100.0 * demand) * a.cost_per_hour 
                    for a in activities
                )
                # Trade-off: costo + lead time
                total_score = activity_cost + (wh.lead_time_days * 10.0)
                
                if total_score < best_score:
                    best_score = total_score
                    best_wh = wh
        
        return best_wh
    
    def _calculate_tdabc_analysis(
        self, 
        warehouse: Warehouse, 
        activities: List[Activity]
    ) -> TransferAnalysis:
        """Calcula análisis TDABC completo"""
        activity_cost = sum(
            (a.duration_hours / 100.0 * warehouse.available_qty) * a.cost_per_hour 
            for a in activities
        )
        transfer_cost = (warehouse.distance_km / 100.0) * 10.0 + activity_cost
        
        return TransferAnalysis(
            selected_warehouse=warehouse.warehouse_id,
            transfer_quantity=warehouse.available_qty * 0.95,
            total_transfer_cost=transfer_cost,
            lead_time=warehouse.lead_time_days,
            cost_per_unit=transfer_cost / max(warehouse.available_qty, 1.0),
            reliability_score=warehouse.stock_reliability,
            total_activity_cost=activity_cost
        )
    
    def _determine_transfer_decision(self, analysis: TransferAnalysis) -> str:
        """Decide si transferencia es VIABLE, CONDITIONAL, o RISKY"""
        if analysis.cost_per_unit < 15.0 and analysis.reliability_score > 0.90:
            return "transfer_viable"
        elif analysis.cost_per_unit < 25.0 and analysis.reliability_score > 0.80:
            return "transfer_conditional"
        else:
            return "transfer_risky"
    
    def _generate_reasoning(self, analysis: TransferAnalysis, decision: str) -> str:
        """Genera explicación detallada"""
        return (
            f"Almacén: {analysis.selected_warehouse} | "
            f"Cantidad: {analysis.transfer_quantity:.0f} u. "
            f"Costo Total: ${analysis.total_transfer_cost:.0f} (${analysis.cost_per_unit:.2f}/u). "
            f"Lead time: {analysis.lead_time:.1f}d | Confiabilidad: {analysis.reliability_score:.1%}. "
            f"Actividad TDABC: ${analysis.total_activity_cost:.0f} | "
            f"Decisión: {decision.replace('transfer_', '').upper()}"
        )


# Factory function
def get_transfer_tdabc_algorithm() -> TransferTDABCAlgorithm:
    """Obtiene instancia del algoritmo Transfer TDABC"""
    return TransferTDABCAlgorithm()
