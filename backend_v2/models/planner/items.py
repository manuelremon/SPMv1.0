"""
Modelos de ítems y estructura de producto para Planner.

Adaptado de src/planner/models/items.py a SQLAlchemy.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum, Index
)
from sqlalchemy.orm import relationship
from core.db import Base


class ABCClassification(str, PyEnum):
    """Clasificación ABC para análisis de inventario"""
    A = "A"  # 80% del valor con 20% del volumen
    B = "B"  # 15% del valor con 30% del volumen
    C = "C"  # 5% del valor con 50% del volumen


class ItemCriticality(str, PyEnum):
    """Niveles de criticidad de materiales"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ProcurementType(str, PyEnum):
    """Tipos de abastecimiento"""
    PURCHASE = "PURCHASE"     # Compra a proveedor
    MAKE = "MAKE"             # Fabricación interna
    TRANSFER = "TRANSFER"     # Transferencia entre almacenes
    IMPORT = "IMPORT"         # Importación directa
    VMI = "VMI"               # Vendor Managed Inventory


class ItemMaster(Base):
    """
    Maestro de materiales completo con soporte para:
    - Clasificación ABC y criticidad
    - Unidades de medida y conversiones
    - Estructura de producto (BOM)
    - Ítems equivalentes
    - Parámetros de control
    """
    __tablename__ = "planner_item_master"
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(50), unique=True, nullable=False, index=True)
    sap_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=False)
    long_description = Column(Text, nullable=True)
    
    # Clasificación
    abc_class = Column(Enum(ABCClassification), default=ABCClassification.C, nullable=False)
    criticality = Column(Enum(ItemCriticality), default=ItemCriticality.LOW, nullable=False)
    procurement_type = Column(Enum(ProcurementType), default=ProcurementType.PURCHASE, nullable=False)
    
    # Unidades de medida
    base_unit = Column(String(10), nullable=False)  # EA, KG, M, LT
    alternative_units = Column(JSON, default=dict)  # {"BOX": 10, "PALLET": 500}
    
    # Especificaciones técnicas (JSON flexible)
    specifications = Column(JSON, default=dict)  # {"voltage": "220V", "rpm": 1500}
    
    # Cumplimiento normativo
    requires_traceability = Column(Boolean, default=False)
    compliance_standards = Column(JSON, default=list)  # ["ISO9001", "FDA"]
    shelf_life_days = Column(Integer, nullable=True)  # None = indefinida
    requires_cold_chain = Column(Boolean, default=False)
    
    # Estructura de producto
    is_assembly = Column(Boolean, default=False)
    
    # Costos y precios
    standard_cost_usd = Column(Float, default=0.0)
    list_price_usd = Column(Float, default=0.0)
    annual_consumption_units = Column(Float, default=0.0)
    
    # Parámetros de control
    minimum_order_quantity = Column(Float, default=1.0)
    order_multiple = Column(Float, default=1.0)
    safety_stock_days = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bom_components = relationship("BOMComponent", back_populates="parent_item", cascade="all, delete-orphan")
    equivalent_items = relationship("EquivalentItem", back_populates="item", cascade="all, delete-orphan")
    inventory_lots = relationship("InventoryLot", back_populates="item")
    
    # Indexes
    __table_args__ = (
        Index('idx_item_abc_criticality', 'abc_class', 'criticality'),
        Index('idx_item_procurement_type', 'procurement_type'),
    )
    
    def get_quantity_in_base_unit(self, quantity: float, from_unit: str) -> float:
        """
        Convierte cantidad de una UoM alternativa a la UoM base.
        
        Args:
            quantity: Cantidad en from_unit
            from_unit: Unidad origen
        
        Returns:
            Cantidad en base_unit
        """
        if from_unit == self.base_unit:
            return quantity
        
        conversion_factor = self.alternative_units.get(from_unit)
        if conversion_factor is None:
            raise ValueError(f"Unidad {from_unit} no definida para {self.item_id}")
        
        return quantity * conversion_factor
    
    def __repr__(self):
        return f"<ItemMaster {self.item_id} ({self.sap_code}) - {self.description[:30]}>"


class BOMComponent(Base):
    """
    Componente en lista de materiales (BOM).
    
    Define la estructura de producto:
    - Ensamble padre → Componentes
    - Cantidades y unidades
    - Factor de desperdicio
    """
    __tablename__ = "planner_bom_component"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_item_id = Column(Integer, ForeignKey("planner_item_master.id"), nullable=False)
    component_id = Column(String(50), nullable=False)  # ID del material componente
    quantity = Column(Float, nullable=False)  # Cantidad requerida
    unit_of_measure = Column(String(10), nullable=False)  # UoM del componente
    sequence = Column(Integer, default=1)  # Secuencia de ensamble
    scrap_factor = Column(Float, default=1.0)  # 1.05 = 5% desperdicio
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent_item = relationship("ItemMaster", back_populates="bom_components")
    
    # Indexes
    __table_args__ = (
        Index('idx_bom_parent', 'parent_item_id'),
        Index('idx_bom_component', 'component_id'),
    )
    
    def get_effective_quantity(self) -> float:
        """Retorna cantidad incluyendo factor de desperdicio"""
        return self.quantity * self.scrap_factor
    
    def __repr__(self):
        return f"<BOMComponent {self.component_id} x{self.quantity} {self.unit_of_measure}>"


class EquivalentItem(Base):
    """
    Ítem equivalente o sustituto autorizado.
    
    Define materiales intercambiables con:
    - Factor de conversión técnica
    - Diferencial de costo
    - Confiabilidad del proveedor
    """
    __tablename__ = "planner_equivalent_item"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("planner_item_master.id"), nullable=False)
    equivalent_id = Column(String(50), nullable=False)  # ID del equivalente
    equivalent_code = Column(String(50), nullable=False)  # Código SAP equivalente
    
    # Conversión técnica
    conversion_factor = Column(Float, default=1.0)  # equiv_qty = item_qty * factor
    technical_specs_match = Column(Float, default=0.9)  # % coincidencia (0-1)
    
    # Diferencias operativas
    cost_differential = Column(Float, default=0.0)  # 0.05 = +5% más caro
    lead_time_delta_days = Column(Integer, default=0)  # +/- días vs original
    supplier_reliability = Column(Float, default=0.95)  # Confiabilidad (0-1)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("ItemMaster", back_populates="equivalent_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_equiv_item', 'item_id'),
        Index('idx_equiv_id', 'equivalent_id'),
    )
    
    def __repr__(self):
        return f"<EquivalentItem {self.equivalent_id} for {self.item_id}>"
