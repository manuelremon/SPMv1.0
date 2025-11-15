"""
Repository layer para Supplier.

Proporciona acceso a proveedores y acuerdos de precio.
"""

from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, UTC

from models.planner import (
    Supplier, SupplierPriceAgreement,
    SupplierRating
)


class SupplierRepository:
    """Repository para operaciones de Supplier"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, supplier_id: str) -> Optional[Supplier]:
        """
        Obtiene proveedor por ID.
        
        Args:
            supplier_id: ID del proveedor (e.g., "SUP-001")
        
        Returns:
            Supplier o None
        """
        stmt = select(Supplier).where(Supplier.supplier_id == supplier_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_code(self, supplier_code: str) -> Optional[Supplier]:
        """
        Obtiene proveedor por código.
        
        Args:
            supplier_code: Código del proveedor (e.g., "PROV-001")
        
        Returns:
            Supplier o None
        """
        stmt = select(Supplier).where(Supplier.supplier_code == supplier_code)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_active_suppliers(
        self,
        min_rating: Optional[SupplierRating] = None,
        min_reliability: float = 0.0
    ) -> List[Supplier]:
        """
        Obtiene proveedores activos.
        
        Args:
            min_rating: Rating mínimo requerido
            min_reliability: Score de confiabilidad mínimo (0.0-1.0)
        
        Returns:
            Lista de proveedores activos ordenados por reliability_score
        """
        stmt = select(Supplier).where(Supplier.is_active == True)
        
        if min_rating:
            # Filtrar por rating (PREFERRED > APPROVED > CONDITIONAL > PROBATION)
            rating_order = {
                SupplierRating.PREFERRED: 1,
                SupplierRating.APPROVED: 2,
                SupplierRating.CONDITIONAL: 3,
                SupplierRating.PROBATION: 4,
                SupplierRating.BLOCKED: 5
            }
            
            target_order = rating_order[min_rating]
            valid_ratings = [
                rating for rating, order in rating_order.items()
                if order <= target_order
            ]
            
            stmt = stmt.where(Supplier.rating.in_(valid_ratings))
        
        if min_reliability > 0.0:
            stmt = stmt.where(Supplier.reliability_score >= min_reliability)
        
        stmt = stmt.order_by(Supplier.reliability_score.desc())
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_price_agreement(
        self,
        supplier_id: str,
        item_id: str,
        as_of_date: Optional[datetime] = None
    ) -> Optional[SupplierPriceAgreement]:
        """
        Obtiene acuerdo de precio vigente para un item.
        
        Args:
            supplier_id: ID del proveedor
            item_id: ID del item
            as_of_date: Fecha a validar (default: hoy)
        
        Returns:
            SupplierPriceAgreement vigente o None
        """
        # Obtener Supplier.id (DB id)
        supplier_stmt = select(Supplier.id).where(Supplier.supplier_id == supplier_id)
        supplier_result = self.session.execute(supplier_stmt)
        supplier_db_id = supplier_result.scalar_one_or_none()
        
        if not supplier_db_id:
            return None
        
        check_date = as_of_date or datetime.now(UTC)
        
        stmt = (
            select(SupplierPriceAgreement)
            .where(
                and_(
                    SupplierPriceAgreement.supplier_id == supplier_db_id,
                    SupplierPriceAgreement.item_id == item_id,
                    SupplierPriceAgreement.valid_from <= check_date
                )
            )
        )
        
        # Filtrar por valid_to (None = indefinido)
        stmt = stmt.where(
            or_(
                SupplierPriceAgreement.valid_to.is_(None),
                SupplierPriceAgreement.valid_to >= check_date
            )
        )
        
        # Ordenar por más reciente
        stmt = stmt.order_by(SupplierPriceAgreement.valid_from.desc())
        
        result = self.session.execute(stmt)
        return result.scalars().first()
    
    def get_suppliers_for_item(
        self,
        item_id: str,
        only_active: bool = True,
        min_reliability: float = 0.8
    ) -> List[Tuple[Supplier, Optional[SupplierPriceAgreement]]]:
        """
        Obtiene proveedores que suministran un item con sus acuerdos.
        
        Args:
            item_id: ID del item
            only_active: Solo proveedores activos
            min_reliability: Confiabilidad mínima
        
        Returns:
            Lista de tuplas (Supplier, SupplierPriceAgreement)
        """
        # Obtener todos los price agreements para el item
        agreement_stmt = (
            select(SupplierPriceAgreement)
            .where(SupplierPriceAgreement.item_id == item_id)
            .options(joinedload(SupplierPriceAgreement.supplier))
        )
        
        agreement_result = self.session.execute(agreement_stmt)
        agreements = list(agreement_result.unique().scalars().all())
        
        results = []
        check_date = datetime.now(UTC)
        
        for agreement in agreements:
            supplier = agreement.supplier
            
            # Filtros
            if only_active and not supplier.is_active:
                continue
            
            if supplier.reliability_score < min_reliability:
                continue
            
            # Verificar vigencia
            if not agreement.is_valid(check_date):
                continue
            
            results.append((supplier, agreement))
        
        # Ordenar por reliability_score desc
        results.sort(key=lambda x: x[0].reliability_score, reverse=True)
        
        return results
    
    def get_best_supplier_for_item(
        self,
        item_id: str,
        quantity: float = 1.0,
        optimize_for: str = "cost"  # "cost", "time", "reliability"
    ) -> Optional[Tuple[Supplier, SupplierPriceAgreement, float]]:
        """
        Obtiene el mejor proveedor para un item según criterio.
        
        Args:
            item_id: ID del item
            quantity: Cantidad requerida (para verificar MOQ)
            optimize_for: Criterio ("cost", "time", "reliability")
        
        Returns:
            Tupla (Supplier, Agreement, Score) o None
        """
        suppliers_agreements = self.get_suppliers_for_item(item_id, only_active=True)
        
        if not suppliers_agreements:
            return None
        
        best_option = None
        best_score = float('-inf')
        
        for supplier, agreement in suppliers_agreements:
            # Verificar MOQ
            if quantity < agreement.moq:
                continue
            
            # Calcular score según criterio
            if optimize_for == "cost":
                # Menor precio es mejor (invertir para maximizar)
                score = -agreement.unit_price_usd
            elif optimize_for == "time":
                # Menor lead time es mejor
                lead_time = agreement.lead_time_days or supplier.average_lead_time_days
                score = -lead_time
            elif optimize_for == "reliability":
                # Mayor confiabilidad es mejor
                score = supplier.reliability_score * supplier.on_time_delivery_rate
            else:
                # Balanced: combinar costo, tiempo, confiabilidad
                cost_score = 1.0 / (agreement.unit_price_usd + 1)
                lead_time = agreement.lead_time_days or supplier.average_lead_time_days
                time_score = 1.0 / (lead_time + 1)
                reliability_score = supplier.reliability_score
                
                score = (cost_score * 0.4) + (time_score * 0.3) + (reliability_score * 0.3)
            
            if score > best_score:
                best_score = score
                best_option = (supplier, agreement, score)
        
        return best_option
    
    def get_by_rating(self, rating: SupplierRating) -> List[Supplier]:
        """
        Obtiene proveedores por rating.
        
        Args:
            rating: Rating a filtrar
        
        Returns:
            Lista de proveedores con ese rating
        """
        stmt = (
            select(Supplier)
            .where(Supplier.rating == rating)
            .order_by(Supplier.reliability_score.desc())
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def search_by_name(self, search_term: str, limit: int = 20) -> List[Supplier]:
        """
        Busca proveedores por nombre.
        
        Args:
            search_term: Término a buscar
            limit: Máximo de resultados
        
        Returns:
            Lista de proveedores que coinciden
        """
        search_pattern = f"%{search_term}%"
        
        stmt = (
            select(Supplier)
            .where(Supplier.name.ilike(search_pattern))
            .limit(limit)
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
