"""
Algoritmo: Compra Multi-Criterio (Selección de Proveedores)

Responsabilidades:
- Ranking multi-criterio de proveedores (AHP/TOPSIS)
- Optimizar: precio, lead time, calidad, confiabilidad
- Negociación de cantidades (MOQ, múltiplos)
- Recomendar mejor proveedor

Complejidad: O(m*n) donde m=criterios, n=proveedores

Adaptado de src/planner/algorithms/purchase_multicriterion.py
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


@dataclass
class SupplierScore:
    """Score multi-criterio de un proveedor"""
    supplier_id: str
    supplier_name: str
    
    # Criterios individuales (0-1)
    price_score: float
    lead_time_score: float
    quality_score: float
    reliability_score: float
    
    # Score total ponderado
    total_score: float
    
    # Datos operativos
    unit_price: float
    lead_time_days: int
    minimum_order_quantity: float


class PurchaseMulticriterionAlgorithm(BaseAlgorithm):
    """
    Algoritmo de selección de proveedores por multi-criterio.
    
    Método: Weighted Sum Model (WSM)
    - Precio: 40% del peso
    - Lead time: 25%
    - Calidad: 20%
    - Confiabilidad: 15%
    """
    
    def __init__(self):
        """Inicializa algoritmo de compra multi-criterio"""
        super().__init__(AlgorithmType.PURCHASE_MULTICRITERION)
        
        # Pesos de criterios (deben sumar 1.0)
        self.weights = {
            "price": 0.40,
            "lead_time": 0.25,
            "quality": 0.20,
            "reliability": 0.15
        }
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """
        Valida que el input sea compatible con compra.
        
        Requisitos:
        - Budget disponible
        - Demanda > 0
        """
        # 1. Verificar budget
        if input_data.budget_available <= 0:
            return False, "Presupuesto requerido para compra"
        
        # 2. Verificar demanda
        if input_data.demand_quantity <= 0:
            return False, "Demanda debe ser > 0"
        
        return True, ""
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """
        Ejecuta selección multi-criterio de proveedores.
        """
        try:
            # 1. Obtener proveedores candidatos
            if input_data.db_session:
                suppliers = self._fetch_suppliers_from_db(
                    input_data.db_session,
                    input_data.item_id
                )
            else:
                suppliers = self._get_candidate_suppliers(input_data)
            
            # 2. Calcular scores multi-criterio
            scored_suppliers = self._score_suppliers(suppliers, input_data)
            
            # 3. Seleccionar mejor proveedor
            best_supplier = max(scored_suppliers, key=lambda s: s.total_score)
            
            # 4. Calcular cantidad ajustada por MOQ
            adjusted_qty = self._adjust_quantity_for_moq(
                input_data.demand_quantity,
                best_supplier.minimum_order_quantity
            )
            
            # 5. Calcular costo total
            total_cost = adjusted_qty * best_supplier.unit_price
            
            # 6. Validar presupuesto
            if total_cost > input_data.budget_available:
                # Ajustar cantidad si excede presupuesto
                adjusted_qty = input_data.budget_available / best_supplier.unit_price
                total_cost = input_data.budget_available
            
            # 7. Generar alternativas
            alternatives = [
                {
                    "supplier_id": s.supplier_id,
                    "supplier_name": s.supplier_name,
                    "score": s.total_score,
                    "unit_price": s.unit_price,
                    "lead_time_days": s.lead_time_days
                }
                for s in scored_suppliers[1:4]  # Top 3 alternativas
            ]
            
            reasoning = (
                f"Proveedor seleccionado: {best_supplier.supplier_name} "
                f"(score: {best_supplier.total_score:.2f}). "
                f"Cantidad: {adjusted_qty:.1f} u @ ${best_supplier.unit_price:.2f}/u. "
                f"Lead time: {best_supplier.lead_time_days} días. "
                f"Costo total: ${total_cost:.2f}"
            )
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.PURCHASE_MULTICRITERION,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=f"PURCHASE_FROM_{best_supplier.supplier_id}",
                proposed_quantity=adjusted_qty,
                estimated_cost=total_cost,
                estimated_lead_time=best_supplier.lead_time_days,
                confidence_score=best_supplier.total_score,
                reasoning=reasoning,
                alternatives_considered=alternatives
            )
            
        except Exception as e:
            self.logger.error(f"Error en compra multi-criterio: {str(e)}")
            raise
    
    def _fetch_suppliers_from_db(
        self,
        session,
        item_id: str
    ) -> List[Dict[str, Any]]:
        """
        Consulta proveedores reales desde base de datos.
        
        Args:
            session: SQLAlchemy session
            item_id: ID del item
        
        Returns:
            Lista de proveedores con sus datos operativos
        """
        try:
            from services.planner.repositories import SupplierRepository
            from models.planner import SupplierRating
            
            repo = SupplierRepository(session)
            
            # Obtener acuerdos de precio para este item
            agreements = repo.get_price_agreements(
                item_id=item_id,
                valid_only=True
            )
            
            # Mapear SupplierRating a quality_rating (0-1)
            rating_map = {
                SupplierRating.EXCELLENT: 0.95,
                SupplierRating.GOOD: 0.85,
                SupplierRating.FAIR: 0.70,
                SupplierRating.POOR: 0.50
            }
            
            suppliers_list = []
            for agreement in agreements:
                supplier = agreement.supplier
                
                suppliers_list.append({
                    "id": supplier.supplier_id,
                    "name": supplier.name,
                    "base_price": float(agreement.unit_price_usd),
                    "lead_time_days": supplier.lead_time_days,
                    "quality_rating": rating_map.get(supplier.rating, 0.75),
                    "reliability_rating": 0.90 if supplier.is_preferred else 0.75,
                    "minimum_order_quantity": float(agreement.moq)
                })
            
            if not suppliers_list:
                self.logger.warning(f"No suppliers found in DB for item {item_id}, using simulated")
                return self._get_candidate_suppliers_simulated()
            
            self.logger.info(f"Fetched {len(suppliers_list)} suppliers from DB for {item_id}")
            return suppliers_list
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch suppliers from DB: {e}. Using simulated.")
            return self._get_candidate_suppliers_simulated()
    
    def _get_candidate_suppliers_simulated(self) -> List[Dict[str, Any]]:
        """Proveedores simulados para backward compatibility"""
        return [
            {
                "id": "SUP-001",
                "name": "Proveedor Alpha",
                "base_price": 45.0,
                "lead_time_days": 7,
                "quality_rating": 0.95,
                "reliability_rating": 0.90,
                "minimum_order_quantity": 10.0
            },
            {
                "id": "SUP-002",
                "name": "Proveedor Beta",
                "base_price": 42.0,
                "lead_time_days": 14,
                "quality_rating": 0.85,
                "reliability_rating": 0.88,
                "minimum_order_quantity": 20.0
            },
            {
                "id": "SUP-003",
                "name": "Proveedor Gamma",
                "base_price": 50.0,
                "lead_time_days": 5,
                "quality_rating": 0.98,
                "reliability_rating": 0.95,
                "minimum_order_quantity": 5.0
            }
        ]
    
    def _get_candidate_suppliers(
        self,
        input_data: AlgorithmInput
    ) -> List[Dict[str, Any]]:
        """
        Obtiene lista de proveedores candidatos.
        
        En producción: Query a base de datos de proveedores.
        Ahora: Datos simulados para proof-of-concept.
        """
        # Simulated supplier data
        return [
            {
                "id": "SUP-001",
                "name": "Proveedor Alpha",
                "base_price": 45.0,
                "lead_time_days": 7,
                "quality_rating": 0.95,
                "reliability_rating": 0.90,
                "moq": 10.0
            },
            {
                "id": "SUP-002",
                "name": "Proveedor Beta",
                "base_price": 42.0,
                "lead_time_days": 14,
                "quality_rating": 0.85,
                "reliability_rating": 0.85,
                "moq": 20.0
            },
            {
                "id": "SUP-003",
                "name": "Proveedor Gamma",
                "base_price": 50.0,
                "lead_time_days": 5,
                "quality_rating": 0.98,
                "reliability_rating": 0.95,
                "moq": 5.0
            }
        ]
    
    def _score_suppliers(
        self,
        suppliers: List[Dict[str, Any]],
        input_data: AlgorithmInput
    ) -> List[SupplierScore]:
        """
        Calcula scores multi-criterio para cada proveedor.
        
        Normalización:
        - Precio: menor es mejor → normalize inverso
        - Lead time: menor es mejor → normalize inverso
        - Calidad: mayor es mejor → normalize directo
        - Confiabilidad: mayor es mejor → normalize directo
        """
        # Extraer valores para normalización
        prices = [s["base_price"] for s in suppliers]
        lead_times = [s["lead_time_days"] for s in suppliers]
        
        max_price = max(prices)
        min_price = min(prices)
        max_lead_time = max(lead_times)
        min_lead_time = min(lead_times)
        
        scored = []
        for supplier in suppliers:
            # Normalize precio (inverso: menor es mejor)
            price_score = (
                (max_price - supplier["base_price"]) / (max_price - min_price)
                if max_price != min_price else 1.0
            )
            
            # Normalize lead time (inverso: menor es mejor)
            lead_time_score = (
                (max_lead_time - supplier["lead_time_days"]) / (max_lead_time - min_lead_time)
                if max_lead_time != min_lead_time else 1.0
            )
            
            # Scores directos (ya en 0-1)
            quality_score = supplier["quality_rating"]
            reliability_score = supplier["reliability_rating"]
            
            # Score total ponderado
            total_score = (
                price_score * self.weights["price"] +
                lead_time_score * self.weights["lead_time"] +
                quality_score * self.weights["quality"] +
                reliability_score * self.weights["reliability"]
            )
            
            scored.append(SupplierScore(
                supplier_id=supplier["id"],
                supplier_name=supplier["name"],
                price_score=price_score,
                lead_time_score=lead_time_score,
                quality_score=quality_score,
                reliability_score=reliability_score,
                total_score=total_score,
                unit_price=supplier["base_price"],
                lead_time_days=supplier["lead_time_days"],
                minimum_order_quantity=supplier.get("minimum_order_quantity") or supplier.get("moq", 0.0)
            ))
        
        # Ordenar por score descendente
        scored.sort(key=lambda s: s.total_score, reverse=True)
        return scored
    
    def _adjust_quantity_for_moq(
        self,
        requested_qty: float,
        moq: float
    ) -> float:
        """
        Ajusta cantidad por MOQ (Minimum Order Quantity).
        
        Si requested < MOQ → usar MOQ
        Si requested > MOQ → redondear al múltiplo superior
        """
        if requested_qty < moq:
            return moq
        
        # Redondear al múltiplo superior de MOQ
        import math
        return math.ceil(requested_qty / moq) * moq
    
    def get_metadata(self) -> dict:
        """Retorna metadata del algoritmo"""
        metadata = super().get_metadata()
        metadata.update({
            "strategy": "Weighted Sum Model (WSM)",
            "weights": self.weights,
            "description": "Selección multi-criterio de proveedores (precio, lead time, calidad, confiabilidad)"
        })
        return metadata


# Instancia global del algoritmo
_purchase_multicriterion = PurchaseMulticriterionAlgorithm()


def get_purchase_multicriterion_algorithm() -> PurchaseMulticriterionAlgorithm:
    """Obtiene la instancia global del algoritmo"""
    return _purchase_multicriterion
