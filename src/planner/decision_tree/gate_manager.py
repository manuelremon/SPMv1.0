"""
gate_manager.py
Manager centralizado de puertas de decisión (gates)

Módulo responsable de:
- Gestión centralizada de gates del árbol de decisión
- Evaluación personalizada y caching de resultados
- Lógica de apertura/cierre con reglas complejas
- Auditoría y tracking de evaluaciones
- Customización de gates por contexto
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Tuple, Any
from enum import Enum
import json
from datetime import datetime
from functools import lru_cache

from .decision_tree import Gate, GateType
from .execution_engine import ExecutionContext


class GateState(Enum):
    """Estados posibles de una puerta"""
    OPEN = "open"           # Puerta abierta (pasa)
    CLOSED = "closed"       # Puerta cerrada (falla)
    CONDITION_MET = "passed"
    CONDITION_NOT_MET = "failed"
    UNKNOWN = "unknown"


@dataclass
class GateEvaluation:
    """Registro de evaluación de una puerta"""
    gate_id: str
    gate_type: GateType
    state: GateState
    
    # Contexto de evaluación
    context_hash: str                      # Hash del contexto para caching
    condition_result: bool                 # Resultado de la condición
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    
    # Metadata
    evaluation_time_ms: float = 0.0
    notes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evaluator_id: str = "system"


@dataclass
class GateConfiguration:
    """Configuración de una puerta específica"""
    gate_id: str
    gate_type: GateType
    
    # Enabled/disabled
    enabled: bool = True
    severity: str = "normal"  # "critical", "normal", "warning"
    
    # Reglas de evaluación
    rule_type: str = "simple"  # "simple", "compound", "statistical"
    custom_condition: Optional[Callable] = None
    
    # Parámetros
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Contextos
    applicable_contexts: List[str] = field(default_factory=list)  # empty = all
    not_applicable_contexts: List[str] = field(default_factory=list)
    
    # Histórico
    evaluations: List[GateEvaluation] = field(default_factory=list)
    pass_rate: float = 1.0


class GateManager:
    """Manager centralizado para gates del árbol de decisión"""
    
    def __init__(self, max_cache_size: int = 1000):
        """
        Inicializa el manager de gates
        
        Args:
            max_cache_size: Tamaño máximo del cache de evaluaciones
        """
        self.gates: Dict[str, Gate] = {}
        self.configurations: Dict[str, GateConfiguration] = {}
        self.evaluation_cache: Dict[str, GateEvaluation] = {}
        self.max_cache_size = max_cache_size
        self.evaluation_history: List[GateEvaluation] = []
        self.global_rules: Dict[str, Callable] = {}
    
    def register_gate(self, gate: Gate, config: Optional[GateConfiguration] = None) -> None:
        """
        Registra una puerta en el manager
        
        Args:
            gate: Gate a registrar
            config: Configuración opcional de la puerta
        """
        self.gates[gate.gate_id] = gate
        
        if not config:
            config = GateConfiguration(
                gate_id=gate.gate_id,
                gate_type=gate.gate_type
            )
        
        self.configurations[gate.gate_id] = config
    
    def register_global_rule(self, rule_name: str, rule_func: Callable) -> None:
        """
        Registra una regla global aplicable a múltiples gates
        
        Args:
            rule_name: Nombre de la regla
            rule_func: Función que implementa la regla
        """
        self.global_rules[rule_name] = rule_func
    
    def evaluate_gate(
        self,
        gate_id: str,
        context: ExecutionContext,
        use_cache: bool = True
    ) -> Tuple[bool, GateEvaluation]:
        """
        Evalúa una puerta individual
        
        Args:
            gate_id: ID de la puerta
            context: Contexto de ejecución
            use_cache: Si usa caching
        
        Returns:
            (resultado_booleano, GateEvaluation)
        """
        if gate_id not in self.gates:
            return False, GateEvaluation(
                gate_id=gate_id,
                gate_type=GateType.COMPLEX,
                state=GateState.UNKNOWN,
                context_hash="",
                condition_result=False,
                notes=["Gate no registrado"]
            )
        
        gate = self.gates[gate_id]
        config = self.configurations.get(gate_id)
        
        # Verificar si puerta está enabled
        if config and not config.enabled:
            evaluation = GateEvaluation(
                gate_id=gate_id,
                gate_type=gate.gate_type,
                state=GateState.OPEN,
                context_hash=self._hash_context(context),
                condition_result=True,
                notes=["Puerta deshabilitada (bypass)"]
            )
            return True, evaluation
        
        # Generar context hash para caching
        context_hash = self._hash_context(context)
        cache_key = f"{gate_id}:{context_hash}"
        
        # Buscar en cache
        if use_cache and cache_key in self.evaluation_cache:
            cached = self.evaluation_cache[cache_key]
            return cached.condition_result, cached
        
        # Evaluar
        try:
            result = gate.evaluate(context)
            
            # Crear evaluation record
            evaluation = GateEvaluation(
                gate_id=gate_id,
                gate_type=gate.gate_type,
                state=GateState.OPEN if result else GateState.CLOSED,
                context_hash=context_hash,
                condition_result=result,
                notes=[f"Umbral: {gate.threshold}" if gate.threshold else "Condición custom"]
            )
            
            # Cachear
            if len(self.evaluation_cache) < self.max_cache_size:
                self.evaluation_cache[cache_key] = evaluation
            
            # Registrar en histórico
            if config:
                config.evaluations.append(evaluation)
                self._update_pass_rate(config)
            
            self.evaluation_history.append(evaluation)
            
            return result, evaluation
        
        except Exception as e:
            evaluation = GateEvaluation(
                gate_id=gate_id,
                gate_type=gate.gate_type,
                state=GateState.UNKNOWN,
                context_hash=context_hash,
                condition_result=False,
                notes=[f"Error en evaluación: {str(e)}"]
            )
            return False, evaluation
    
    def evaluate_gates_batch(
        self,
        gate_ids: List[str],
        context: ExecutionContext,
        stop_on_fail: bool = False
    ) -> Tuple[bool, List[GateEvaluation]]:
        """
        Evalúa múltiples puertas
        
        Args:
            gate_ids: IDs de puertas a evaluar
            context: Contexto de ejecución
            stop_on_fail: Si detiene al primer fallo
        
        Returns:
            (todos_pasaron, lista_evaluaciones)
        """
        all_pass = True
        evaluations = []
        
        for gate_id in gate_ids:
            result, evaluation = self.evaluate_gate(gate_id, context)
            evaluations.append(evaluation)
            
            if not result:
                all_pass = False
                if stop_on_fail:
                    break
        
        return all_pass, evaluations
    
    def evaluate_with_fallback(
        self,
        gate_id: str,
        context: ExecutionContext,
        fallback_gate_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, GateEvaluation]]:
        """
        Evalúa con fallback si primera puerta falla
        
        Args:
            gate_id: ID de puerta principal
            context: Contexto de ejecución
            fallback_gate_id: ID de puerta alternativa (opcional)
        
        Returns:
            (resultado, {principal: eval, fallback: eval})
        """
        result, main_eval = self.evaluate_gate(gate_id, context)
        
        evals = {gate_id: main_eval}
        
        if not result and fallback_gate_id:
            fallback_result, fallback_eval = self.evaluate_gate(fallback_gate_id, context)
            evals[fallback_gate_id] = fallback_eval
            result = fallback_result
        
        return result, evals
    
    def apply_global_rule(
        self,
        rule_name: str,
        gate_ids: List[str],
        context: ExecutionContext
    ) -> Tuple[bool, List[GateEvaluation]]:
        """
        Aplica una regla global a múltiples puertas
        
        Args:
            rule_name: Nombre de la regla
            gate_ids: IDs de puertas donde aplicar
            context: Contexto de ejecución
        
        Returns:
            (resultado_global, evaluaciones)
        """
        if rule_name not in self.global_rules:
            return False, []
        
        rule_func = self.global_rules[rule_name]
        evaluations = []
        
        # Evaluar todas las puertas
        for gate_id in gate_ids:
            result, evaluation = self.evaluate_gate(gate_id, context)
            evaluations.append(evaluation)
        
        # Aplicar regla global
        global_result = rule_func(evaluations, context)
        
        return global_result, evaluations
    
    def get_gate_statistics(self, gate_id: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de evaluación de una puerta
        
        Returns:
            Dict con estadísticas
        """
        config = self.configurations.get(gate_id)
        if not config:
            return {}
        
        total = len(config.evaluations)
        passed = sum(1 for e in config.evaluations if e.condition_result)
        failed = total - passed
        
        return {
            "gate_id": gate_id,
            "total_evaluations": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "last_evaluation": config.evaluations[-1].timestamp if config.evaluations else None,
            "enabled": config.enabled,
            "severity": config.severity
        }
    
    def get_all_statistics(self) -> List[Dict[str, Any]]:
        """Obtiene estadísticas de todas las puertas"""
        return [self.get_gate_statistics(gid) for gid in self.gates.keys()]
    
    def clear_cache(self) -> None:
        """Limpia el cache de evaluaciones"""
        self.evaluation_cache.clear()
    
    def export_audit_log(self, file_path: str, format: str = "json") -> bool:
        """
        Exporta log de auditoría de evaluaciones
        
        Args:
            file_path: Ruta del archivo
            format: "json" o "csv"
        
        Returns:
            True si exporta exitoso
        """
        try:
            if format == "json":
                data = [
                    {
                        "gate_id": e.gate_id,
                        "gate_type": e.gate_type.value,
                        "state": e.state.value,
                        "condition_result": e.condition_result,
                        "timestamp": e.timestamp,
                        "notes": e.notes
                    }
                    for e in self.evaluation_history
                ]
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format == "csv":
                import csv
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "gate_id", "gate_type", "state", "condition_result", "timestamp"
                    ])
                    writer.writeheader()
                    for e in self.evaluation_history:
                        writer.writerow({
                            "gate_id": e.gate_id,
                            "gate_type": e.gate_type.value,
                            "state": e.state.value,
                            "condition_result": e.condition_result,
                            "timestamp": e.timestamp
                        })
            
            return True
        except Exception as e:
            print(f"Error exporting audit log: {e}")
            return False
    
    def _hash_context(self, context: ExecutionContext) -> str:
        """
        Genera hash del contexto para caching
        
        Args:
            context: ExecutionContext
        
        Returns:
            String hash del contexto
        """
        context_str = f"{context.item_id}:{context.demand_quantity}:{context.days_to_deadline}"
        return str(hash(context_str))
    
    def _update_pass_rate(self, config: GateConfiguration) -> None:
        """Actualiza la tasa de paso de una configuración"""
        if config.evaluations:
            passed = sum(1 for e in config.evaluations if e.condition_result)
            config.pass_rate = passed / len(config.evaluations)


