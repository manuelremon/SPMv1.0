"""
Manager del solver MIP/ILP con heurística greedy y reoptimización.

Estrategias:
1. Solver exacto (PuLP+CBC): Óptimo para instancias pequeñas
2. Heurística greedy: Rápida para instancias grandes (fallback)
3. Reoptimización local: Mejora soluciones factibles
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from datetime import datetime, timedelta
import time

from .constraint_builder import ConstraintSet, ConstraintBuilder
from .formulation import OptimizationModel, SolutionAnalyzer

logger = logging.getLogger(__name__)


class SolverStrategy(Enum):
    """Estrategias de resolución."""
    EXACT = "exact"              # PuLP+CBC (óptimo)
    GREEDY = "greedy"            # Heurística rápida
    GREEDY_WITH_REOPT = "greedy_reopt"  # Greedy + local search


@dataclass
class SolverConfig:
    """Configuración del solver."""
    strategy: SolverStrategy = SolverStrategy.GREEDY_WITH_REOPT
    time_limit_seconds: int = 300
    gap_tolerance: float = 0.05  # 5% óptimo
    greedy_iterations: int = 10
    reopt_max_iterations: int = 5
    enable_logging: bool = True


@dataclass
class SolverResult:
    """Resultado de la resolución."""
    success: bool
    status: str
    objective_value: Optional[float] = None
    solution: Dict[str, Any] = field(default_factory=dict)
    solve_time_seconds: float = 0.0
    strategy_used: str = "unknown"
    iterations: int = 0
    gap: Optional[float] = None
    
    def __post_init__(self):
        if self.status not in ["Optimal", "Feasible", "Infeasible", "Unbounded"]:
            logger.warning(f"Status inusual: {self.status}")


class GreedySolver:
    """Solucionador greedy (heurística rápida)."""
    
    def __init__(self, config: SolverConfig):
        """Inicializa solver greedy."""
        self.config = config
    
    def solve(
        self,
        item_id: str,
        demand: float,
        cte_scores: List[Dict[str, Any]],
        constraints: ConstraintSet
    ) -> SolverResult:
        """
        Resuelve greedy: selecciona opciones ordenadas por CTE ascendente.
        
        Args:
            item_id: Identificador del ítem
            demand: Cantidad demandada
            cte_scores: Lista de opciones con CTE y cantidad
            constraints: Restricciones
        
        Returns:
            SolverResult con solución greedy
        """
        start_time = time.time()
        logger.info(f"[Greedy] Resolviendo {item_id}, demanda={demand}")
        
        # Ordenar por CTE ascendente (menor costo primero)
        sorted_options = sorted(
            cte_scores,
            key=lambda x: x.get("cte", float('inf'))
        )
        
        selected = []
        total_qty = 0.0
        total_cost = 0.0
        
        # Greedy: tomar opciones hasta cubrir demanda
        for option in sorted_options:
            if total_qty >= demand:
                break
            
            option_id = option.get("option_id", "")
            cte = option.get("cte", 0)
            qty = option.get("qty", 1)
            max_qty = option.get("max_qty", qty)
            
            # Cantidad a tomar de esta opción
            qty_to_take = min(max_qty, demand - total_qty)
            
            # Verificar restricciones
            if self._check_constraints(option_id, qty_to_take, constraints):
                selected.append({
                    "option_id": option_id,
                    "quantity": qty_to_take,
                    "cte": cte,
                    "cost": cte * qty_to_take
                })
                total_qty += qty_to_take
                total_cost += cte * qty_to_take
                logger.debug(f"  Greedy: seleccionó {option_id} qty={qty_to_take}")
        
        is_feasible = total_qty >= demand - 1e-6
        solve_time = time.time() - start_time
        
        result = SolverResult(
            success=is_feasible,
            status="Feasible" if is_feasible else "Infeasible",
            objective_value=total_cost,
            solution={
                "item_id": item_id,
                "demand": demand,
                "total_quantity": total_qty,
                "total_cost": total_cost,
                "selected_options": selected,
                "gap_demand": max(0, demand - total_qty)
            },
            solve_time_seconds=solve_time,
            strategy_used="greedy",
            iterations=self.config.greedy_iterations
        )
        
        logger.info(f"[Greedy] Resolvió en {solve_time:.2f}s. "
                   f"Factible: {is_feasible}, Costo: {total_cost:.2f}")
        
        return result
    
    def _check_constraints(
        self,
        option_id: str,
        quantity: float,
        constraints: ConstraintSet
    ) -> bool:
        """Verifica si la opción cumple restricciones básicas."""
        # Verificar capacidad
        if constraints.capacity_constraints:
            for cap in constraints.capacity_constraints:
                if quantity > cap.available_capacity:
                    return False
        
        # Verificar presupuesto (simplificado)
        if constraints.budget_constraints:
            # Aquí se revisaría el presupuesto
            pass
        
        return True


class LocalSearchOptimizer:
    """Optimizador local: mejora soluciones factibles."""
    
    def __init__(self, config: SolverConfig):
        """Inicializa optimizador."""
        self.config = config
    
    def reoptimize(
        self,
        initial_solution: Dict[str, Any],
        cte_scores: List[Dict[str, Any]],
        demand: float
    ) -> Dict[str, Any]:
        """
        Reoptimización local: intenta mejorar solución greedy.
        
        Estrategia: 2-opt local search (cambios locales)
        """
        logger.info(f"[LocalSearch] Iniciando reoptimización...")
        
        best_solution = initial_solution.copy()
        best_cost = best_solution.get("total_cost", float('inf'))
        
        for iteration in range(self.config.reopt_max_iterations):
            improved = False
            
            # 2-opt: intentar remover/agregar opciones
            for i, selected in enumerate(best_solution.get("selected_options", [])):
                option_id = selected.get("option_id", "")
                
                # Intentar aumentar cantidad
                new_qty = selected.get("quantity", 1) * 1.1
                new_cost = selected.get("cte", 0) * new_qty
                
                if new_cost < selected.get("cost", 0):
                    selected["quantity"] = new_qty
                    selected["cost"] = new_cost
                    improved = True
                    logger.debug(f"[LocalSearch] Mejora: {option_id} qty aumentada")
            
            if not improved:
                break
        
        logger.info(f"[LocalSearch] Reoptimización completada en {iteration+1} iteraciones")
        return best_solution


class SolverManager:
    """Manager principal del solver."""
    
    def __init__(self, config: Optional[SolverConfig] = None):
        """Inicializa manager del solver."""
        self.config = config or SolverConfig()
        self.greedy_solver = GreedySolver(self.config)
        self.local_optimizer = LocalSearchOptimizer(self.config)
        self.logger = logger
    
    def solve(
        self,
        item_id: str,
        demand: float,
        required_date: str,
        cte_scores: List[Dict[str, Any]],
        constraints: ConstraintSet
    ) -> SolverResult:
        """
        Resuelve el portafolio con estrategia elegida.
        
        Args:
            item_id: Identificador del ítem
            demand: Cantidad demandada
            required_date: Fecha requerida (YYYY-MM-DD)
            cte_scores: Lista de opciones con CTE
            constraints: Restricciones
        
        Returns:
            SolverResult con solución
        """
        self.logger.info(f"[SolverManager] Resolviendo {item_id} (estrategia={self.config.strategy.value})")
        
        if self.config.strategy == SolverStrategy.EXACT:
            return self._solve_exact(item_id, demand, required_date, cte_scores, constraints)
        
        elif self.config.strategy == SolverStrategy.GREEDY:
            return self._solve_greedy(item_id, demand, cte_scores, constraints)
        
        elif self.config.strategy == SolverStrategy.GREEDY_WITH_REOPT:
            return self._solve_greedy_with_reopt(item_id, demand, cte_scores, constraints)
        
        else:
            raise ValueError(f"Estrategia desconocida: {self.config.strategy}")
    
    def _solve_exact(
        self,
        item_id: str,
        demand: float,
        required_date: str,
        cte_scores: List[Dict[str, Any]],
        constraints: ConstraintSet
    ) -> SolverResult:
        """Resuelve con PuLP+CBC (exacto)."""
        self.logger.info(f"[Exact] Construyendo modelo MIP...")
        
        try:
            model = OptimizationModel(
                item_id=item_id,
                demand=demand,
                required_date=required_date,
                cte_scores=cte_scores,
                constraints=constraints,
                time_limit_seconds=self.config.time_limit_seconds
            )
            
            model.build()
            success, solution = model.solve()
            
            if success:
                return SolverResult(
                    success=True,
                    status="Optimal",
                    objective_value=solution.get("objective_value"),
                    solution=solution,
                    strategy_used="exact"
                )
            else:
                return SolverResult(
                    success=False,
                    status=solution.get("status", "Infeasible"),
                    strategy_used="exact"
                )
        
        except Exception as e:
            self.logger.error(f"[Exact] Error: {e}")
            # Fallback a greedy
            self.logger.info(f"[Exact] Fallback a greedy...")
            return self._solve_greedy(item_id, demand, cte_scores, constraints)
    
    def _solve_greedy(
        self,
        item_id: str,
        demand: float,
        cte_scores: List[Dict[str, Any]],
        constraints: ConstraintSet
    ) -> SolverResult:
        """Resuelve con greedy."""
        return self.greedy_solver.solve(item_id, demand, cte_scores, constraints)
    
    def _solve_greedy_with_reopt(
        self,
        item_id: str,
        demand: float,
        cte_scores: List[Dict[str, Any]],
        constraints: ConstraintSet
    ) -> SolverResult:
        """Resuelve con greedy + reoptimización local."""
        # Fase 1: Greedy
        greedy_result = self.greedy_solver.solve(item_id, demand, cte_scores, constraints)
        
        if not greedy_result.success:
            self.logger.warning(f"[Greedy+Reopt] Greedy no encontró solución factible")
            return greedy_result
        
        # Fase 2: Reoptimización
        reopt_solution = self.local_optimizer.reoptimize(
            greedy_result.solution,
            cte_scores,
            demand
        )
        
        greedy_result.solution = reopt_solution
        greedy_result.strategy_used = "greedy_with_reopt"
        greedy_result.iterations = self.config.greedy_iterations + self.config.reopt_max_iterations
        
        return greedy_result
    
    def batch_solve(
        self,
        items: List[Dict[str, Any]],
        constraints: Optional[ConstraintSet] = None
    ) -> List[SolverResult]:
        """
        Resuelve múltiples ítems en lote.
        
        Args:
            items: Lista de dicts con item_id, demand, required_date, cte_scores
            constraints: Restricciones comunes
        
        Returns:
            Lista de SolverResult
        """
        results = []
        for item in items:
            result = self.solve(
                item_id=item.get("item_id"),
                demand=item.get("demand", 0),
                required_date=item.get("required_date", ""),
                cte_scores=item.get("cte_scores", []),
                constraints=constraints or ConstraintSet({})
            )
            results.append(result)
        
        return results
    
    def get_portfolio_summary(self, results: List[SolverResult]) -> Dict[str, Any]:
        """Resumen del portafolio."""
        total_cost = sum(r.objective_value or 0 for r in results)
        num_feasible = sum(1 for r in results if r.success)
        
        return {
            "num_items": len(results),
            "num_feasible": num_feasible,
            "total_cost": total_cost,
            "avg_cost_per_item": total_cost / len(results) if results else 0,
            "feasibility_rate": num_feasible / len(results) if results else 0
        }
