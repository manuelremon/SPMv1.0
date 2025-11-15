"""
Algoritmo #3: Disassembly Knapsack Problem
==========================================
Resuelve el problema de empaquetamiento 0/1 para minimizar costos de desarme.

Responsabilidad:
- Dado un item con BOM (Bill of Materials), determinar qué componentes desensamblar
- Objetivo: Minimizar costo total considerando disassembly cost vs valor recuperado
- Restricción: Capacity knapsack (tiempo/costo disponible)

Aplicación en supply chain:
- Cuando un item está dañado o obsoleto
- Recuperar componentes valiosos para otros proyectos
- Optimizar decisión: desensamblar completo vs. parcial vs. no desensamblar

Complejidad: O(n*W) donde n = # componentes, W = capacity
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


class DisassemblyStrategy(str, Enum):
    """Estrategia de desarme"""
    FULL_DISASSEMBLY = "full"      # Desensamblar todos los componentes
    PARTIAL_DISASSEMBLY = "partial"  # Desensamblar componentes selectos
    NO_DISASSEMBLY = "none"         # No desensamblar, vender/descartar completo


@dataclass
class KnapsackComponent:
    """Componente evaluable en problema knapsack"""
    component_id: str
    component_qty: float
    component_cost: float           # Costo de desensamblar esta cantidad
    component_value: float          # Valor recuperado (precio mercado)
    profit: float                   # value - cost
    profit_ratio: float             # profit / cost (eficiencia)
    include_in_solution: bool = False


@dataclass
class DisassemblyAnalysis:
    """Resultado del análisis de disassembly knapsack"""
    strategy: DisassemblyStrategy
    total_disassembly_cost: float
    total_recovery_value: float
    net_profit: float              # recovery_value - disassembly_cost
    selected_components: List[str]  # IDs de componentes a desensamblar
    skipped_components: List[str]
    capacity_utilization: float    # % del capacity usado
    efficiency_score: float        # net_profit / total_disassembly_cost
    confidence_score: float        # 0-1, basado en value certainty


class DisassemblyKnapsackAlgorithm(BaseAlgorithm):
    """
    Resuelve problema 0/1 knapsack para decisión de desarme.
    
    Entrada:
    - item_id: str
    - demand_quantity: float (units to disassemble)
    - bom_components: Dict[str, float] (component_id → quantity)
    - criticality: str (CRITICAL/HIGH → conservative, LOW → aggressive)
    
    Salida:
    - proposed_quantity: float (cantidad a desensamblar)
    - confidence_score: 0-1 (certeza en recuperación de valor)
    - reasoning: str (explicación de selección)
    - selected_option: str ("disassembly_full/partial/none")
    """
    
    # Constantes
    FULL_DISASSEMBLY_THRESHOLD = 0.30   # Si eficiencia >= 30%, desensamblar completo
    PARTIAL_DISASSEMBLY_THRESHOLD = 0.10  # Si 10% <= eficiencia < 30%, parcial
    
    def __init__(self):
        super().__init__(AlgorithmType.DISASSEMBLY_KNAPSACK)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida entrada del algoritmo"""
        if not input_data.item_id:
            return False, "item_id requerido"
        if input_data.demand_quantity <= 0:
            return False, "demand_quantity debe ser > 0"
        return True, "OK"
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        Ejecuta algoritmo de disassembly knapsack.
        
        Pasos:
        1. Validar entrada
        2. Construir lista de componentes (mock BOM)
        3. Calcular costo-beneficio de cada componente
        4. Resolver knapsack 0/1 usando programación dinámica
        5. Determinar estrategia (full/partial/none)
        6. Calcular confidence basado en certeza de valor
        7. Retornar resultado con reasoning
        """
        try:
            # 1. Construir lista de componentes
            if input_data.db_session:
                components = self._fetch_bom_components_from_db(
                    input_data.db_session,
                    input_data.item_id
                )
            else:
                components = self._build_bom_components(input_data)
            
            if not components:
                return AlgorithmOutput(
                    algorithm_type=self.algorithm_type,
                    item_id=input_data.item_id,
                    success=True,
                    status=AlgorithmStatus.COMPLETED,
                    proposed_quantity=0.0,
                    estimated_cost=0.0,
                    confidence_score=0.0,
                    reasoning="No hay componentes para desensamblar",
                    selected_option="disassembly_none"
                )
            
            # 2. Calcular profit de cada componente
            components = self._calculate_component_profit(components, input_data)
            
            # 3. Resolver knapsack
            capacity = self._determine_capacity(input_data)
            analysis = self._solve_knapsack(components, capacity, input_data)
            
            # 4. Determinar estrategia
            strategy = self._determine_strategy(analysis)
            analysis.strategy = strategy
            
            # 5. Calcular confidence
            confidence = self._calculate_confidence(analysis, input_data)
            
            # 6. Preparar reasoning
            reasoning = self._generate_reasoning(analysis, strategy)
            
            # Determinar cantidad a desensamblar
            if strategy == DisassemblyStrategy.FULL_DISASSEMBLY:
                proposed_qty = input_data.demand_quantity
                selected_option = "disassembly_full"
            elif strategy == DisassemblyStrategy.PARTIAL_DISASSEMBLY:
                proposed_qty = input_data.demand_quantity * 0.5
                selected_option = "disassembly_partial"
            else:
                proposed_qty = 0.0
                selected_option = "disassembly_none"
            
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                proposed_quantity=proposed_qty,
                estimated_cost=analysis.total_disassembly_cost,
                confidence_score=confidence,
                reasoning=reasoning,
                selected_option=selected_option
            )
        
        except Exception as e:
            logger.error(f"Error en DisassemblyKnapsackAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=self.algorithm_type,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                proposed_quantity=0.0,
                estimated_cost=0.0,
                confidence_score=0.0,
                reasoning=f"Error en análisis knapsack: {str(e)}"
            )
    
    # ===== Métodos Privados =====
    
    def _build_bom_components(self, input_data: AlgorithmInput) -> List[KnapsackComponent]:
        """
        Construye lista de componentes desde BOM simulado.
        En producción: consultaría base de datos BOM real.
        """
        # Mock BOM: componentes típicos de un item manufacturado
        components_data = [
            {"id": "COMP-001", "qty": 3.0, "disassembly_cost": 1.5, "market_value": 8.0},
            {"id": "COMP-002", "qty": 2.0, "disassembly_cost": 2.0, "market_value": 5.0},
            {"id": "COMP-003", "qty": 1.0, "disassembly_cost": 3.0, "market_value": 12.0},
            {"id": "COMP-004", "qty": 4.0, "disassembly_cost": 0.5, "market_value": 2.5},
            {"id": "COMP-005", "qty": 1.0, "disassembly_cost": 1.0, "market_value": 3.0},
        ]
        
        components = []
        for comp_data in components_data:
            component = KnapsackComponent(
                component_id=comp_data["id"],
                component_qty=comp_data["qty"],
                component_cost=comp_data["disassembly_cost"],
                component_value=comp_data["market_value"],
                profit=0.0,
                profit_ratio=0.0
            )
            components.append(component)
        
        return components
    
    def _calculate_component_profit(
        self,
        components: List[KnapsackComponent],
        input_data: AlgorithmInput
    ) -> List[KnapsackComponent]:
        """Calcula profit (value - cost) para cada componente"""
        for component in components:
            # Profit por unidad de componente
            profit_per_unit = component.component_value - component.component_cost
            component.profit = profit_per_unit * component.component_qty
            
            # Ratio de eficiencia
            if component.component_cost > 0:
                component.profit_ratio = component.profit / component.component_cost
            else:
                component.profit_ratio = float('inf') if component.profit > 0 else 0
        
        # Aplicar ajuste por criticidad (items críticos → más conservador)
        criticality_factor = {
            "CRITICAL": 0.6,   # Recuperar solo lo más valioso
            "HIGH": 0.8,
            "MEDIUM": 1.0,
            "LOW": 1.2          # Más agresivo si es low priority
        }
        factor = criticality_factor.get(input_data.criticality, 1.0)
        
        for component in components:
            component.profit_ratio *= factor
        
        return components
    
    def _determine_capacity(self, input_data: AlgorithmInput) -> float:
        """
        Determina capacity (tiempo/costo máximo de disassembly).
        Por defecto: 20% del valor del item original.
        """
        # Simulado: valor base del item
        item_value = 100.0
        
        # Capacity = 20% del valor
        capacity = item_value * 0.20
        
        # Ajuste por criticidad
        if input_data.criticality == "CRITICAL":
            capacity *= 0.5  # Más estricto
        elif input_data.criticality == "LOW":
            capacity *= 1.5  # Más flexible
        
        return capacity
    
    def _solve_knapsack(
        self,
        components: List[KnapsackComponent],
        capacity: float,
        input_data: AlgorithmInput
    ) -> DisassemblyAnalysis:
        """
        Resuelve problema 0/1 knapsack usando programación dinámica.
        
        Items: componentes (costo = disassembly_cost*qty, valor = market_value*qty)
        Capacity: capacity disponible
        Goal: Maximizar valor recuperado bajo constraint de costo
        """
        n = len(components)
        w = int(capacity * 10)  # Discretizar a escala 0.1
        
        # DP table: dp[i][j] = max value usando primeros i items con capacity j
        dp = [[0.0 for _ in range(w + 1)] for _ in range(n + 1)]
        
        # Llenar tabla DP
        for i in range(1, n + 1):
            comp = components[i - 1]
            comp_cost = int(comp.component_cost * comp.component_qty * 10)
            comp_value = comp.component_value * comp.component_qty
            
            for j in range(w + 1):
                # Opción 1: No incluir componente i
                dp[i][j] = dp[i - 1][j]
                
                # Opción 2: Incluir componente i (si cabe)
                if comp_cost <= j:
                    dp[i][j] = max(dp[i][j], dp[i - 1][j - comp_cost] + comp_value)
        
        # Backtracking: recuperar qué componentes incluir
        selected = []
        remaining_capacity = w
        total_cost = 0.0
        total_value = 0.0
        
        for i in range(n, 0, -1):
            if dp[i][remaining_capacity] != dp[i - 1][remaining_capacity]:
                selected.append(components[i - 1])
                comp_cost = int(components[i - 1].component_cost * 
                               components[i - 1].component_qty * 10)
                remaining_capacity -= comp_cost
                total_cost += components[i - 1].component_cost * components[i - 1].component_qty
                total_value += components[i - 1].component_value * components[i - 1].component_qty
        
        selected_ids = [c.component_id for c in selected]
        skipped_ids = [c.component_id for c in components if c.component_id not in selected_ids]
        
        # Calcular métricas
        net_profit = total_value - total_cost
        efficiency = (net_profit / total_cost * 100) if total_cost > 0 else 0
        utilization = (total_cost / capacity * 100) if capacity > 0 else 0
        
        return DisassemblyAnalysis(
            strategy=DisassemblyStrategy.FULL_DISASSEMBLY,  # Placeholder
            total_disassembly_cost=total_cost,
            total_recovery_value=total_value,
            net_profit=net_profit,
            selected_components=selected_ids,
            skipped_components=skipped_ids,
            capacity_utilization=min(utilization, 100.0),
            efficiency_score=efficiency,
            confidence_score=0.0  # Se calcula después
        )
    
    def _determine_strategy(self, analysis: DisassemblyAnalysis) -> DisassemblyStrategy:
        """Determina estrategia basado en eficiencia del knapsack"""
        efficiency = analysis.efficiency_score / 100  # Normalizar
        
        if efficiency >= self.FULL_DISASSEMBLY_THRESHOLD:
            return DisassemblyStrategy.FULL_DISASSEMBLY
        elif efficiency >= self.PARTIAL_DISASSEMBLY_THRESHOLD:
            return DisassemblyStrategy.PARTIAL_DISASSEMBLY
        else:
            return DisassemblyStrategy.NO_DISASSEMBLY
    
    def _calculate_confidence(
        self,
        analysis: DisassemblyAnalysis,
        input_data: AlgorithmInput
    ) -> float:
        """
        Calcula confidence score (0-1).
        
        Factores:
        - Eficiencia del knapsack (40%)
        - Utilización de capacity (30%)
        - Certeza en valores recuperados (20%)
        - Ajuste por criticidad (10%)
        """
        # Eficiencia: (40%) - rango 0-1
        efficiency_score = min(analysis.efficiency_score / 50, 1.0) * 0.40
        
        # Utilización: (30%) - rango 0-1
        utilization_score = (analysis.capacity_utilization / 100) * 0.30
        
        # Certeza en valores: (20%) - simulado como 0.8 (high uncertainty)
        value_certainty = 0.8 * 0.20
        
        # Ajuste por criticidad: (10%)
        criticality_confidence = {
            "CRITICAL": 0.6,   # Menos confianza en recuperación
            "HIGH": 0.8,
            "MEDIUM": 0.9,
            "LOW": 0.85
        }
        criticality_score = criticality_confidence.get(input_data.criticality, 0.9) * 0.10
        
        total_confidence = efficiency_score + utilization_score + value_certainty + criticality_score
        return min(total_confidence, 1.0)
    
    def _generate_reasoning(
        self,
        analysis: DisassemblyAnalysis,
        strategy: DisassemblyStrategy
    ) -> str:
        """Genera explicación detallada de la decisión"""
        if strategy == DisassemblyStrategy.FULL_DISASSEMBLY:
            action = "Desensamblar 100% (estrategia full)"
        elif strategy == DisassemblyStrategy.PARTIAL_DISASSEMBLY:
            action = "Desensamblar 50% (estrategia parcial)"
        else:
            action = "No desensamblar (vender/descartar completo)"
        
        reasoning = (
            f"{action}. "
            f"Componentes seleccionados: {len(analysis.selected_components)}. "
            f"Valor recuperado: ${analysis.total_recovery_value:.2f}. "
            f"Costo disassembly: ${analysis.total_disassembly_cost:.2f}. "
            f"Ganancia neta: ${analysis.net_profit:.2f}. "
            f"Eficiencia: {analysis.efficiency_score:.1f}%. "
            f"Utilización capacity: {analysis.capacity_utilization:.1f}%. "
        )
        return reasoning
    
    def _fetch_bom_components_from_db(self, session, item_id: str) -> List[KnapsackComponent]:
        """Consulta componentes BOM reales desde base de datos"""
        try:
            from services.planner.repositories import ItemRepository
            
            repo = ItemRepository(session)
            bom_components = repo.get_bom_components(item_id)
            
            knapsack_components = []
            for component in bom_components:
                # Calcular costo de desarme y valor recuperado
                disassembly_cost = component.quantity * 5.0  # $5 por unidad
                recovery_value = component.quantity * 8.0    # $8 por unidad (valor mercado)
                profit = recovery_value - disassembly_cost
                profit_ratio = profit / disassembly_cost if disassembly_cost > 0 else 0.0
                
                knapsack_components.append(KnapsackComponent(
                    component_id=component.component_id,
                    component_qty=component.quantity,
                    component_cost=disassembly_cost,
                    component_value=recovery_value,
                    profit=profit,
                    profit_ratio=profit_ratio
                ))
            
            if not knapsack_components:
                self.logger.warning(f"No BOM components found for {item_id}, using simulated")
                return self._build_bom_components_simulated()
            
            return knapsack_components
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch BOM from DB: {e}")
            return self._build_bom_components_simulated()
    
    def _build_bom_components_simulated(self) -> List[KnapsackComponent]:
        """Componentes simulados para backward compatibility"""
        return [
            KnapsackComponent("COMP-A", 10.0, 50.0, 80.0, 30.0, 0.60),
            KnapsackComponent("COMP-B", 5.0, 25.0, 35.0, 10.0, 0.40),
            KnapsackComponent("COMP-C", 8.0, 40.0, 75.0, 35.0, 0.875),
        ]


# Factory function
def get_disassembly_knapsack_algorithm() -> DisassemblyKnapsackAlgorithm:
    """Obtiene instancia del algoritmo Disassembly Knapsack"""
    return DisassemblyKnapsackAlgorithm()
