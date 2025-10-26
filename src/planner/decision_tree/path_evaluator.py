"""
path_evaluator.py
Evaluador de viabilidad de caminos de abastecimiento

Módulo responsable de:
- Evaluación detallada de viabilidad de ExecutionPath
- Análisis de compatibilidad técnica y criterios operativos
- Scoring específico por tipo de ruta
- Matrices de decisión multi-criterio
- Optimización de rutas alcanzables
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import json
from datetime import datetime, timedelta

from .decision_tree import ExecutionPath, SourceRoute, DecisionNode


class FeasibilityMetric(Enum):
    """Métricas de viabilidad evaluadas"""
    SUCCESS = "success"               # Ruta alcanzó nodo final exitoso
    LEAD_TIME = "lead_time"           # Lead time dentro de plazo
    COST = "cost"                     # Costo dentro de presupuesto
    CRITICALITY_MATCH = "criticality" # Ruta compatible con criticidad
    QUALITY = "quality"               # Calidad garantizada
    RISK = "risk"                     # Riesgo aceptable
    REGULATORY = "regulatory"         # Cumple normas
    AVAILABLE = "available"           # Disponibilidad confirmada


@dataclass
class FeasibilityScore:
    """Score detallado de viabilidad de un camino"""
    path_id: str
    metrics: Dict[FeasibilityMetric, bool] = field(default_factory=dict)
    weights: Dict[FeasibilityMetric, float] = field(default_factory=dict)
    
    # Scores normalizados [0,1]
    lead_time_score: float = 0.0      # 1.0 si dentro plazo, decrece con atraso
    cost_score: float = 0.0           # 1.0 si within budget, decrece con exceso
    success_score: float = 0.0        # Tasa éxito esperada de ruta
    risk_score: float = 0.0           # 1.0 - risk_normalized
    quality_score: float = 0.0        # Probabilidad calidad OK
    
    # Score composite
    composite_score: float = 0.0      # Weighted sum de scores
    feasibility_level: str = "Unknown" # FULL, PARTIAL, MARGINAL, INFEASIBLE
    
    # Detalles
    failed_metrics: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    evaluation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RouteScoringProfile:
    """Perfil de scoring específico por SourceRoute"""
    route: SourceRoute
    route_name: str
    
    # Parámetros de scoring
    base_success_rate: float = 0.8    # Tasa éxito base de ruta
    cost_volatility: float = 0.1      # Variabilidad de costo (±%)
    lead_time_variability: float = 2.0 # Variabilidad LT (±días)
    
    # Pesos por métrica (normalizados a 1.0)
    weight_success: float = 0.25
    weight_lead_time: float = 0.35
    weight_cost: float = 0.25
    weight_risk: float = 0.15
    
    # Thresholds
    acceptable_cost_premium: float = 0.2    # 20% sobre costo mínimo
    critical_lead_time_margin: float = 2.0  # ±2 días margen crítico
    min_quality_acceptable: float = 0.95    # 95% quality mínimo
    
    # Contextos óptimos
    optimal_for: List[str] = field(default_factory=list)  # ["high_criticality", "short_lead_time"]


class PathEvaluator:
    """Evaluador de viabilidad de caminos de ejecución"""
    
    def __init__(self):
        """Inicializa evaluador con perfiles de rutas estándar"""
        self.route_profiles = self._initialize_route_profiles()
        self.evaluation_cache: Dict[str, FeasibilityScore] = {}
    
    def _initialize_route_profiles(self) -> Dict[SourceRoute, RouteScoringProfile]:
        """Crea perfiles de scoring para cada ruta operativa"""
        profiles = {}
        
        # Ruta 1: Stock Local - Alta disponibilidad, bajo costo
        profiles[SourceRoute.STOCK_LOCAL] = RouteScoringProfile(
            route=SourceRoute.STOCK_LOCAL,
            route_name="Stock Local",
            base_success_rate=0.95,
            cost_volatility=0.05,
            lead_time_variability=0.5,
            weight_success=0.3, weight_lead_time=0.2, weight_cost=0.35, weight_risk=0.15,
            acceptable_cost_premium=0.05,
            critical_lead_time_margin=0.5,
            min_quality_acceptable=0.99,
            optimal_for=["all_criticality", "immediate_need", "cost_sensitive"]
        )
        
        # Ruta 2: Stock Local + Assets - Intermedio, requiere validation
        profiles[SourceRoute.STOCK_LOCAL_ASSETS] = RouteScoringProfile(
            route=SourceRoute.STOCK_LOCAL_ASSETS,
            route_name="Stock Local + Assets",
            base_success_rate=0.85,
            cost_volatility=0.08,
            lead_time_variability=1.0,
            weight_success=0.25, weight_lead_time=0.25, weight_cost=0.3, weight_risk=0.2,
            acceptable_cost_premium=0.1,
            critical_lead_time_margin=1.0,
            min_quality_acceptable=0.97,
            optimal_for=["medium_criticality", "short_term"]
        )
        
        # Ruta 3: Disassembly - Complejo, requiere knapsack
        profiles[SourceRoute.DISASSEMBLY] = RouteScoringProfile(
            route=SourceRoute.DISASSEMBLY,
            route_name="Disassembly",
            base_success_rate=0.70,
            cost_volatility=0.15,
            lead_time_variability=3.0,
            weight_success=0.2, weight_lead_time=0.3, weight_cost=0.35, weight_risk=0.15,
            acceptable_cost_premium=0.25,
            critical_lead_time_margin=2.0,
            min_quality_acceptable=0.92,
            optimal_for=["high_complexity", "available_parent_components"]
        )
        
        # Ruta 4: Substitutes - Requiere análisis grafo
        profiles[SourceRoute.SUBSTITUTES] = RouteScoringProfile(
            route=SourceRoute.SUBSTITUTES,
            route_name="Substitutes",
            base_success_rate=0.75,
            cost_volatility=0.12,
            lead_time_variability=2.5,
            weight_success=0.25, weight_lead_time=0.25, weight_cost=0.3, weight_risk=0.2,
            acceptable_cost_premium=0.15,
            critical_lead_time_margin=1.5,
            min_quality_acceptable=0.94,
            optimal_for=["non_critical", "technical_flexibility"]
        )
        
        # Ruta 5: Recovery - Reutilización, bajo costo pero lento
        profiles[SourceRoute.RECOVERY] = RouteScoringProfile(
            route=SourceRoute.RECOVERY,
            route_name="Recovery",
            base_success_rate=0.60,
            cost_volatility=0.20,
            lead_time_variability=5.0,
            weight_success=0.15, weight_lead_time=0.35, weight_cost=0.35, weight_risk=0.15,
            acceptable_cost_premium=0.50,
            critical_lead_time_margin=3.0,
            min_quality_acceptable=0.90,
            optimal_for=["low_criticality", "flexible_deadline", "cost_driven"]
        )
        
        # Ruta 6: Transfer - Transferencia inter-almacenes
        profiles[SourceRoute.TRANSFER] = RouteScoringProfile(
            route=SourceRoute.TRANSFER,
            route_name="Transfer",
            base_success_rate=0.88,
            cost_volatility=0.10,
            lead_time_variability=2.0,
            weight_success=0.25, weight_lead_time=0.30, weight_cost=0.25, weight_risk=0.2,
            acceptable_cost_premium=0.12,
            critical_lead_time_margin=1.5,
            min_quality_acceptable=0.97,
            optimal_for=["multi_site_network", "balanced_inventory"]
        )
        
        # Ruta 7: Intercompany - Compra inter-compañía
        profiles[SourceRoute.INTERCOMPANY] = RouteScoringProfile(
            route=SourceRoute.INTERCOMPANY,
            route_name="Intercompany",
            base_success_rate=0.82,
            cost_volatility=0.08,
            lead_time_variability=1.5,
            weight_success=0.25, weight_lead_time=0.25, weight_cost=0.3, weight_risk=0.2,
            acceptable_cost_premium=0.10,
            critical_lead_time_margin=1.0,
            min_quality_acceptable=0.96,
            optimal_for=["corporate_network", "transfer_pricing_advantage"]
        )
        
        # Ruta 8: VMI - Vendor-managed inventory
        profiles[SourceRoute.VMI] = RouteScoringProfile(
            route=SourceRoute.VMI,
            route_name="VMI",
            base_success_rate=0.90,
            cost_volatility=0.06,
            lead_time_variability=1.0,
            weight_success=0.30, weight_lead_time=0.25, weight_cost=0.25, weight_risk=0.2,
            acceptable_cost_premium=0.08,
            critical_lead_time_margin=0.8,
            min_quality_acceptable=0.98,
            optimal_for=["contract_active", "predictable_demand", "quality_critical"]
        )
        
        # Ruta 9: Loan - Préstamo de otra parte
        profiles[SourceRoute.LOAN] = RouteScoringProfile(
            route=SourceRoute.LOAN,
            route_name="Loan",
            base_success_rate=0.65,
            cost_volatility=0.25,
            lead_time_variability=2.5,
            weight_success=0.20, weight_lead_time=0.30, weight_cost=0.20, weight_risk=0.3,
            acceptable_cost_premium=0.30,
            critical_lead_time_margin=2.0,
            min_quality_acceptable=0.93,
            optimal_for=["emergency_only", "relationship_based"]
        )
        
        # Ruta 10: Expedite - Acelerar entrega
        profiles[SourceRoute.EXPEDITE] = RouteScoringProfile(
            route=SourceRoute.EXPEDITE,
            route_name="Expedite",
            base_success_rate=0.75,
            cost_volatility=0.30,
            lead_time_variability=1.0,
            weight_success=0.20, weight_lead_time=0.40, weight_cost=0.25, weight_risk=0.15,
            acceptable_cost_premium=0.50,
            critical_lead_time_margin=0.5,
            min_quality_acceptable=0.95,
            optimal_for=["high_criticality", "tight_deadline", "expedite_budget"]
        )
        
        # Ruta 11: Purchase - Compra estándar
        profiles[SourceRoute.PURCHASE] = RouteScoringProfile(
            route=SourceRoute.PURCHASE,
            route_name="Purchase",
            base_success_rate=0.85,
            cost_volatility=0.10,
            lead_time_variability=3.0,
            weight_success=0.20, weight_lead_time=0.30, weight_cost=0.35, weight_risk=0.15,
            acceptable_cost_premium=0.20,
            critical_lead_time_margin=2.0,
            min_quality_acceptable=0.96,
            optimal_for=["standard_sourcing", "supplier_qualified"]
        )
        
        # Ruta 12: Final Result - Resultado final
        profiles[SourceRoute.FINAL_RESULT] = RouteScoringProfile(
            route=SourceRoute.FINAL_RESULT,
            route_name="Final Result",
            base_success_rate=1.0,
            cost_volatility=0.0,
            lead_time_variability=0.0,
            weight_success=1.0,
            optimal_for=["all"]
        )
        
        return profiles
    
    def evaluate_path(
        self,
        path: ExecutionPath,
        required_date: datetime,
        max_budget: float,
        criticality: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> FeasibilityScore:
        """
        Evalúa viabilidad detallada de un camino de ejecución
        
        Args:
            path: ExecutionPath a evaluar
            required_date: Fecha requerida de entrega
            max_budget: Presupuesto máximo disponible
            criticality: Nivel criticidad ("low", "medium", "high", "critical")
            context_data: Datos contextuales adicionales (opcional)
        
        Returns:
            FeasibilityScore con evaluación detallada
        """
        score = FeasibilityScore(path_id=path.path_id)
        
        # Obtener perfil de ruta
        if path.final_route not in self.route_profiles:
            score.notes.append(f"Ruta {path.final_route} no tiene perfil definido")
            score.feasibility_level = "INFEASIBLE"
            return score
        
        profile = self.route_profiles[path.final_route]
        score.weights = {
            FeasibilityMetric.SUCCESS: profile.weight_success,
            FeasibilityMetric.LEAD_TIME: profile.weight_lead_time,
            FeasibilityMetric.COST: profile.weight_cost,
            FeasibilityMetric.RISK: profile.weight_risk,
        }
        
        # Evaluación 1: Éxito (path logró resultado?)
        score.metrics[FeasibilityMetric.SUCCESS] = path.final_success
        score.success_score = profile.base_success_rate if path.final_success else 0.0
        
        # Evaluación 2: Lead time
        lead_time_ok = (path.total_lead_time <= (required_date - datetime.now()).days)
        score.metrics[FeasibilityMetric.LEAD_TIME] = lead_time_ok
        days_margin = (required_date - datetime.now()).days - path.total_lead_time
        score.lead_time_score = self._compute_lead_time_score(
            days_margin,
            profile.critical_lead_time_margin
        )
        
        # Evaluación 3: Costo
        cost_ok = (path.total_cost <= max_budget)
        score.metrics[FeasibilityMetric.COST] = cost_ok
        cost_ratio = path.total_cost / max_budget if max_budget > 0 else 1.0
        score.cost_score = self._compute_cost_score(
            cost_ratio,
            profile.acceptable_cost_premium
        )
        
        # Evaluación 4: Criticality match
        criticality_match = self._check_criticality_match(criticality, profile)
        score.metrics[FeasibilityMetric.CRITICALITY_MATCH] = criticality_match
        
        # Evaluación 5: Disponibilidad
        available = len(path.visited_nodes) > 0  # Simplificado: si visitó nodos, hay disponibilidad
        score.metrics[FeasibilityMetric.AVAILABLE] = available
        
        # Evaluación 6: Riesgo (inverso)
        risk_score = self._compute_risk_score(path, criticality)
        score.risk_score = risk_score
        
        # Evaluación 7: Calidad
        quality_score = profile.min_quality_acceptable
        score.quality_score = quality_score
        
        # Composite score (weighted sum)
        score.composite_score = (
            score.success_score * profile.weight_success +
            score.lead_time_score * profile.weight_lead_time +
            score.cost_score * profile.weight_cost +
            score.risk_score * profile.weight_risk
        )
        
        # Determinar nivel de viabilidad
        failed = [m.value for m, val in score.metrics.items() if not val]
        score.failed_metrics = failed
        
        if not failed:
            score.feasibility_level = "FULL"
        elif len(failed) <= 1:
            score.feasibility_level = "PARTIAL"
        elif len(failed) <= 2:
            score.feasibility_level = "MARGINAL"
        else:
            score.feasibility_level = "INFEASIBLE"
        
        # Generar notas
        if not path.final_success:
            score.notes.append("Ruta no alcanzó nodo final exitoso")
        if not lead_time_ok:
            score.notes.append(f"Lead time {path.total_lead_time}d excede requerimiento")
        if not cost_ok:
            score.notes.append(f"Costo ${path.total_cost} excede presupuesto ${max_budget}")
        
        return score
    
    def _compute_lead_time_score(self, days_margin: float, critical_margin: float) -> float:
        """
        Calcula score de lead time [0, 1]
        - 1.0: margen positivo
        - Decrece con atraso
        - 0.0: atraso > 2*critical_margin
        """
        if days_margin >= 0:
            return 1.0
        elif days_margin >= -critical_margin:
            return 0.5 + (days_margin / critical_margin) * 0.5
        else:
            return max(0.0, 0.5 - (abs(days_margin) / (2 * critical_margin)) * 0.5)
    
    def _compute_cost_score(self, cost_ratio: float, premium_acceptable: float) -> float:
        """
        Calcula score de costo [0, 1]
        - 1.0: cost_ratio <= 1.0 (within budget)
        - Decrece con ratio
        - 0.0: ratio > 1.0 + 2*premium_acceptable
        """
        if cost_ratio <= 1.0:
            return 1.0
        elif cost_ratio <= (1.0 + premium_acceptable):
            excess = cost_ratio - 1.0
            return 1.0 - (excess / premium_acceptable) * 0.5
        else:
            excess = cost_ratio - 1.0
            return max(0.0, 0.5 - (excess / (2 * premium_acceptable)) * 0.5)
    
    def _check_criticality_match(self, criticality: str, profile: RouteScoringProfile) -> bool:
        """Verifica si ruta es compatible con nivel de criticidad"""
        criticality_map = {
            "low": ["low_criticality", "all_criticality", "flexible_deadline"],
            "medium": ["medium_criticality", "all_criticality"],
            "high": ["high_criticality", "all_criticality"],
            "critical": ["critical_only", "high_criticality", "all_criticality", "emergency_only"]
        }
        
        acceptable = criticality_map.get(criticality, ["all_criticality"])
        route_contexts = profile.optimal_for
        
        return any(ctx in route_contexts for ctx in acceptable)
    
    def _compute_risk_score(self, path: ExecutionPath, criticality: str) -> float:
        """Calcula score inverso de riesgo"""
        # Riesgo base = (100 - success_rate) / 100
        base_risk = (100 - (path.node_results.get(path.visited_nodes[-1], (False, []))[0] * 100)) / 100 if path.visited_nodes else 0.5
        
        # Penalización por criticidad
        criticality_penalty = {"low": 0.0, "medium": 0.05, "high": 0.10, "critical": 0.20}.get(criticality, 0.05)
        
        risk = base_risk + criticality_penalty
        return max(0.0, 1.0 - risk)
    
    def compare_paths(
        self,
        paths: List[ExecutionPath],
        required_date: datetime,
        max_budget: float,
        criticality: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[ExecutionPath, float, List[FeasibilityScore]]:
        """
        Compara múltiples caminos y retorna el mejor
        
        Args:
            paths: Lista de ExecutionPath a comparar
            required_date: Fecha requerida
            max_budget: Presupuesto máximo
            criticality: Nivel criticidad
            weights: Pesos customizados (composite, lead_time, cost) - default: balanced
        
        Returns:
            (best_path, best_score, all_scores)
        """
        if not weights:
            weights = {"composite": 0.50, "lead_time": 0.25, "cost": 0.25}
        
        scores = [
            self.evaluate_path(p, required_date, max_budget, criticality)
            for p in paths
        ]
        
        # Calcular score ponderado
        weighted_scores = []
        for score in scores:
            weighted = (
                score.composite_score * weights.get("composite", 0.5) +
                score.lead_time_score * weights.get("lead_time", 0.25) +
                score.cost_score * weights.get("cost", 0.25)
            )
            weighted_scores.append(weighted)
        
        best_idx = weighted_scores.index(max(weighted_scores))
        return paths[best_idx], weighted_scores[best_idx], scores
    
    def rank_paths(
        self,
        paths: List[ExecutionPath],
        required_date: datetime,
        max_budget: float,
        criticality: str
    ) -> List[Tuple[ExecutionPath, FeasibilityScore, float]]:
        """
        Rankea caminos por viabilidad descendente
        
        Returns:
            List[(path, score, rank_position)]
        """
        scores = [
            self.evaluate_path(p, required_date, max_budget, criticality)
            for p in paths
        ]
        
        # Ordenar por composite_score descendente
        ranked = sorted(
            zip(paths, scores),
            key=lambda x: x[1].composite_score,
            reverse=True
        )
        
        return [
            (path, score, i + 1)
            for i, (path, score) in enumerate(ranked)
        ]
    
    def export_feasibility_report(
        self,
        scores: List[FeasibilityScore],
        file_path: str,
        format: str = "json"
    ) -> bool:
        """
        Exporta reporte de viabilidad a archivo
        
        Args:
            scores: Lista de FeasibilityScore a exportar
            file_path: Ruta del archivo
            format: "json" o "csv"
        
        Returns:
            True si exporta exitoso
        """
        try:
            if format == "json":
                data = [
                    {
                        "path_id": s.path_id,
                        "composite_score": s.composite_score,
                        "feasibility_level": s.feasibility_level,
                        "metrics": {m.value: v for m, v in s.metrics.items()},
                        "scores": {
                            "success": s.success_score,
                            "lead_time": s.lead_time_score,
                            "cost": s.cost_score,
                            "risk": s.risk_score,
                            "quality": s.quality_score
                        },
                        "failed_metrics": s.failed_metrics,
                        "notes": s.notes,
                        "timestamp": s.evaluation_timestamp
                    }
                    for s in scores
                ]
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format == "csv":
                import csv
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "path_id", "composite_score", "feasibility_level",
                        "success_score", "lead_time_score", "cost_score", "risk_score"
                    ])
                    writer.writeheader()
                    for s in scores:
                        writer.writerow({
                            "path_id": s.path_id,
                            "composite_score": s.composite_score,
                            "feasibility_level": s.feasibility_level,
                            "success_score": s.success_score,
                            "lead_time_score": s.lead_time_score,
                            "cost_score": s.cost_score,
                            "risk_score": s.risk_score
                        })
            
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
