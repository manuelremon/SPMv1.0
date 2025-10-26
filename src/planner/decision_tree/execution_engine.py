"""
Motor de ejecución del árbol de decisión.

Responsabilidades:
- Navegar el árbol según gates
- Evaluar contexto en cada nodo
- Registrar ejecución
- Retornar camino y resultado
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from .decision_tree import (
    DecisionNode, ExecutionPath, DecisionTreeBuilder, 
    create_standard_decision_tree, SourceRoute, GateType
)

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Contexto de ejecución del árbol."""
    item_id: str
    demand_quantity: float
    required_date: str
    
    # Información de inventario
    local_stock_available: float = 0.0
    local_assets_available: float = 0.0
    bom_components_available: Dict[str, float] = field(default_factory=dict)
    substitutes_available: List[str] = field(default_factory=list)
    
    # Información de transferencias
    transfer_centers_available: Dict[str, float] = field(default_factory=dict)
    intercompany_available: bool = False
    vmi_contract_active: bool = False
    loan_partner_available: bool = False
    
    # Información de tiempo
    days_to_deadline: float = 0.0
    can_expedite: bool = False
    expedite_budget_available: float = 0.0
    
    # Información de compra
    supplier_available: bool = True
    supplier_lead_time_days: float = 14.0
    
    # Metadata
    criticality: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    budget_available: float = float('inf')
    max_acceptable_cost: float = float('inf')
    
    def get_gates_evaluation(self) -> Dict[str, bool]:
        """Retorna evaluación de gates relevantes."""
        return {
            "stock_local": self.local_stock_available >= self.demand_quantity,
            "assets_available": self.local_assets_available > 0,
            "bom_available": len(self.bom_components_available) > 0,
            "substitutes_available": len(self.substitutes_available) > 0,
            "transfer_available": sum(self.transfer_centers_available.values()) >= self.demand_quantity,
            "intercompany_available": self.intercompany_available,
            "vmi_active": self.vmi_contract_active,
            "loan_partner_available": self.loan_partner_available,
            "expedite_available": self.can_expedite and self.expedite_budget_available > 0,
            "supplier_available": self.supplier_available,
            "time_sufficient": self.days_to_deadline >= 1
        }


class DecisionTreeExecutor:
    """Ejecutor del árbol de decisión."""
    
    def __init__(self, tree_builder: Optional[DecisionTreeBuilder] = None):
        """Inicializa executor."""
        if tree_builder is None:
            tree_builder = create_standard_decision_tree()
        
        self.tree = tree_builder.build()
        self.all_nodes = tree_builder.get_all_nodes()
        self.logger = logger
    
    def execute(
        self,
        context: ExecutionContext,
        max_depth: int = 12
    ) -> ExecutionPath:
        """
        Ejecuta el árbol de decisión.
        
        Args:
            context: Contexto de ejecución (inventario, tiempo, etc)
            max_depth: Profundidad máxima del árbol
        
        Returns:
            ExecutionPath con resultado
        """
        path_id = f"{context.item_id}_{datetime.now().isoformat()}"
        path = ExecutionPath(
            path_id=path_id,
            item_id=context.item_id,
            demand_quantity=context.demand_quantity,
            required_date=context.required_date
        )
        
        self.logger.info(f"Iniciando ejecución árbol: {context.item_id}, "
                        f"demanda={context.demand_quantity}, deadline={context.required_date}")
        
        current_node = self.tree
        depth = 0
        
        while current_node is not None and depth < max_depth:
            # Evaluar gates del nodo actual
            gates_pass, failed_gates = current_node.evaluate_gates(self._context_to_dict(context))
            path.add_node_visit(current_node.node_id, gates_pass, failed_gates)
            
            self.logger.debug(f"Nodo {current_node.node_id} ({current_node.name}): "
                            f"gates_pass={gates_pass}, failed={failed_gates}")
            
            # Determinar próximo nodo
            if gates_pass:
                # Gates abiertos: seguir por success path
                if current_node.next_on_success is None:
                    # Nodo terminal
                    path.set_result(
                        success=True,
                        route=current_node.route,
                        source=current_node.name,
                        lead_time=current_node.estimated_lead_time_days,
                        cost=current_node.estimated_cost
                    )
                    self.logger.info(f"Ejecución exitosa: ruta={current_node.route.name}")
                    break
                
                current_node = current_node.next_on_success
            else:
                # Gates cerrados: seguir por failure path
                if current_node.next_on_failure is None:
                    # No hay alternate: fallar
                    path.set_result(
                        success=False,
                        route=current_node.route,
                        source=current_node.name,
                        lead_time=float('inf'),
                        cost=float('inf')
                    )
                    self.logger.warning(f"Ejecución fallida en nodo {current_node.node_id}: "
                                      f"gates={failed_gates}")
                    break
                
                current_node = current_node.next_on_failure
            
            depth += 1
        
        if depth >= max_depth:
            self.logger.warning(f"Ejecución alcanzó profundidad máxima")
        
        return path
    
    def execute_batch(
        self,
        contexts: List[ExecutionContext]
    ) -> List[ExecutionPath]:
        """Ejecuta múltiples contextos."""
        paths = []
        for context in contexts:
            path = self.execute(context)
            paths.append(path)
        
        return paths
    
    def _context_to_dict(self, context: ExecutionContext) -> Dict[str, Any]:
        """Convierte ExecutionContext a diccionario para gates."""
        return {
            "item_id": context.item_id,
            "demand": context.demand_quantity,
            "local_stock": context.local_stock_available,
            "local_assets": context.local_assets_available,
            "bom_components": context.bom_components_available,
            "substitutes": context.substitutes_available,
            "transfer_centers": context.transfer_centers_available,
            "intercompany": context.intercompany_available,
            "vmi": context.vmi_contract_active,
            "loan_partner": context.loan_partner_available,
            "days_to_deadline": context.days_to_deadline,
            "can_expedite": context.can_expedite,
            "expedite_budget": context.expedite_budget_available,
            "supplier_available": context.supplier_available,
            "supplier_lead_time": context.supplier_lead_time_days,
            "criticality": context.criticality,
            "budget": context.budget_available,
            "max_cost": context.max_acceptable_cost
        }
    
    def get_execution_statistics(self, paths: List[ExecutionPath]) -> Dict[str, Any]:
        """Estadísticas de ejecución."""
        successful = [p for p in paths if p.final_success]
        
        if not paths:
            return {"error": "Sin ejecuciones"}
        
        stats = {
            "total_executions": len(paths),
            "successful": len(successful),
            "failed": len(paths) - len(successful),
            "success_rate": len(successful) / len(paths) if paths else 0,
            "avg_lead_time": sum(p.total_lead_time for p in successful) / len(successful) if successful else 0,
            "avg_cost": sum(p.total_cost for p in successful) / len(successful) if successful else 0,
            "routes_used": {}
        }
        
        # Contar rutas usadas
        for path in successful:
            if path.final_route:
                route_name = path.final_route.name
                stats["routes_used"][route_name] = stats["routes_used"].get(route_name, 0) + 1
        
        return stats
    
    def export_execution_log(
        self,
        paths: List[ExecutionPath],
        file_path: str,
        format: str = "json"
    ) -> bool:
        """Exporta log de ejecuciones."""
        try:
            if format == "json":
                import json
                data = [p.get_summary() for p in paths]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                # Formato texto simple
                with open(file_path, 'w', encoding='utf-8') as f:
                    for path in paths:
                        summary = path.get_summary()
                        f.write(f"Item: {summary['item_id']}\n")
                        f.write(f"  Success: {summary['success']}\n")
                        f.write(f"  Route: {summary['route']}\n")
                        f.write(f"  Source: {summary['source']}\n")
                        f.write(f"  Lead Time: {summary['lead_time']} days\n")
                        f.write(f"  Cost: ${summary['cost']:.2f}\n")
                        f.write(f"  Nodes Visited: {summary['num_nodes']}\n\n")
            
            self.logger.info(f"Log exportado a: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exportando log: {e}")
            return False


