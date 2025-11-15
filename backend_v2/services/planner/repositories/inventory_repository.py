"""
Repository layer para InventoryLot.

Proporciona acceso a datos de inventario con cálculos de disponibilidad.
"""

from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, UTC

from models.planner import (
    InventoryLot, LotLocation, ItemMaster,
    QCStatus
)


class InventoryRepository:
    """Repository para operaciones de InventoryLot"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_lot_number(self, lot_number: str) -> Optional[InventoryLot]:
        """
        Obtiene lote por número.
        
        Args:
            lot_number: Número de lote
        
        Returns:
            InventoryLot o None
        """
        stmt = select(InventoryLot).where(InventoryLot.lot_number == lot_number)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_item(
        self, 
        item_id: str, 
        only_approved: bool = True,
        include_locations: bool = False
    ) -> List[InventoryLot]:
        """
        Obtiene lotes de un item específico.
        
        Args:
            item_id: ID del item (join con ItemMaster)
            only_approved: Solo lotes con QC aprobado
            include_locations: Cargar ubicaciones físicas
        
        Returns:
            Lista de lotes ordenados por fecha de recepción
        """
        # Primero obtener el ItemMaster.id
        item_stmt = select(ItemMaster.id).where(ItemMaster.item_id == item_id)
        item_result = self.session.execute(item_stmt)
        item_db_id = item_result.scalar_one_or_none()
        
        if not item_db_id:
            return []
        
        stmt = select(InventoryLot).where(InventoryLot.item_id == item_db_id)
        
        if only_approved:
            stmt = stmt.where(InventoryLot.qc_status == QCStatus.APPROVED)
        
        if include_locations:
            stmt = stmt.options(joinedload(InventoryLot.locations))
        
        stmt = stmt.order_by(InventoryLot.receipt_date.asc())
        
        result = self.session.execute(stmt)
        return list(result.unique().scalars().all()) if include_locations else list(result.scalars().all())
    
    def get_available_lots(
        self,
        item_id: str,
        min_quantity: float = 0.1,
        warehouse_code: Optional[str] = None
    ) -> List[InventoryLot]:
        """
        Obtiene lotes con cantidad disponible > 0.
        
        Args:
            item_id: ID del item
            min_quantity: Cantidad mínima disponible
            warehouse_code: Filtrar por almacén específico
        
        Returns:
            Lista de lotes con stock disponible ordenados por FEFO
        """
        # Obtener ItemMaster.id
        item_stmt = select(ItemMaster.id).where(ItemMaster.item_id == item_id)
        item_result = self.session.execute(item_stmt)
        item_db_id = item_result.scalar_one_or_none()
        
        if not item_db_id:
            return []
        
        stmt = (
            select(InventoryLot)
            .where(
                and_(
                    InventoryLot.item_id == item_db_id,
                    InventoryLot.qc_status == QCStatus.APPROVED,
                    InventoryLot.quantity_on_hand > 0
                )
            )
        )
        
        if warehouse_code:
            # Join con LotLocation
            stmt = (
                stmt
                .join(LotLocation, InventoryLot.id == LotLocation.lot_id)
                .where(LotLocation.warehouse_code == warehouse_code)
            )
        
        # FEFO: First Expiry, First Out
        stmt = stmt.order_by(
            InventoryLot.expiration_date.asc().nullslast(),
            InventoryLot.receipt_date.asc()
        )
        
        result = self.session.execute(stmt)
        lots = list(result.unique().scalars().all()) if warehouse_code else list(result.scalars().all())
        
        # Filtrar por cantidad disponible calculada
        return [lot for lot in lots if lot.quantity_available >= min_quantity]
    
    def calculate_total_available(self, item_id: str, warehouse_code: Optional[str] = None) -> float:
        """
        Calcula cantidad total disponible para un item.
        
        Args:
            item_id: ID del item
            warehouse_code: Filtrar por almacén
        
        Returns:
            Cantidad total disponible (suma de quantity_available)
        """
        lots = self.get_available_lots(item_id, min_quantity=0.0, warehouse_code=warehouse_code)
        return sum(lot.quantity_available for lot in lots)
    
    def get_expiring_soon(self, days_threshold: int = 30) -> List[InventoryLot]:
        """
        Obtiene lotes que vencen pronto.
        
        Args:
            days_threshold: Días hasta vencimiento
        
        Returns:
            Lotes que vencen en los próximos N días
        """
        cutoff_date = datetime.now(UTC) + timedelta(days=days_threshold)
        
        stmt = (
            select(InventoryLot)
            .where(
                and_(
                    InventoryLot.expiration_date.isnot(None),
                    InventoryLot.expiration_date <= cutoff_date,
                    InventoryLot.quantity_on_hand > 0,
                    InventoryLot.qc_status.in_([QCStatus.APPROVED, QCStatus.CONDITIONAL])
                )
            )
            .order_by(InventoryLot.expiration_date.asc())
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_warehouse(self, warehouse_code: str, only_available: bool = True) -> List[InventoryLot]:
        """
        Obtiene lotes en un almacén específico.
        
        Args:
            warehouse_code: Código de almacén (e.g., "WH-001")
            only_available: Solo con cantidad disponible > 0
        
        Returns:
            Lista de lotes en ese almacén
        """
        stmt = (
            select(InventoryLot)
            .join(LotLocation, InventoryLot.id == LotLocation.lot_id)
            .where(LotLocation.warehouse_code == warehouse_code)
            .options(joinedload(InventoryLot.locations))
        )
        
        if only_available:
            stmt = stmt.where(
                and_(
                    InventoryLot.quantity_on_hand > 0,
                    InventoryLot.qc_status == QCStatus.APPROVED
                )
            )
        
        result = self.session.execute(stmt)
        return list(result.unique().scalars().all())
    
    def get_lots_by_supplier(self, supplier_id: str, only_approved: bool = True) -> List[InventoryLot]:
        """
        Obtiene lotes de un proveedor específico.
        
        Args:
            supplier_id: ID del proveedor
            only_approved: Solo QC aprobado
        
        Returns:
            Lista de lotes de ese proveedor
        """
        stmt = select(InventoryLot).where(InventoryLot.supplier_id == supplier_id)
        
        if only_approved:
            stmt = stmt.where(InventoryLot.qc_status == QCStatus.APPROVED)
        
        stmt = stmt.order_by(InventoryLot.receipt_date.desc())
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_inventory_summary(self, item_id: str) -> Dict[str, float]:
        """
        Obtiene resumen de inventario para un item.
        
        Args:
            item_id: ID del item
        
        Returns:
            Dict con totales {on_hand, available, reserved_hard, reserved_soft, allocated}
        """
        # Obtener ItemMaster.id
        item_stmt = select(ItemMaster.id).where(ItemMaster.item_id == item_id)
        item_result = self.session.execute(item_stmt)
        item_db_id = item_result.scalar_one_or_none()
        
        if not item_db_id:
            return {
                "on_hand": 0.0,
                "available": 0.0,
                "reserved_hard": 0.0,
                "reserved_soft": 0.0,
                "allocated": 0.0
            }
        
        stmt = (
            select(
                func.sum(InventoryLot.quantity_on_hand).label("on_hand"),
                func.sum(InventoryLot.quantity_reserved_hard).label("reserved_hard"),
                func.sum(InventoryLot.quantity_reserved_soft).label("reserved_soft"),
                func.sum(InventoryLot.quantity_allocated).label("allocated")
            )
            .where(
                and_(
                    InventoryLot.item_id == item_db_id,
                    InventoryLot.qc_status == QCStatus.APPROVED
                )
            )
        )
        
        result = self.session.execute(stmt)
        row = result.one()
        
        on_hand = float(row.on_hand or 0.0)
        reserved_hard = float(row.reserved_hard or 0.0)
        reserved_soft = float(row.reserved_soft or 0.0)
        allocated = float(row.allocated or 0.0)
        
        available = on_hand - reserved_hard - reserved_soft - allocated
        
        return {
            "on_hand": on_hand,
            "available": max(0.0, available),
            "reserved_hard": reserved_hard,
            "reserved_soft": reserved_soft,
            "allocated": allocated
        }
