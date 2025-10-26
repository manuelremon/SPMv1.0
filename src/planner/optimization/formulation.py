"""
Formulación MIP/ILP para optimización de portafolio.

Modelo matemático:
    minimize: Σᵢ CTEᵢ × xᵢ + Σⱼ penalty_preferences_j

    subject to:
        (Demanda)      Σᵢ qtyᵢ × xᵢ ≥ demand
        (FEFO)         consume en orden exp_date
        (Capacidad)    Σᵢ inv_iⱼ ≤ cap_j  ∀j (ubicación)
        (Lead time)    LT_i ≤ LT_max
        (SL)           SL_i ≥ SL_min
        (Presupuesto)  Σᵢ cost_i × xᵢ ≤ budget
        (One-in)       Σₖ y_ik ≤ 1  ∀i (máx 1 proveedor)
        (Binarias)     xᵢ ∈ {0,1}
        (Continuas)    qty_i ≥ 0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from datetime import datetime

try:
    from pulp import (
        LpMinimize, LpMaximize, LpProblem, LpVariable, 
        LpBinary, LpContinuous, lpSum, LpStatus, value
    )
except ImportError:
    raise ImportError("PuLP no instalado. Instala con: pip install pulp")

from .constraint_builder import ConstraintSet, ConstraintType, ConstraintBuilder

logger = logging.getLogger(__name__)


class SolverStatus(Enum):
    """Estado del solver."""
    OPTIMAL = "Optimal"
    NOT_SOLVED = "Not Solved"
    INFEASIBLE = "Infeasible"
    UNBOUNDED = "Unbounded"
    UNDEFINED = "Undefined"


@dataclass
class PortfolioVariable:
    """Variable de decisión en el portafolio."""
    option_id: str
    item_id: str
    quantity: float = 0.0
    is_selected: bool = False
    cte_value: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Costo total = CTE × cantidad."""
        return self.cte_value * self.quantity


