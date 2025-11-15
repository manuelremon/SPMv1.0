"""
Modelos de almacenes para Planner.

Gestiona ubicaciones de almacenamiento y parámetros operativos.
"""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, JSON, Enum, Index
)
from core.db import Base


class WarehouseType(str, PyEnum):
    """Tipos de almacén"""
    CENTRAL = "CENTRAL"          # Almacén central
    REGIONAL = "REGIONAL"        # Almacén regional
    FIELD = "FIELD"              # Almacén de campo
    CONSIGNMENT = "CONSIGNMENT"  # Consignación
    VMI = "VMI"                  # Vendor Managed Inventory


class Warehouse(Base):
    """
    Maestro de almacenes.
    
    Gestiona:
    - Ubicación geográfica
    - Capacidades operativas
    - Costos de operación
    - Conectividad con otros almacenes
    """
    __tablename__ = "planner_warehouse"
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(50), unique=True, nullable=False, index=True)
    warehouse_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    warehouse_type = Column(Enum(WarehouseType), default=WarehouseType.REGIONAL, nullable=False)
    
    # Ubicación geográfica
    location = Column(String(255), nullable=True)  # Ciudad o área
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")
    
    # Capacidades
    total_capacity_cubic_meters = Column(Float, nullable=True)
    total_capacity_pallets = Column(Integer, nullable=True)
    utilization_rate = Column(Float, default=0.0)  # 0.0 - 1.0
    
    # Costos operativos (por hora)
    picking_cost_per_hour = Column(Float, default=25.0)
    packing_cost_per_hour = Column(Float, default=20.0)
    shipping_cost_per_hour = Column(Float, default=35.0)
    coordination_cost_per_hour = Column(Float, default=40.0)
    
    # Parámetros operativos
    operates_24_7 = Column(Boolean, default=False)
    working_hours_per_day = Column(Integer, default=8)
    average_picking_time_hours = Column(Float, default=0.5)
    average_packing_time_hours = Column(Float, default=0.25)
    
    # Conectividad (JSON con distancias a otros almacenes)
    # {"WH-02": {"distance_km": 350, "transit_days": 2}, ...}
    connections = Column(JSON, default=dict)
    
    # Confiabilidad
    reliability_score = Column(Float, default=0.95)  # 0.0 - 1.0
    on_time_shipping_rate = Column(Float, default=0.9)  # 0.0 - 1.0
    
    # Estado
    is_active = Column(Boolean, default=True)
    manager_name = Column(String(255), nullable=True)
    manager_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_warehouse_type', 'warehouse_type'),
        Index('idx_warehouse_active', 'is_active'),
        Index('idx_warehouse_location', 'location'),
    )
    
    def get_transfer_info(self, target_warehouse_id: str) -> Optional[dict]:
        """
        Obtiene información de transferencia a otro almacén.
        
        Args:
            target_warehouse_id: ID del almacén destino
        
        Returns:
            Dict con distance_km y transit_days, o None si no hay conexión
        """
        return self.connections.get(target_warehouse_id)
    
    def calculate_transfer_cost(self, quantity: float, target_warehouse_id: str) -> float:
        """
        Calcula costo de transferencia a otro almacén.
        
        Formula simplificada basada en TDABC:
        - Picking: 0.5h * $25
        - Packing: 0.25h * $20
        - Shipping: (distance_km / 500) * $35/h
        - Coordination: 1h * $40
        
        Args:
            quantity: Cantidad a transferir
            target_warehouse_id: ID del almacén destino
        
        Returns:
            Costo total en USD
        """
        transfer_info = self.get_transfer_info(target_warehouse_id)
        if not transfer_info:
            return float('inf')  # No hay ruta disponible
        
        distance_km = transfer_info.get('distance_km', 0)
        
        # Actividades TDABC
        picking_cost = self.average_picking_time_hours * self.picking_cost_per_hour
        packing_cost = self.average_packing_time_hours * self.packing_cost_per_hour
        shipping_cost = (distance_km / 500) * self.shipping_cost_per_hour
        coordination_cost = 1.0 * self.coordination_cost_per_hour
        
        total_cost = picking_cost + packing_cost + shipping_cost + coordination_cost
        
        # Costo por unidad (mínimo 1 unidad)
        return total_cost / max(quantity, 1.0)
    
    def __repr__(self):
        return f"<Warehouse {self.warehouse_code}: {self.name}>"
