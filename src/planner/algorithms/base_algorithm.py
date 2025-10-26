"""
Arquitectura Base para Algoritmos de Optimización por Vía

Patrón Strategy con arquitectura común para todos los algoritmos:
- Interfaz base: BaseAlgorithm
- Registry dinámico: AlgorithmRegistry
- Ejecutor: AlgorithmExecutor
- Context compartido: AlgorithmContext
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlgorithmType(Enum):
    """Tipos de algoritmos por vía de abastecimiento"""
    RESERVE_DYNAMIC = "reserve_dynamic"              # Stock local
    RELEASE_MARGINAL = "release_marginal_cost"      # Liberación
    DISASSEMBLY_KNAPSACK = "disassembly_knapsack"   # Desarme
    SUBSTITUTES_GRAPH = "substitutes_graph"          # Sustitutos
    CTP_JOHNSON = "ctp_johnson"                       # CTP
    TRANSFER_TDABC = "transfer_tdabc"                 # Transferencias
    EXPEDITE_PROBABILITY = "expedite_probability"    # Aceleración
    PURCHASE_MULTICRITERION = "purchase_multicriterion"  # Compra


class AlgorithmStatus(Enum):
    """Estados de ejecución del algoritmo"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AlgorithmInput:
    """Input estándar para todos los algoritmos"""
    item_id: str
    demand_quantity: float
    required_date: str
    
    # Contexto de inventario
    local_stock: Dict[str, float] = field(default_factory=dict)
    local_assets: Dict[str, float] = field(default_factory=dict)
    bom_components: Dict[str, float] = field(default_factory=dict)
    
    # Contexto operativo
    criticality: str = "MEDIUM"
    budget_available: float = float('inf')
    max_acceptable_cost: float = float('inf')
    
    # Metadata
    execution_context: Optional[Dict[str, Any]] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlgorithmOutput:
    """Output estándar para todos los algoritmos"""
    algorithm_type: AlgorithmType
    item_id: str
    success: bool
    status: AlgorithmStatus
    
    # Resultado
    selected_option: Optional[Any] = None
    proposed_quantity: float = 0.0
    estimated_cost: float = 0.0
    estimated_lead_time: int = 0
    confidence_score: float = 0.0
    
    # Trazabilidad
    reasoning: str = ""
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_ms: float = 0.0
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None


