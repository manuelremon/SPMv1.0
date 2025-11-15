"""
Modelos de inventario con trazabilidad completa.

Adaptado de src/planner/models/inventory.py a SQLAlchemy.
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from core.db import Base


class QCStatus(str, PyEnum):
    """Estados de control de calidad"""
    INSPECTING = "INSPECTING"    # En inspección
    APPROVED = "APPROVED"        # Aprobado
    CONDITIONAL = "CONDITIONAL"  # Aprobado con condiciones
    REJECTED = "REJECTED"        # Rechazado
    QUARANTINE = "QUARANTINE"    # Cuarentena


class InventoryLot(Base):
    """
    Lote de inventario con trazabilidad completa.
    
    Gestiona:
    - Cantidades (recibida, disponible, reservada, asignada)
    - Control de calidad
    - Ubicaciones físicas
    - Trazabilidad de proveedor
    - Fechas de vencimiento
    """
    __tablename__ = "planner_inventory_lot"
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_number = Column(String(50), unique=True, nullable=False, index=True)
    serial_number = Column(String(50), nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("planner_item_master.id"), nullable=False)
    
    # Cantidades
    quantity_received = Column(Float, nullable=False)  # Total recibida
    quantity_on_hand = Column(Float, nullable=False)   # Disponible en almacén
    quantity_reserved_hard = Column(Float, default=0.0)  # Reservas confirmadas
    quantity_reserved_soft = Column(Float, default=0.0)  # Reservas tentativas
    quantity_allocated = Column(Float, default=0.0)    # Asignadas a SO (salidas)
    
    # Fechas
    receipt_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)  # None = no aplica
    shelf_life_days = Column(Integer, nullable=True)
    
    # Control de Calidad (QC)
    qc_status = Column(Enum(QCStatus), default=QCStatus.INSPECTING, nullable=False)
    qc_approver = Column(String(100), nullable=True)
    qc_date = Column(DateTime, nullable=True)
    qc_notes = Column(Text, nullable=True)
    
    # Trazabilidad
    supplier_id = Column(String(50), nullable=True)
    purchase_order = Column(String(50), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("ItemMaster", back_populates="inventory_lots")
    locations = relationship("LotLocation", back_populates="lot", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity_on_hand >= 0', name='check_qoh_positive'),
        CheckConstraint('quantity_reserved_hard >= 0', name='check_reserved_hard_positive'),
        CheckConstraint('quantity_reserved_soft >= 0', name='check_reserved_soft_positive'),
        CheckConstraint('quantity_allocated >= 0', name='check_allocated_positive'),
        Index('idx_lot_item', 'item_id'),
        Index('idx_lot_status', 'qc_status'),
        Index('idx_lot_supplier', 'supplier_id'),
        Index('idx_lot_expiration', 'expiration_date'),
    )
    
    @property
    def quantity_available(self) -> float:
        """
        Cantidad disponible para nueva asignación.
        
        Fórmula: QoH - reservas_hard - reservas_soft - allocated
        """
        return (
            self.quantity_on_hand
            - self.quantity_reserved_hard
            - self.quantity_reserved_soft
            - self.quantity_allocated
        )
    
    @property
    def is_expired(self) -> bool:
        """¿El lote está vencido?"""
        if self.expiration_date is None:
            return False
        return datetime.utcnow() > self.expiration_date
    
    @property
    def days_to_expiration(self) -> Optional[int]:
        """Días hasta expiración (None si no aplica)"""
        if self.expiration_date is None:
            return None
        delta = self.expiration_date - datetime.utcnow()
        return max(0, delta.days)
    
    def is_critical_expiration(self, threshold_days: int = 30) -> bool:
        """
        ¿El lote está próximo a vencer?
        
        Args:
            threshold_days: Umbral en días
        
        Returns:
            True si vence en <= threshold_days
        """
        days = self.days_to_expiration
        if days is None:
            return False
        return days <= threshold_days
    
    def can_allocate(self, quantity: float) -> bool:
        """
        ¿Se puede asignar la cantidad solicitada?
        
        Args:
            quantity: Cantidad a asignar
        
        Returns:
            True si quantity <= quantity_available
        """
        return self.quantity_available >= quantity
    
    def __repr__(self):
        return f"<InventoryLot {self.lot_number} - QoH:{self.quantity_on_hand} Avail:{self.quantity_available}>"


class LotLocation(Base):
    """
    Ubicación física de un lote en el almacén.
    
    Estructura jerárquica:
    - Warehouse → Zone → Rack → Level → Position
    """
    __tablename__ = "planner_lot_location"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("planner_inventory_lot.id"), nullable=False)
    
    # Ubicación jerárquica
    warehouse_code = Column(String(20), nullable=False)  # ALM-1
    zone = Column(String(20), nullable=True)            # REC, STO, SHP
    rack = Column(String(20), nullable=True)            # R01, R02
    level = Column(String(10), nullable=True)           # A, B, C
    position = Column(String(10), nullable=True)        # 01, 02
    
    quantity = Column(Float, nullable=False)  # Cantidad en esta ubicación
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lot = relationship("InventoryLot", back_populates="locations")
    
    # Indexes
    __table_args__ = (
        Index('idx_location_lot', 'lot_id'),
        Index('idx_location_warehouse', 'warehouse_code'),
    )
    
    def full_location(self) -> str:
        """
        Retorna ubicación formateada.
        
        Returns:
            "ALM-1-REC-R02-A-01" o componentes disponibles
        """
        parts = [self.warehouse_code]
        if self.zone:
            parts.append(self.zone)
        if self.rack:
            parts.append(self.rack)
        if self.level:
            parts.append(self.level)
        if self.position:
            parts.append(self.position)
        
        return "-".join(parts)
    
    def __repr__(self):
        return f"<LotLocation {self.full_location()} Qty:{self.quantity}>"