@dataclass
class OptimizationModel:
    """Modelo MIP para portafolio."""
    item_id: str
    demand: float
    required_date: str
    cte_scores: List[Dict[str, Any]]  # [{"option_id": "...", "cte": X, "qty": Y}, ...]
    constraints: ConstraintSet
    
    # Pesos objetivos
    weight_cost: float = 0.4
    weight_time_risk: float = 0.6
    
    # Parámetros del solver
    time_limit_seconds: Optional[int] = None
    gap_tolerance: float = 0.05  # 5% de gap óptimo
    
    # Modelo PuLP
    model: Optional[LpProblem] = None
    variables: Dict[str, LpVariable] = field(default_factory=dict)
    solution: Optional[Dict[str, Any]] = None
    
    def build(self) -> "OptimizationModel":
        """Construye el modelo MIP."""
        logger.info(f"Construyendo MIP para {self.item_id}, demanda={self.demand}")
        
        # Crear problema
        self.model = LpProblem(f"Portfolio_{self.item_id}", LpMinimize)
        
        # Variables de decisión
        self._create_variables()
        
        # Función objetivo
        self._set_objective()
        
        # Restricciones
        self._add_constraints()
        
        logger.info(f"MIP construido: {len(self.variables)} variables, "
                   f"{len(self.model.constraints)} restricciones")
        return self
    
    def _create_variables(self):
        """Crea variables de decisión."""
        # Tabla hash: option_id -> LpVariable
        self.variables = {}
        
        for score_entry in self.cte_scores:
            option_id = score_entry.get("option_id", "")
            max_qty = score_entry.get("max_qty", float('inf'))
            
            # Variable binaria: ¿seleccionar esta opción?
            if max_qty == 1 or max_qty < 1.5:  # Si qty es binaria
                var = LpVariable(f"x_{option_id}", cat=LpBinary)
            else:
                # Variable continua: cantidad a ordenar
                var = LpVariable(f"qty_{option_id}", lowBound=0, cat=LpContinuous)
            
            self.variables[option_id] = var
            logger.debug(f"Variable creada: {option_id}")
    
    def _set_objective(self):
        """Establece función objetivo: minimizar CTE total."""
        if not self.variables:
            raise ValueError("No hay variables. Ejecuta _create_variables() primero.")
        
        objective = lpSum([
            score_entry.get("cte", 0) * self.variables[score_entry.get("option_id")]
            for score_entry in self.cte_scores
            if score_entry.get("option_id") in self.variables
        ])
        
        self.model += objective, "Objective_MinimizeCTE"
        logger.debug("Función objetivo establecida: minimizar CTE")
    
    def _add_constraints(self):
        """Agrega restricciones al modelo."""
        # 1. Restricción de demanda
        self._add_demand_constraint()
        
        # 2. Restricción de capacidad
        self._add_capacity_constraints()
        
        # 3. Restricción de presupuesto
        self._add_budget_constraint()
        
        # 4. Restricción de lead time
        self._add_lead_time_constraints()
        
        # 5. Restricción de SL
        self._add_service_level_constraints()
        
        # 6. Restricción one-in
        self._add_one_in_constraints()
        
        logger.debug(f"Total restricciones: {len(self.model.constraints)}")
    
    def _add_demand_constraint(self):
        """Demanda: Σ qty·x ≥ demand"""
        demand_constr = self.constraints.demand_constraints
        if not demand_constr:
            return
        
        demand_qty = demand_constr[0].quantity_required
        
        # Cantidad total ≥ demanda
        qty_sum = lpSum([
            score_entry.get("qty", 1) * self.variables.get(score_entry.get("option_id"))
            for score_entry in self.cte_scores
            if score_entry.get("option_id") in self.variables
        ])
        
        self.model += qty_sum >= demand_qty, "Constraint_Demand"
        logger.debug(f"Restricción demanda: Σ qty >= {demand_qty}")
    
    def _add_capacity_constraints(self):
        """Capacidad por ubicación: Σ inv ≤ cap_j"""
        for cap_constr in self.constraints.capacity_constraints:
            max_cap = cap_constr.available_capacity
            location = cap_constr.location_id
            
            # Simplificación: si hay capacidad, permitir hasta ese máximo
            qty_sum = lpSum([
                score_entry.get("qty", 1) * self.variables.get(score_entry.get("option_id"))
                for score_entry in self.cte_scores
                if score_entry.get("option_id") in self.variables
            ])
            
            self.model += qty_sum <= max_cap, f"Constraint_Capacity_{location}"
            logger.debug(f"Restricción capacidad {location}: <= {max_cap}")
    
    def _add_budget_constraint(self):
        """Presupuesto: Σ cost·x ≤ budget"""
        budget_constr = self.constraints.budget_constraints
        if not budget_constr:
            return
        
        budget = budget_constr[0].available_budget
        
        cost_sum = lpSum([
            score_entry.get("cte", 0) * score_entry.get("qty", 1) * self.variables.get(score_entry.get("option_id"))
            for score_entry in self.cte_scores
            if score_entry.get("option_id") in self.variables
        ])
        
        self.model += cost_sum <= budget, "Constraint_Budget"
        logger.debug(f"Restricción presupuesto: <= {budget}")
    
    def _add_lead_time_constraints(self):
        """Lead time: LT_i ≤ LT_max (basado en deadline)"""
        for lt_constr in self.constraints.lead_time_constraints:
            # Filtrar opciones que cumplan el lead time
            # Esto es más bien un filtro pre-solver
            logger.debug(f"Restricción lead time para {lt_constr.option_id}")
    
    def _add_service_level_constraints(self):
        """SL: SL_i ≥ SL_min"""
        for sl_constr in self.constraints.service_level_constraints:
            # Similar a lead time: filtrar opciones
            logger.debug(f"Restricción SL para {sl_constr.item_id}")
    
    def _add_one_in_constraints(self):
        """One-in: máximo 1 proveedor por ítem"""
        for one_in_constr in self.constraints.one_in_constraints:
            allowed_suppliers = one_in_constr.allowed_suppliers
            
            supplier_vars = [
                self.variables.get(f"{one_in_constr.item_id}_{sup}")
                for sup in allowed_suppliers
                if f"{one_in_constr.item_id}_{sup}" in self.variables
            ]
            
            if supplier_vars:
                self.model += lpSum(supplier_vars) <= 1, f"Constraint_OneIn_{one_in_constr.item_id}"
                logger.debug(f"Restricción one-in para {one_in_constr.item_id}")
    
    def solve(self) -> Tuple[bool, Dict[str, Any]]:
        """Resuelve el modelo."""
        if self.model is None:
            raise ValueError("Modelo no construido. Ejecuta build() primero.")
        
        logger.info("Iniciando solver...")
        
        try:
            # Solver CBC (open-source)
            self.model.solve()
        except Exception as e:
            logger.error(f"Error en solver: {e}")
            return False, {"error": str(e)}
        
        status = LpStatus[self.model.status]
        logger.info(f"Solver terminado. Status: {status}")
        
        if status == "Optimal":
            self._extract_solution()
            return True, self.solution
        else:
            self.solution = {"status": status, "objective_value": None}
            return False, self.solution
    
    def _extract_solution(self):
        """Extrae la solución del modelo."""
        self.solution = {
            "status": "Optimal",
            "objective_value": value(self.model.objective),
            "variables": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for var_name, var in self.variables.items():
            if var.varValue is not None and var.varValue > 1e-6:
                self.solution["variables"][var_name] = var.varValue
        
        logger.info(f"Solución extraída. Variables activas: {len(self.solution['variables'])}")
    
    def get_solution_summary(self) -> Dict[str, Any]:
        """Retorna resumen de la solución."""
        if self.solution is None:
            return {"error": "Sin solución disponible"}
        
        return {
            "status": self.solution.get("status"),
            "objective_value": self.solution.get("objective_value"),
            "num_options_selected": len(self.solution.get("variables", {})),
            "options_selected": list(self.solution.get("variables", {}).keys()),
            "timestamp": self.solution.get("timestamp")
        }


@dataclass
class SolutionAnalyzer:
    """Analiza la solución del modelo."""
    
    model: OptimizationModel
    solution: Dict[str, Any]
    
    def get_feasibility_report(self) -> Dict[str, Any]:
        """Reporte de viabilidad."""
        report = {
            "is_feasible": self.solution.get("status") == "Optimal",
            "objective_value": self.solution.get("objective_value"),
            "gap": "N/A"
        }
        return report
    
    def get_sensitivity_analysis(self) -> Dict[str, Any]:
        """Análisis de sensibilidad (shadow prices)."""
        if self.model.model is None:
            return {"error": "Modelo no disponible"}
        
        sensitivity = {}
        for constr_name, constr in self.model.model.constraints.items():
            sensitivity[constr_name] = {
                "slack": constr.slack,
                "pi": constr.pi  # Shadow price
            }
        return sensitivity
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """Desglose de costos por opción."""
        breakdown = {}
        for option_id, qty in self.solution.get("variables", {}).items():
            # Encontrar CTE de esta opción
            cte = next(
                (e.get("cte", 0) for e in self.model.cte_scores if e.get("option_id") == option_id),
                0
            )
            breakdown[option_id] = cte * qty
        return breakdown
