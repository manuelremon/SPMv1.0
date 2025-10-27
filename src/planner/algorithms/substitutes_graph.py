"""
Algoritmo #4: Substitutes Graph Search
========================================
Busca items equivalentes/sustitutos en un grafo de equivalencias.

Responsabilidad:
- Dado un item, encontrar alternativas técnicamente compatibles
- Objetivo: Maximizar disponibilidad minimizando costo/impacto técnico
- Estrategia: DFS/BFS en grafo de equivalencias con restricciones

Aplicación en supply chain:
- Cuando no hay stock del item original
- Encontrar sustitutos técnicamente compatibles
- Evaluar trade-off: compatibilidad vs costo vs disponibilidad

Complejidad: O(V+E) donde V=nodos (items), E=aristas (equivalencias)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Set
from collections import deque
from datetime import datetime

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)


class SearchStrategy(str, Enum):
    """Estrategia de búsqueda en grafo"""
    DFS = "dfs"  # Depth-First Search (exploración profunda)
    BFS = "bfs"  # Breadth-First Search (exploración por niveles)


@dataclass
class EquivalentNode:
    """Nodo en grafo de equivalencias"""
    item_id: str
    description: str
    technical_compatibility: float  # 0-1, qué tan compatible es
    cost_differential: float         # +5% = más caro, -10% = más barato
    supplier_reliability: float      # 0-1, confiabilidad proveedor
    lead_time_delta: int             # días vs item original
    availability: float              # 0-1, disponibilidad estimada
    is_original: bool = False


@dataclass
class SubstituteOption:
    """Opción de sustituto evaluada"""
    item_id: str
    search_depth: int
    path: List[str]                  # Ruta en el grafo
    technical_score: float           # 0-1
    cost_score: float                # 0-1 (lower cost = higher score)
    reliability_score: float         # 0-1
    overall_score: float             # 0-1 (agregado)
    recommendation: str
    alternatives_count: int


@dataclass
class GraphAnalysis:
    """Resultado del análisis de grafo"""
    search_strategy: SearchStrategy
    total_nodes_explored: int
    total_edges_explored: int
    max_depth: int
    best_substitute: Optional[SubstituteOption]
    alternatives_found: List[SubstituteOption] = field(default_factory=list)
    confidence_score: float = 0.0


class SubstitutesGraphAlgorithm(BaseAlgorithm):
    """
    Busca items equivalentes en un grafo usando DFS/BFS.
    
    Entrada:
    - item_id: str (item original)
    - demand_quantity: float
    - criticality: str (affects search aggressiveness)
    
    Salida:
    - proposed_quantity: float (cantidad del sustituto)
    - confidence_score: 0-1 (compatibilidad técnica)
    - selected_option: str ("substitute_found/no_substitute")
    """
    
    def __init__(self):
        super().__init__(AlgorithmType.SUBSTITUTES_GRAPH)
        self.execution_history: List[Dict] = []
        self.search_strategy = SearchStrategy.BFS  # Default
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida entrada del algoritmo"""
        if not input_data.item_id:
            return False, "item_id requerido"
        if input_data.demand_quantity <= 0:
            return False, "demand_quantity debe ser > 0"
        return True, "OK"
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        Ejecuta búsqueda de sustitutos en grafo.
        
        Pasos:
        1. Validar entrada
        2. Construir grafo de equivalencias (mock)
        3. Seleccionar estrategia de búsqueda (DFS/BFS según criticality)
        4. Ejecutar búsqueda con constraints
        5. Evaluar alternativas encontradas
        6. Calcular confidence basado en compatibilidad
        7. Retornar resultado
        """
        start_time = datetime.now()
        
        # 1. Validar
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                proposed_quantity=0,
                confidence_score=0.0,
                reasoning=error_msg
            )
        
        try:
            # 2. Construir grafo
            graph = self._build_equivalence_graph(input_data)
            
            if not graph:
                return AlgorithmOutput(
                    algorithm_type=self.algorithm_type,
                    item_id=input_data.item_id,
                    success=True,
                    status=AlgorithmStatus.COMPLETED,
                    proposed_quantity=0,
                    confidence_score=0.0,
                    reasoning="No hay equivalentes disponibles en grafo",
                    selected_option="substitute_none"
                )
            
            # 3. Seleccionar estrategia
            self.search_strategy = self._select_search_strategy(input_data)
            
            # 4. Ejecutar búsqueda
            if self.search_strategy == SearchStrategy.DFS:
                analysis = self._search_dfs(input_data.item_id, graph, input_data)
            else:
                analysis = self._search_bfs(input_data.item_id, graph, input_data)
            
            # 5. Evaluar alternativas
            best_option = self._evaluate_alternatives(analysis, input_data)
            
            if not best_option:
                return AlgorithmOutput(
                    algorithm_type=self.algorithm_type,
                    item_id=input_data.item_id,
                    success=True,
                    status=AlgorithmStatus.COMPLETED,
                    proposed_quantity=0,
                    confidence_score=0.0,
                    reasoning="Búsqueda completada pero sin sustitutos viables",
                    selected_option="substitute_none"
                )
            
            # 6. Calcular confidence
            confidence = self._calculate_confidence(best_option, analysis, input_data)
            
            # 7. Preparar reasoning
            reasoning = self._generate_reasoning(best_option, analysis)
            
            # Guardar historial
            self.execution_count += 1
            self.execution_history.append({
                "item_id": input_data.item_id,
                "substitute_id": best_option.item_id,
                "technical_score": best_option.technical_score,
                "confidence": confidence,
                "timestamp": start_time.isoformat()
            })
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                proposed_quantity=input_data.demand_quantity,
                confidence_score=confidence,
                reasoning=reasoning,
                selected_option="substitute_found",
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                proposed_quantity=0,
                confidence_score=0.0,
                reasoning=f"Error en búsqueda de grafo: {str(e)}"
            )
    
    def get_metadata(self) -> Dict:
        """Retorna metadata del algoritmo"""
        return {
            "type": self.algorithm_type.value,
            "execution_count": self.execution_count,
            "algorithm_name": "SubstitutesGraph",
            "description": "DFS/BFS graph search para encontrar items equivalentes",
            "complexity": "O(V+E) graph traversal",
            "search_strategy": self.search_strategy.value,
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    # ===== Métodos Privados =====
    
    def _build_equivalence_graph(self, input_data: AlgorithmInput) -> Dict[str, List[EquivalentNode]]:
        """
        Construye grafo de equivalencias (mock).
        En producción: consultaría base de datos de equivalencias.
        """
        # Grafo de ejemplo: item_id → [lista de equivalentes]
        graph = {
            "ITEM-001": [
                EquivalentNode(
                    item_id="ITEM-001",
                    description="Item original",
                    technical_compatibility=1.0,
                    cost_differential=0.0,
                    supplier_reliability=0.95,
                    lead_time_delta=0,
                    availability=0.6,
                    is_original=True
                ),
                EquivalentNode(
                    item_id="EQUIV-001-A",
                    description="Equivalente nivel 1",
                    technical_compatibility=0.95,
                    cost_differential=-0.05,
                    supplier_reliability=0.90,
                    lead_time_delta=2,
                    availability=0.85
                ),
                EquivalentNode(
                    item_id="EQUIV-001-B",
                    description="Equivalente nivel 1",
                    technical_compatibility=0.85,
                    cost_differential=0.10,
                    supplier_reliability=0.92,
                    lead_time_delta=1,
                    availability=0.92
                ),
            ],
            "EQUIV-001-A": [
                EquivalentNode(
                    item_id="EQUIV-001-A-I",
                    description="Equivalente nivel 2",
                    technical_compatibility=0.80,
                    cost_differential=-0.15,
                    supplier_reliability=0.85,
                    lead_time_delta=5,
                    availability=0.75
                ),
            ],
            "EQUIV-001-B": [
                EquivalentNode(
                    item_id="EQUIV-001-B-I",
                    description="Equivalente nivel 2",
                    technical_compatibility=0.75,
                    cost_differential=0.20,
                    supplier_reliability=0.88,
                    lead_time_delta=3,
                    availability=0.88
                ),
            ]
        }
        
        return graph if input_data.item_id == "ITEM-001" else {}
    
    def _select_search_strategy(self, input_data: AlgorithmInput) -> SearchStrategy:
        """
        Selecciona estrategia basado en criticality.
        - CRITICAL: DFS (exploración profunda, máxima compatibilidad)
        - LOW: BFS (exploración ancha, opciones variadas)
        """
        if input_data.criticality in ["CRITICAL", "HIGH"]:
            return SearchStrategy.DFS
        else:
            return SearchStrategy.BFS
    
    def _search_dfs(
        self,
        start_item: str,
        graph: Dict[str, List[EquivalentNode]],
        input_data: AlgorithmInput
    ) -> GraphAnalysis:
        """Búsqueda DFS (profundidad) en grafo"""
        visited: Set[str] = set()
        all_alternatives: List[SubstituteOption] = []
        max_depth_reached = 0
        edges_explored = 0
        
        def dfs_recursive(node_id: str, path: List[str], depth: int):
            nonlocal edges_explored, max_depth_reached
            
            visited.add(node_id)
            max_depth_reached = max(max_depth_reached, depth)
            
            if node_id not in graph:
                return
            
            for neighbor in graph[node_id]:
                edges_explored += 1
                
                if neighbor.item_id not in visited:
                    new_path = path + [neighbor.item_id]
                    
                    # Evaluar este nodo como alternativa
                    if not neighbor.is_original and neighbor.item_id != start_item:
                        option = SubstituteOption(
                            item_id=neighbor.item_id,
                            search_depth=depth,
                            path=new_path,
                            technical_score=neighbor.technical_compatibility,
                            cost_score=1 - abs(neighbor.cost_differential),
                            reliability_score=neighbor.supplier_reliability,
                            overall_score=0.0,
                            recommendation="",
                            alternatives_count=0
                        )
                        all_alternatives.append(option)
                    
                    # Continuar búsqueda
                    dfs_recursive(neighbor.item_id, new_path, depth + 1)
        
        dfs_recursive(start_item, [start_item], 0)
        
        return GraphAnalysis(
            search_strategy=SearchStrategy.DFS,
            total_nodes_explored=len(visited),
            total_edges_explored=edges_explored,
            max_depth=max_depth_reached,
            best_substitute=None,
            alternatives_found=all_alternatives
        )
    
    def _search_bfs(
        self,
        start_item: str,
        graph: Dict[str, List[EquivalentNode]],
        input_data: AlgorithmInput
    ) -> GraphAnalysis:
        """Búsqueda BFS (amplitud) en grafo"""
        visited: Set[str] = set()
        all_alternatives: List[SubstituteOption] = []
        queue = deque([(start_item, [start_item], 0)])
        max_depth_reached = 0
        edges_explored = 0
        
        while queue:
            current_item, path, depth = queue.popleft()
            
            if current_item in visited:
                continue
            
            visited.add(current_item)
            max_depth_reached = max(max_depth_reached, depth)
            
            if current_item not in graph:
                continue
            
            for neighbor in graph[current_item]:
                edges_explored += 1
                
                if neighbor.item_id not in visited:
                    new_path = path + [neighbor.item_id]
                    
                    # Evaluar este nodo como alternativa
                    if not neighbor.is_original and neighbor.item_id != start_item:
                        option = SubstituteOption(
                            item_id=neighbor.item_id,
                            search_depth=depth,
                            path=new_path,
                            technical_score=neighbor.technical_compatibility,
                            cost_score=1 - abs(neighbor.cost_differential),
                            reliability_score=neighbor.supplier_reliability,
                            overall_score=0.0,
                            recommendation="",
                            alternatives_count=0
                        )
                        all_alternatives.append(option)
                    
                    queue.append((neighbor.item_id, new_path, depth + 1))
        
        return GraphAnalysis(
            search_strategy=SearchStrategy.BFS,
            total_nodes_explored=len(visited),
            total_edges_explored=edges_explored,
            max_depth=max_depth_reached,
            best_substitute=None,
            alternatives_found=all_alternatives
        )
    
    def _evaluate_alternatives(
        self,
        analysis: GraphAnalysis,
        input_data: AlgorithmInput
    ) -> Optional[SubstituteOption]:
        """Evalúa alternativas y retorna la mejor"""
        if not analysis.alternatives_found:
            return None
        
        # Calcular overall score para cada alternativa
        for option in analysis.alternatives_found:
            # Ponderado: técnica 50%, confiabilidad 30%, costo 20%
            option.overall_score = (
                option.technical_score * 0.50 +
                option.reliability_score * 0.30 +
                option.cost_score * 0.20
            )
        
        # Aplicar ajuste por criticidad
        if input_data.criticality == "CRITICAL":
            # Prioriza compatibilidad técnica
            for option in analysis.alternatives_found:
                option.overall_score = option.technical_score * 0.70 + (option.overall_score * 0.30)
        elif input_data.criticality == "LOW":
            # Prioriza costo
            for option in analysis.alternatives_found:
                option.overall_score = option.cost_score * 0.50 + (option.overall_score * 0.50)
        
        # Retornar mejor opción
        best = max(analysis.alternatives_found, key=lambda x: x.overall_score)
        best.alternatives_count = len(analysis.alternatives_found)
        best.recommendation = "Sustituto óptimo encontrado"
        
        return best
    
    def _calculate_confidence(
        self,
        option: SubstituteOption,
        analysis: GraphAnalysis,
        input_data: AlgorithmInput
    ) -> float:
        """
        Calcula confidence score (0-1).
        
        Factores:
        - Compatibilidad técnica (50%)
        - Profundidad búsqueda (30%)
        - Overall score (20%)
        """
        # Compatibilidad técnica (50%)
        tech_score = option.technical_score * 0.50
        
        # Profundidad (30%) - nodos cercanos = más confianza
        depth_normalized = 1 - min(option.search_depth / 5, 1.0)  # Penaliza profundidad
        depth_score = depth_normalized * 0.30
        
        # Overall score (20%)
        overall_component = option.overall_score * 0.20
        
        confidence = tech_score + depth_score + overall_component
        return min(confidence, 1.0)
    
    def _generate_reasoning(
        self,
        option: SubstituteOption,
        analysis: GraphAnalysis
    ) -> str:
        """Genera explicación detallada"""
        reasoning = (
            f"Sustituto encontrado: {option.item_id}. "
            f"Compatibilidad técnica: {option.technical_score*100:.0f}%. "
            f"Confiabilidad proveedor: {option.reliability_score*100:.0f}%. "
            f"Score general: {option.overall_score*100:.0f}%. "
            f"Profundidad en grafo: {option.search_depth}. "
            f"Alternativas evaluadas: {option.alternatives_count}. "
            f"Estrategia búsqueda: {analysis.search_strategy.value}. "
            f"Nodos explorados: {analysis.total_nodes_explored}. "
        )
        return reasoning
