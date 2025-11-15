"""
Repository layer para ItemMaster.

Proporciona acceso a datos de items con queries optimizadas.
"""

from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, UTC

from models.planner import (
    ItemMaster, BOMComponent, EquivalentItem,
    ItemCriticality, ABCClassification
)


class ItemRepository:
    """Repository para operaciones de ItemMaster"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, item_id: str) -> Optional[ItemMaster]:
        """
        Obtiene item por item_id.
        
        Args:
            item_id: ID del item (e.g., "ITEM-001")
        
        Returns:
            ItemMaster o None si no existe
        """
        stmt = select(ItemMaster).where(ItemMaster.item_id == item_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_sap_code(self, sap_code: str) -> Optional[ItemMaster]:
        """
        Obtiene item por código SAP.
        
        Args:
            sap_code: Código SAP (e.g., "MAT-001")
        
        Returns:
            ItemMaster o None si no existe
        """
        stmt = select(ItemMaster).where(ItemMaster.sap_code == sap_code)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_critical_items(self, min_criticality: ItemCriticality = ItemCriticality.HIGH) -> List[ItemMaster]:
        """
        Obtiene items críticos.
        
        Args:
            min_criticality: Criticidad mínima (default: HIGH)
        
        Returns:
            Lista de items críticos ordenados por criticidad
        """
        criticality_order = {
            ItemCriticality.CRITICAL: 1,
            ItemCriticality.HIGH: 2,
            ItemCriticality.MEDIUM: 3,
            ItemCriticality.LOW: 4
        }
        
        target_order = criticality_order[min_criticality]
        
        # Filtrar por CRITICAL, HIGH, o lo que sea >= min_criticality
        valid_criticalities = [
            crit for crit, order in criticality_order.items() 
            if order <= target_order
        ]
        
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.criticality.in_(valid_criticalities))
            .order_by(ItemMaster.criticality)
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_abc_class(self, abc_class: ABCClassification) -> List[ItemMaster]:
        """
        Obtiene items por clasificación ABC.
        
        Args:
            abc_class: Clase ABC (A, B, C)
        
        Returns:
            Lista de items de esa clase
        """
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.abc_class == abc_class)
            .order_by(ItemMaster.annual_consumption_units.desc())
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_with_bom(self, item_id: str) -> Optional[ItemMaster]:
        """
        Obtiene item con sus componentes BOM cargados.
        
        Args:
            item_id: ID del item
        
        Returns:
            ItemMaster con bom_components cargados
        """
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.item_id == item_id)
            .options(joinedload(ItemMaster.bom_components))
        )
        
        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    def get_with_equivalents(self, item_id: str) -> Optional[ItemMaster]:
        """
        Obtiene item con sus equivalentes cargados.
        
        Args:
            item_id: ID del item
        
        Returns:
            ItemMaster con equivalent_items cargados
        """
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.item_id == item_id)
            .options(joinedload(ItemMaster.equivalent_items))
        )
        
        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    def search_by_description(self, search_term: str, limit: int = 20) -> List[ItemMaster]:
        """
        Busca items por descripción.
        
        Args:
            search_term: Término a buscar (case-insensitive)
            limit: Máximo de resultados
        
        Returns:
            Lista de items que coinciden
        """
        search_pattern = f"%{search_term}%"
        
        stmt = (
            select(ItemMaster)
            .where(
                or_(
                    ItemMaster.description.ilike(search_pattern),
                    ItemMaster.long_description.ilike(search_pattern)
                )
            )
            .limit(limit)
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_assemblies(self) -> List[ItemMaster]:
        """
        Obtiene todos los items que son ensamblajes (tienen BOM).
        
        Returns:
            Lista de items assembly
        """
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.is_assembly == True)
            .options(joinedload(ItemMaster.bom_components))
        )
        
        result = self.session.execute(stmt)
        return list(result.unique().scalars().all())
    
    def get_multiple_by_ids(self, item_ids: List[str]) -> List[ItemMaster]:
        """
        Obtiene múltiples items por sus IDs.
        
        Args:
            item_ids: Lista de item_ids
        
        Returns:
            Lista de items encontrados
        """
        stmt = (
            select(ItemMaster)
            .where(ItemMaster.item_id.in_(item_ids))
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