class PathEvaluator:
    """Evaluador de viabilidad de caminos."""
    
    @staticmethod
    def evaluate_path_feasibility(
        path: ExecutionPath,
        required_date: str,
        max_budget: float,
        criticality: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Evalúa viabilidad de un camino.
        
        Returns:
            Viabilidad según múltiples criterios
        """
        
        # Parsear fechas (simplificado)
        # En producción, usar dateutil.parser
        
        evaluation = {
            "path_id": path.path_id,
            "feasible": path.final_success,
            "success": path.final_success,
            "route": path.final_route.name if path.final_route else None,
            "criteria": {
                "success": path.final_success,
                "lead_time_ok": path.total_lead_time < 365,  # No infinito
                "cost_ok": path.total_cost <= max_budget,
                "criticality_match": True
            },
            "overall_feasible": True
        }
        
        # Verificar lead time
        if path.total_lead_time >= 365:
            evaluation["criteria"]["lead_time_ok"] = False
        
        # Verificar costo
        if path.total_cost > max_budget:
            evaluation["criteria"]["cost_ok"] = False
        
        # Calcular overall
        all_criteria_ok = all(evaluation["criteria"].values())
        evaluation["overall_feasible"] = all_criteria_ok
        
        return evaluation
    
    @staticmethod
    def compare_paths(
        path1: ExecutionPath,
        path2: ExecutionPath,
        weight_cost: float = 0.4,
        weight_time: float = 0.3,
        weight_success: float = 0.3
    ) -> Tuple[ExecutionPath, float]:
        """
        Compara dos caminos. Retorna el mejor.
        
        Score = weight_cost × cost_score + weight_time × time_score + weight_success × success_score
        """
        
        # Scores normalizados 0-1
        cost_score_1 = 1 - min(path1.total_cost / 1000, 1)  # Normalizar
        cost_score_2 = 1 - min(path2.total_cost / 1000, 1)
        
        time_score_1 = max(0, 1 - path1.total_lead_time / 30)
        time_score_2 = max(0, 1 - path2.total_lead_time / 30)
        
        success_score_1 = 1 if path1.final_success else 0
        success_score_2 = 1 if path2.final_success else 0
        
        # Score composito
        score1 = (weight_cost * cost_score_1 + 
                 weight_time * time_score_1 + 
                 weight_success * success_score_1)
        
        score2 = (weight_cost * cost_score_2 + 
                 weight_time * time_score_2 + 
                 weight_success * success_score_2)
        
        best_path = path1 if score1 >= score2 else path2
        best_score = max(score1, score2)
        
        return best_path, best_score
    
    @staticmethod
    def rank_paths(paths: List[ExecutionPath]) -> List[Tuple[ExecutionPath, float]]:
        """Rankea múltiples caminos por viabilidad."""
        ranked = []
        
        for path in paths:
            # Score simple: éxito + costo bajo + tiempo corto
            success_bonus = 0.5 if path.final_success else 0
            cost_penalty = min(path.total_cost / 1000, 1)  # 0-1
            time_penalty = min(path.total_lead_time / 30, 1)  # 0-1
            
            score = success_bonus - (0.3 * cost_penalty + 0.2 * time_penalty)
            ranked.append((path, score))
        
        # Ordenar por score descendente
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
