"""
Análisis post-optimización: sensibilidad, viabilidad, reportes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from .solver_manager import SolverResult
from .constraint_builder import ConstraintSet

logger = logging.getLogger(__name__)


@dataclass
class SensitivityAnalysis:
    """Análisis de sensibilidad de la solución."""
    shadow_prices: Dict[str, float] = field(default_factory=dict)  # Precios sombra
    reduced_costs: Dict[str, float] = field(default_factory=dict)  # Costos reducidos
    dual_values: Dict[str, float] = field(default_factory=dict)    # Valores duales
    
    def get_binding_constraints(self) -> List[str]:
        """Retorna restricciones binding (activas)."""
        return [
            constr for constr, price in self.shadow_prices.items()
            if abs(price) > 1e-6
        ]


@dataclass
class ViabilityReport:
    """Reporte de viabilidad de la solución."""
    is_feasible: bool
    feasibility_gap: float = 0.0  # Gap vs demanda
    constraint_violations: List[str] = field(default_factory=list)
    infeasibility_reasons: List[str] = field(default_factory=list)
    

@dataclass
class CostBreakdownReport:
    """Desglose de costos por fuente."""
    option_id: str
    quantity: float
    unit_cost: float
    total_cost: float
    cost_percentage: float = 0.0
    criticality_level: str = "MEDIUM"


class RobustnessAnalyzer:
    """Analiza robustez de la solución ante cambios de parámetros."""
    
    @staticmethod
    def scenario_analysis(
        base_solution: SolverResult,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Análisis de escenarios: ¿qué pasa si cambian parámetros?
        
        Args:
            base_solution: Solución base
            scenarios: Lista de escenarios (ej: +10% costo, -20% tiempo)
        
        Returns:
            Análisis de robustez
        """
        logger.info(f"Analizando {len(scenarios)} escenarios...")
        
        results = {}
        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get("name", f"Scenario_{i}")
            # Aquí se aplicarían cambios y se resolvería
            # Por ahora: placeholder
            results[scenario_name] = {
                "applied_changes": scenario,
                "impact": "pending_resolution"
            }
        
        return results
    
    @staticmethod
    def get_critical_parameters(solution: SolverResult) -> List[str]:
        """Identifica parámetros críticos (más sensibles)."""
        # Parámetros que más afectan la solución
        critical = []
        
        selected = solution.solution.get("selected_options", [])
        if selected:
            # Si hay pocos proveedores, son críticos
            if len(selected) <= 2:
                critical.append("supplier_selection")
            
            # Si hay restricción presupuestal activa
            critical.append("budget_constraint")
        
        return critical