class BaseAlgorithm(ABC):
    """
    Clase base para todos los algoritmos de optimización.
    
    Interfaz común que deben implementar:
    - validate_input(): Validación de entrada
    - execute(): Lógica principal
    - get_metadata(): Información del algoritmo
    """
    
    def __init__(self, algorithm_type: AlgorithmType):
        """Inicializa algoritmo base"""
        self.algorithm_type = algorithm_type
        self.logger = logger
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    @abstractmethod
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """
        Valida que el input sea compatible con el algoritmo.
        
        Returns:
            (valid, error_message)
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        Ejecuta el algoritmo.
        
        Args:
            input_data: Input estructurado
        
        Returns:
            AlgorithmOutput con resultado
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadata del algoritmo"""
        return {
            "type": self.algorithm_type.value,
            "execution_count": self.execution_count,
            "avg_execution_time_ms": (
                self.total_execution_time / self.execution_count
                if self.execution_count > 0 else 0
            ),
            "total_execution_time_ms": self.total_execution_time
        }
    
    def run(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        Wrapper que ejecuta el algoritmo con validación y telemetría.
        """
        import time
        
        start_time = time.time()
        
        try:
            # 1. Validar input
            valid, error_msg = self.validate_input(input_data)
            if not valid:
                self.logger.warning(f"Input validation failed: {error_msg}")
                return AlgorithmOutput(
                    algorithm_type=self.algorithm_type,
                    item_id=input_data.item_id,
                    success=False,
                    status=AlgorithmStatus.FAILED,
                    error_message=error_msg,
                    reasoning=f"Validación fallida: {error_msg}"
                )
            
            # 2. Ejecutar
            self.logger.info(f"Ejecutando {self.algorithm_type.value} para {input_data.item_id}")
            output = self.execute(input_data)
            output.status = AlgorithmStatus.COMPLETED
            
            # 3. Registrar telemetría
            execution_time_ms = (time.time() - start_time) * 1000
            output.execution_time_ms = execution_time_ms
            self.execution_count += 1
            self.total_execution_time += execution_time_ms
            
            self.logger.info(f"Algoritmo completado en {execution_time_ms:.2f}ms")
            
            return output
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Error en algoritmo: {str(e)}", exc_info=True)
            
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time_ms
            )


class AlgorithmRegistry:
    """
    Registry dinámico para registrar e invocar algoritmos.
    
    Patrón Factory con soporte para descubrimiento dinámico.
    """
    
    def __init__(self):
        """Inicializa registry"""
        self._algorithms: Dict[AlgorithmType, BaseAlgorithm] = {}
        self.logger = logger
    
    def register(self, algorithm: BaseAlgorithm) -> None:
        """Registra un algoritmo"""
        self._algorithms[algorithm.algorithm_type] = algorithm
        self.logger.info(f"Algoritmo registrado: {algorithm.algorithm_type.value}")
    
    def unregister(self, algorithm_type: AlgorithmType) -> None:
        """Desregistra un algoritmo"""
        if algorithm_type in self._algorithms:
            del self._algorithms[algorithm_type]
            self.logger.info(f"Algoritmo desregistrado: {algorithm_type.value}")
    
    def get(self, algorithm_type: AlgorithmType) -> Optional[BaseAlgorithm]:
        """Obtiene un algoritmo registrado"""
        return self._algorithms.get(algorithm_type)
    
    def list_algorithms(self) -> List[Dict[str, Any]]:
        """Lista todos los algoritmos registrados"""
        return [
            {
                "type": algo.algorithm_type.value,
                "metadata": algo.get_metadata()
            }
            for algo in self._algorithms.values()
        ]
    
    def is_registered(self, algorithm_type: AlgorithmType) -> bool:
        """Verifica si un algoritmo está registrado"""
        return algorithm_type in self._algorithms


class AlgorithmExecutor:
    """
    Ejecutor de algoritmos con soporte para:
    - Selección automática
    - Fallback a alternativa
    - Estrategia de composición
    """
    
    def __init__(self, registry: AlgorithmRegistry):
        """Inicializa executor"""
        self.registry = registry
        self.logger = logger
    
    def execute(
        self,
        algorithm_type: AlgorithmType,
        input_data: AlgorithmInput,
        fallback_type: Optional[AlgorithmType] = None
    ) -> AlgorithmOutput:
        """
        Ejecuta un algoritmo con fallback opcional.
        
        Args:
            algorithm_type: Tipo de algoritmo a ejecutar
            input_data: Input del algoritmo
            fallback_type: Algoritmo alternativo si el primero falla
        
        Returns:
            AlgorithmOutput
        """
        # 1. Obtener algoritmo
        algorithm = self.registry.get(algorithm_type)
        if algorithm is None:
            self.logger.error(f"Algoritmo no encontrado: {algorithm_type.value}")
            return AlgorithmOutput(
                algorithm_type=algorithm_type,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                error_message=f"Algoritmo no registrado: {algorithm_type.value}"
            )
        
        # 2. Ejecutar
        output = algorithm.run(input_data)
        
        # 3. Fallback si es necesario
        if not output.success and fallback_type:
            self.logger.info(f"Fallback a {fallback_type.value}")
            fallback_algo = self.registry.get(fallback_type)
            if fallback_algo:
                output = fallback_algo.run(input_data)
        
        return output
    
    def execute_parallel(
        self,
        algorithm_types: List[AlgorithmType],
        input_data: AlgorithmInput,
        select_best: bool = True
    ) -> List[AlgorithmOutput]:
        """
        Ejecuta múltiples algoritmos en paralelo.
        
        Args:
            algorithm_types: Lista de tipos de algoritmos
            input_data: Input compartido
            select_best: Si True, retorna solo el mejor resultado
        
        Returns:
            Lista de outputs o el mejor si select_best=True
        """
        outputs = []
        for algo_type in algorithm_types:
            output = self.execute(algo_type, input_data)
            outputs.append(output)
        
        if select_best:
            # Ranking por confidence score
            outputs.sort(
                key=lambda o: (o.success, o.confidence_score),
                reverse=True
            )
        
        return outputs


# Instancias globales
_registry = AlgorithmRegistry()
_executor = AlgorithmExecutor(_registry)


def get_registry() -> AlgorithmRegistry:
    """Obtiene el registry global"""
    return _registry


def get_executor() -> AlgorithmExecutor:
    """Obtiene el executor global"""
    return _executor


def register_algorithm(algorithm: BaseAlgorithm) -> None:
    """Registra un algoritmo en el registry global"""
    _registry.register(algorithm)


def execute_algorithm(
    algorithm_type: AlgorithmType,
    input_data: AlgorithmInput,
    fallback_type: Optional[AlgorithmType] = None
) -> AlgorithmOutput:
    """Ejecuta un algoritmo usando el executor global"""
    return _executor.execute(algorithm_type, input_data, fallback_type)
