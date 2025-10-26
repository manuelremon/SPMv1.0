"""
Algoritmo: Liberación de Reservas (Min-Costo Marginal)

Responsabilidades:
- Detectar reservas sub-óptimas
- Liberar usando análisis de costo marginal
- Minimizar costo de oportunidad

Complejidad: O(n log n) - sorting + análisis
"""

from dataclasses import dataclass, field
from typing import Tuple, List
import logging
from enum import Enum

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


class ReleaseStrategy(Enum):
    """Estrategias de liberación disponibles"""
    FULL_RELEASE = "full"          # Liberar completamente
    PARTIAL_RELEASE = "partial"    # Liberar parcialmente
    NO_RELEASE = "none"            # No liberar


@dataclass
class MarginalCostAnalysis:
    """Resultado del análisis de costo marginal"""
    reserved_quantity: float
    local_cost_per_unit: float
    alternative_cost_per_unit: float
    marginal_cost_difference: float  # local - alternative
    marginal_cost_index: float  # percentage difference
    recommendation: ReleaseStrategy


class ReleaseMarginalCostAlgorithm(BaseAlgorithm):
    """
    Algoritmo de Liberación Min-Costo Marginal.
    
    Detecta y libera reservas que tienen mejor costo marginal
    en alternativas (transferencias, sustitutos, compra).
    
    Estrategia:
    1. Calcular costo marginal de mantener reserva vs. alternativas
    2. Si costo alternativo < costo reserva + threshold → LIBERAR
    3. Si ahorro marginal > 20% → LIBERAR COMPLETAMENTE
    4. Si ahorro marginal 5-20% → LIBERAR PARCIALMENTE
    """
    
    # Umbrales de decisión
    MARGINAL_COST_THRESHOLD_PCT = 5.0  # Liberación si > 5% ahorro
    FULL_RELEASE_THRESHOLD_PCT = 20.0  # Liberar todo si > 20% ahorro
    
    def __init__(self):
        super().__init__(AlgorithmType.RELEASE_MARGINAL)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida entrada para análisis de liberación"""
        if input_data.demand_quantity <= 0:
            return False, "Demanda debe ser > 0"
        local_stock_qty = sum(input_data.local_stock.values()) if isinstance(input_data.local_stock, dict) else input_data.local_stock
        if local_stock_qty < 0:
            return False, "Stock local no puede ser negativo"
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """Ejecuta análisis de costo marginal para liberación"""
        try:
            # Obtener cantidad de stock local
            local_stock_qty = sum(input_data.local_stock.values()) if isinstance(input_data.local_stock, dict) else input_data.local_stock
            
            # Paso 1: Calcular costo local de mantener reserva
            local_holding_cost = self._calculate_local_holding_cost(input_data)
            
            # Paso 2: Calcular costo alternativo (transfer + expedite + substitute)
            alternative_cost = self._calculate_alternative_cost(input_data)
            
            # Paso 3: Análisis marginal
            marginal_analysis = self._perform_marginal_analysis(
                reserved_qty=local_stock_qty,
                local_cost=local_holding_cost,
                alternative_cost=alternative_cost
            )
            
            # Paso 4: Calcular cantidad a liberar basado en estrategia
            release_qty = self._calculate_release_quantity(
                local_stock_qty,
                marginal_analysis.recommendation,
                input_data.demand_quantity
            )
            
            # Paso 5: Calcular confidence score
            confidence_score = self._calculate_confidence_score(
                marginal_analysis.marginal_cost_index,
                input_data.criticality
            )
            
            reasoning = (
                f"Liberar {release_qty:.1f} u (estrategia: {marginal_analysis.recommendation.value}). "
                f"Ahorro marginal: {marginal_analysis.marginal_cost_index:.1f}%. "
                f"Costo local: ${local_holding_cost:.2f}/u vs "
                f"Alternativa: ${alternative_cost:.2f}/u"
            )
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.RELEASE_MARGINAL,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=f"RELEASE_{marginal_analysis.recommendation.value.upper()}",
                proposed_quantity=release_qty,
                estimated_cost=local_holding_cost * (local_stock_qty - release_qty),
                confidence_score=confidence_score,
                reasoning=reasoning
            )
        except Exception as e:
            logger.error(f"Error en ReleaseMarginalCostAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.RELEASE_MARGINAL,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                proposed_quantity=0,
                confidence_score=0.0,
                reasoning=f"Error en análisis marginal: {str(e)}"
            )
    
    def _calculate_local_holding_cost(self, input_data: AlgorithmInput) -> float:
        """Calcula costo de mantener stock en ubicación local"""
        # Costo holding = (precio_item * tasa_holding_anual / 365) 
        # Simplificado: aproximadamente 10-15% del costo item anual
        base_cost = 8.0  # Costo holding base por unidad-día (aumentado)
        criticality_multiplier = {
            "CRITICAL": 1.5,
            "HIGH": 1.2,
            "MEDIUM": 1.0,
            "LOW": 0.9,  # Ajustado de 0.7 a 0.9
        }
        multiplier = criticality_multiplier.get(input_data.criticality, 1.0)
        return base_cost * multiplier
    
    def _calculate_alternative_cost(self, input_data: AlgorithmInput) -> float:
        """Calcula costo de alternativas (transfer + expedite + buy)"""
        # Transfer TDABC cost: ~2-5 per unit (transport + picking)
        transfer_cost = 3.0
        
        # Expedite premium: ~15-30% sobre transfer
        expedite_factor = 1.2 if input_data.required_date else 1.0
        
        # Substitute availability discount: -10% si disponible
        substitute_discount = 0.9 if input_data.criticality == "CRITICAL" else 1.0
        
        alternative_cost = transfer_cost * expedite_factor * substitute_discount
        return max(alternative_cost, 1.0)  # Mínimo $1
    
    def _perform_marginal_analysis(
        self, 
        reserved_qty: float, 
        local_cost: float, 
        alternative_cost: float
    ) -> MarginalCostAnalysis:
        """Realiza análisis marginal de costos"""
        marginal_difference = local_cost - alternative_cost
        
        # Índice marginal: % de ahorro
        if local_cost > 0:
            marginal_index = (marginal_difference / local_cost) * 100
        else:
            marginal_index = 0.0
        
        # Determinar recomendación basado en threshold
        if marginal_index >= self.FULL_RELEASE_THRESHOLD_PCT:
            recommendation = ReleaseStrategy.FULL_RELEASE
        elif marginal_index >= self.MARGINAL_COST_THRESHOLD_PCT:
            recommendation = ReleaseStrategy.PARTIAL_RELEASE
        else:
            recommendation = ReleaseStrategy.NO_RELEASE
        
        return MarginalCostAnalysis(
            reserved_quantity=reserved_qty,
            local_cost_per_unit=local_cost,
            alternative_cost_per_unit=alternative_cost,
            marginal_cost_difference=marginal_difference,
            marginal_cost_index=marginal_index,
            recommendation=recommendation
        )
    
    def _calculate_release_quantity(
        self, 
        reserved_qty: float, 
        strategy: ReleaseStrategy,
        demand_qty: float
    ) -> float:
        """Calcula cantidad a liberar basada en estrategia"""
        if strategy == ReleaseStrategy.FULL_RELEASE:
            return reserved_qty  # Liberar todo
        elif strategy == ReleaseStrategy.PARTIAL_RELEASE:
            # Liberar 50% de lo reservado
            return min(reserved_qty * 0.5, demand_qty * 0.3)
        else:
            return 0.0  # No liberar
    
    def _calculate_confidence_score(self, marginal_index: float, criticality: str) -> float:
        """Calcula confidence score del análisis"""
        # Base: % de ahorro marginal
        base_confidence = min(marginal_index / 50.0, 1.0)  # Normalizador a 50%
        
        # Ajuste por criticidad: menos confianza si es crítico (más riesgo)
        criticality_adjustment = {
            "CRITICAL": 0.8,
            "HIGH": 0.9,
            "MEDIUM": 1.0,
            "LOW": 1.1,
        }
        adjustment = criticality_adjustment.get(criticality, 1.0)
        
        confidence = base_confidence * adjustment
        return max(0.0, min(confidence, 1.0))  # Clamp 0-1