class ModelAnalyzer:
    """Analizador principal del modelo."""
    
    def __init__(self):
        """Inicializa analizador."""
        self.logger = logger
    
    def analyze_solution(
        self,
        solver_result: SolverResult,
        constraints: ConstraintSet
    ) -> Dict[str, Any]:
        """
        Análisis completo de la solución.
        
        Args:
            solver_result: Resultado del solver
            constraints: Restricciones usadas
        
        Returns:
            Análisis completo
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "feasibility": self._analyze_feasibility(solver_result, constraints),
            "cost_breakdown": self._analyze_cost_breakdown(solver_result),
            "robustness": self._analyze_robustness(solver_result),
            "recommendations": self._generate_recommendations(solver_result)
        }
        
        return analysis
    
    def _analyze_feasibility(
        self,
        solver_result: SolverResult,
        constraints: ConstraintSet
    ) -> ViabilityReport:
        """Analiza viabilidad de la solución."""
        
        violations = []
        reasons = []
        
        # Verificar demanda
        solution = solver_result.solution
        gap_demand = solution.get("gap_demand", 0)
        
        if gap_demand > 1e-6:
            violations.append("demand_not_covered")
            reasons.append(f"Demanda no cubierta: {gap_demand} unidades")
        
        # Verificar presupuesto
        total_cost = solution.get("total_cost", 0)
        if constraints.budget_constraints:
            budget = constraints.budget_constraints[0].available_budget
            if total_cost > budget:
                violations.append("budget_exceeded")
                reasons.append(f"Presupuesto excedido: {total_cost} > {budget}")
        
        is_feasible = len(violations) == 0
        
        return ViabilityReport(
            is_feasible=is_feasible,
            feasibility_gap=gap_demand,
            constraint_violations=violations,
            infeasibility_reasons=reasons
        )
    
    def _analyze_cost_breakdown(self, solver_result: SolverResult) -> List[CostBreakdownReport]:
        """Desglose de costos."""
        breakdown = []
        
        solution = solver_result.solution
        total_cost = solution.get("total_cost", 0)
        selected_options = solution.get("selected_options", [])
        
        for option in selected_options:
            option_id = option.get("option_id", "")
            qty = option.get("quantity", 0)
            cte = option.get("cte", 0)
            cost = option.get("cost", 0)
            pct = (cost / total_cost * 100) if total_cost > 0 else 0
            
            report = CostBreakdownReport(
                option_id=option_id,
                quantity=qty,
                unit_cost=cte,
                total_cost=cost,
                cost_percentage=pct
            )
            breakdown.append(report)
        
        # Ordenar por costo descendente
        breakdown.sort(key=lambda x: x.total_cost, reverse=True)
        
        return breakdown
    
    def _analyze_robustness(self, solver_result: SolverResult) -> Dict[str, Any]:
        """Analiza robustez de la solución."""
        
        robustness = {
            "num_suppliers": 0,
            "supplier_concentration": 0.0,  # % en top supplier
            "cost_variance": 0.0,
            "critical_parameters": []
        }
        
        selected_options = solver_result.solution.get("selected_options", [])
        robustness["num_suppliers"] = len(selected_options)
        
        if selected_options:
            total_cost = solver_result.solution.get("total_cost", 0)
            max_cost = max(o.get("cost", 0) for o in selected_options)
            robustness["supplier_concentration"] = (max_cost / total_cost * 100) if total_cost > 0 else 0
        
        robustness["critical_parameters"] = RobustnessAnalyzer.get_critical_parameters(solver_result)
        
        return robustness
    
    def _generate_recommendations(self, solver_result: SolverResult) -> List[str]:
        """Genera recomendaciones basadas en la solución."""
        recommendations = []
        
        if not solver_result.success:
            recommendations.append("NO SOLUCIÓN FACTIBLE ENCONTRADA. Revisar restricciones.")
            return recommendations
        
        selected_options = solver_result.solution.get("selected_options", [])
        
        # Recomendación: diversificación de proveedores
        if len(selected_options) == 1:
            recommendations.append(
                "Considerar 2+ proveedores para mitigar riesgo de suministro"
            )
        
        # Recomendación: margen de seguridad
        gap = solver_result.solution.get("gap_demand", 0)
        if gap > 0:
            recommendations.append(
                f"Stock insuficiente. Gap de {gap} unidades. Evaluar compra emergente."
            )
        
        # Recomendación: revisión de restricciones
        if solver_result.strategy_used == "greedy":
            recommendations.append(
                "Solución encontrada por heurística. Considerar re-optimizar con exacto si tiempo lo permite."
            )
        
        return recommendations
    
    def generate_report(
        self,
        solver_result: SolverResult,
        constraints: ConstraintSet,
        include_sensitivity: bool = False
    ) -> Dict[str, Any]:
        """
        Genera reporte completo.
        
        Args:
            solver_result: Resultado del solver
            constraints: Restricciones usadas
            include_sensitivity: ¿Incluir análisis de sensibilidad?
        
        Returns:
            Reporte completo
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "solution_status": solver_result.status,
            "objective_value": solver_result.objective_value,
            "solve_time_seconds": solver_result.solve_time_seconds,
            "strategy_used": solver_result.strategy_used,
            "analysis": self.analyze_solution(solver_result, constraints)
        }
        
        if include_sensitivity:
            report["sensitivity_analysis"] = {
                "warning": "Análisis de sensibilidad requiere datos del solver avanzados"
            }
        
        return report
    
    def export_report_html(
        self,
        report: Dict[str, Any],
        file_path: str
    ) -> bool:
        """Exporta reporte a HTML."""
        try:
            html_content = self._build_html_report(report)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"Reporte exportado a: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando reporte: {e}")
            return False
    
    def _build_html_report(self, report: Dict[str, Any]) -> str:
        """Construye contenido HTML del reporte."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SPM - Reporte de Optimización</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .section {{ margin-bottom: 30px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <h1>SPM - Reporte de Optimización de Portafolio</h1>
    <p>Generado: {report.get('generated_at', 'N/A')}</p>
    
    <div class="section">
        <h2>Resultado</h2>
        <p>Estado: <strong>{report.get('solution_status', 'N/A')}</strong></p>
        <p>Valor Objetivo: ${report.get('objective_value', 'N/A'):.2f}</p>
        <p>Tiempo Resolución: {report.get('solve_time_seconds', 'N/A'):.2f}s</p>
        <p>Estrategia: {report.get('strategy_used', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>Análisis</h2>
        <p>Reporte completo disponible en JSON.</p>
    </div>
</body>
</html>
        """
        return html
    
    def export_report_json(
        self,
        report: Dict[str, Any],
        file_path: str
    ) -> bool:
        """Exporta reporte a JSON."""
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Reporte JSON exportado a: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando JSON: {e}")
            return False