class AdvancedGateEvaluator:
    """Evaluador avanzado de gates con lógica compleja"""
    
    def __init__(self, manager: GateManager):
        """
        Inicializa evaluador avanzado
        
        Args:
            manager: GateManager a usar
        """
        self.manager = manager
    
    def evaluate_with_context_adaptation(
        self,
        gate_ids: List[str],
        context: ExecutionContext,
        context_type: str
    ) -> Tuple[bool, List[GateEvaluation]]:
        """
        Evalúa puertas adaptando thresholds según tipo de contexto
        
        Args:
            gate_ids: IDs de puertas
            context: Contexto de ejecución
            context_type: Tipo de contexto ("urgent", "high_volume", "low_cost", etc)
        
        Returns:
            (resultado, evaluaciones)
        """
        # Adaptar thresholds según context_type
        threshold_adjustments = {
            "urgent": {"lead_time": 0.5, "cost": 1.2, "availability": 1.0},
            "high_volume": {"lead_time": 1.0, "cost": 0.9, "availability": 1.5},
            "low_cost": {"lead_time": 1.2, "cost": 0.7, "availability": 1.0},
            "high_quality": {"lead_time": 1.0, "cost": 1.0, "availability": 0.8}
        }
        
        adjustments = threshold_adjustments.get(context_type, {})
        
        # Aplicar ajustes (simplificado - en producción habría más lógica)
        evaluations = []
        all_pass = True
        
        for gate_id in gate_ids:
            result, evaluation = self.manager.evaluate_gate(gate_id, context)
            evaluations.append(evaluation)
            if not result:
                all_pass = False
        
        return all_pass, evaluations
    
    def evaluate_with_severity_levels(
        self,
        gate_configs: Dict[str, GateConfiguration],
        context: ExecutionContext
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evalúa considerando niveles de severidad
        
        Args:
            gate_configs: Dict de configuraciones de gates
            context: Contexto de ejecución
        
        Returns:
            (resultado, resumen_por_severidad)
        """
        result_by_severity = {
            "critical": [],
            "normal": [],
            "warning": []
        }
        
        for gate_id, config in gate_configs.items():
            result, evaluation = self.manager.evaluate_gate(gate_id, context)
            result_by_severity[config.severity].append({
                "gate_id": gate_id,
                "result": result,
                "evaluation": evaluation
            })
        
        # Determine overall result
        critical_pass = all(r["result"] for r in result_by_severity["critical"])
        overall_pass = critical_pass
        
        return overall_pass, result_by_severity
