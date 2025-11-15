"""
Repository layer para Warehouse.

Proporciona acceso a almacenes y cálculo de costos de transferencia.
"""

from typing import List, Optional, Dict, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from datetime import datetime

from models.planner import (
    Warehouse, WarehouseType
)


class WarehouseRepository:
    """Repository para operaciones de Warehouse"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, warehouse_id: str) -> Optional[Warehouse]:
        """
        Obtiene almacén por ID.
        
        Args:
            warehouse_id: ID del almacén (e.g., "WH-001")
        
        Returns:
            Warehouse o None
        """
        stmt = select(Warehouse).where(Warehouse.warehouse_id == warehouse_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_code(self, warehouse_code: str) -> Optional[Warehouse]:
        """
        Obtiene almacén por código.
        
        Args:
            warehouse_code: Código del almacén (e.g., "ALM-CENTRAL")
        
        Returns:
            Warehouse o None
        """
        stmt = select(Warehouse).where(Warehouse.warehouse_code == warehouse_code)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_active_warehouses(
        self,
        warehouse_type: Optional[WarehouseType] = None,
        min_reliability: float = 0.0
    ) -> List[Warehouse]:
        """
        Obtiene almacenes activos.
        
        Args:
            warehouse_type: Tipo de almacén a filtrar
            min_reliability: Confiabilidad mínima
        
        Returns:
            Lista de almacenes activos ordenados por reliability_score
        """
        stmt = select(Warehouse).where(Warehouse.is_active == True)
        
        if warehouse_type:
            stmt = stmt.where(Warehouse.warehouse_type == warehouse_type)
        
        if min_reliability > 0.0:
            stmt = stmt.where(Warehouse.reliability_score >= min_reliability)
        
        stmt = stmt.order_by(Warehouse.reliability_score.desc())
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_connections(self, warehouse_id: str) -> Dict[str, Dict[str, float]]:
        """
        Obtiene conexiones de un almacén con otros.
        
        Args:
            warehouse_id: ID del almacén origen
        
        Returns:
            Dict {target_warehouse_id: {distance_km, transit_days}}
        """
        warehouse = self.get_by_id(warehouse_id)
        
        if not warehouse:
            return {}
        
        return warehouse.connections or {}
    
    def calculate_transfer_cost(
        self,
        source_warehouse_id: str,
        target_warehouse_id: str,
        quantity: float
    ) -> Optional[float]:
        """
        Calcula costo de transferencia entre almacenes.
        
        Args:
            source_warehouse_id: Almacén origen
            target_warehouse_id: Almacén destino
            quantity: Cantidad a transferir
        
        Returns:
            Costo total en USD o None si no hay ruta
        """
        source = self.get_by_id(source_warehouse_id)
        
        if not source:
            return None
        
        return source.calculate_transfer_cost(quantity, target_warehouse_id)
    
    def get_transfer_options(
        self,
        source_warehouse_id: str,
        max_cost: Optional[float] = None,
        max_transit_days: Optional[int] = None
    ) -> List[Tuple[str, Dict[str, float], float]]:
        """
        Obtiene opciones de transferencia desde un almacén.
        
        Args:
            source_warehouse_id: Almacén origen
            max_cost: Costo máximo permitido
            max_transit_days: Días de tránsito máximos
        
        Returns:
            Lista de tuplas (target_warehouse_id, connection_info, transfer_cost)
        """
        source = self.get_by_id(source_warehouse_id)
        
        if not source or not source.connections:
            return []
        
        options = []
        
        for target_id, connection_info in source.connections.items():
            # Filtrar por transit_days
            if max_transit_days and connection_info.get('transit_days', 999) > max_transit_days:
                continue
            
            # Calcular costo (para 1 unidad como base)
            cost = source.calculate_transfer_cost(1.0, target_id)
            
            if cost is None or cost == float('inf'):
                continue
            
            # Filtrar por costo
            if max_cost and cost > max_cost:
                continue
            
            options.append((target_id, connection_info, cost))
        
        # Ordenar por costo ascendente
        options.sort(key=lambda x: x[2])
        
        return options
    
    def get_closest_warehouse(
        self,
        source_warehouse_id: str,
        by: str = "distance"  # "distance", "time", "cost"
    ) -> Optional[Tuple[str, Dict[str, float]]]:
        """
        Obtiene el almacén más cercano según criterio.
        
        Args:
            source_warehouse_id: Almacén origen
            by: Criterio ("distance", "time", "cost")
        
        Returns:
            Tupla (target_warehouse_id, connection_info) o None
        """
        source = self.get_by_id(source_warehouse_id)
        
        if not source or not source.connections:
            return None
        
        best_option = None
        best_value = float('inf')
        
        for target_id, connection_info in source.connections.items():
            if by == "distance":
                value = connection_info.get('distance_km', float('inf'))
            elif by == "time":
                value = connection_info.get('transit_days', float('inf'))
            elif by == "cost":
                value = source.calculate_transfer_cost(1.0, target_id)
                if value is None:
                    value = float('inf')
            else:
                value = float('inf')
            
            if value < best_value:
                best_value = value
                best_option = (target_id, connection_info)
        
        return best_option
    
    def get_by_location(self, location: str) -> List[Warehouse]:
        """
        Obtiene almacenes en una ubicación.
        
        Args:
            location: Ubicación (ciudad o área)
        
        Returns:
            Lista de almacenes en esa ubicación
        """
        search_pattern = f"%{location}%"
        
        stmt = (
            select(Warehouse)
            .where(Warehouse.location.ilike(search_pattern))
            .order_by(Warehouse.warehouse_type)
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_capacity_utilization(self, warehouse_id: str) -> Optional[float]:
        """
        Obtiene utilización de capacidad de un almacén.
        
        Args:
            warehouse_id: ID del almacén
        
        Returns:
            Utilization rate (0.0-1.0) o None
        """
        warehouse = self.get_by_id(warehouse_id)
        
        if not warehouse:
            return None
        
        return warehouse.utilization_rate
    
    def get_warehouses_by_type(self, warehouse_type: WarehouseType) -> List[Warehouse]:
        """
        Obtiene almacenes por tipo.
        
        Args:
            warehouse_type: Tipo de almacén
        
        Returns:
            Lista de almacenes de ese tipo
        """
        stmt = (
            select(Warehouse)
            .where(
                and_(
                    Warehouse.warehouse_type == warehouse_type,
                    Warehouse.is_active == True
                )
            )
            .order_by(Warehouse.reliability_score.desc())
        )
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
