"""
Modelos de proveedores para Planner.

Gestiona información de suppliers para algoritmos de optimización.
"""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, JSON, Enum, Index, ForeignKey
)
from sqlalchemy.orm import relationship
from core.db import Base


class SupplierRating(str, PyEnum):
    """Calificación de proveedor"""
    PREFERRED = "PREFERRED"    # Proveedor preferido
    APPROVED = "APPROVED"      # Aprobado
    CONDITIONAL = "CONDITIONAL"  # Con condiciones
    PROBATION = "PROBATION"    # En prueba
    BLOCKED = "BLOCKED"        # Bloqueado


class Supplier(Base):
    """
    Maestro de proveedores.
    
    Gestiona:
    - Información general del proveedor
    - Rating y confiabilidad
    - Plazos de entrega promedio
    - Condiciones de pago
    - Categorías de materiales que suministra
    """
    __tablename__ = "planner_supplier"
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String(50), unique=True, nullable=False, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    
    # Información de contacto
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    # Clasificación y rating
    rating = Column(Enum(SupplierRating), default=SupplierRating.APPROVED, nullable=False)
    reliability_score = Column(Float, default=0.9)  # 0.0 - 1.0
    quality_score = Column(Float, default=0.9)      # 0.0 - 1.0
    on_time_delivery_rate = Column(Float, default=0.95)  # 0.0 - 1.0
    
    # Plazos y condiciones
    average_lead_time_days = Column(Integer, default=15)
    minimum_order_value_usd = Column(Float, default=0.0)
    payment_terms_days = Column(Integer, default=30)
    
    # Capacidades
    categories_supplied = Column(JSON, default=list)  # ["RAW_MATERIALS", "COMPONENTS"]
    certifications = Column(JSON, default=list)       # ["ISO9001", "ISO14001"]
    geographical_coverage = Column(JSON, default=list)  # ["ARGENTINA", "BRAZIL"]
    
    # Estado
    is_active = Column(Boolean, default=True)
    blocked_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_agreements = relationship("SupplierPriceAgreement", back_populates="supplier", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_supplier_rating', 'rating'),
        Index('idx_supplier_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Supplier {self.supplier_code}: {self.name}>"


class SupplierPriceAgreement(Base):
    """
    Acuerdo de precio con proveedor para un ítem específico.
    
    Define:
    - Precio unitario acordado
    - MOQ (Minimum Order Quantity)
    - Vigencia del acuerdo
    - Plazos de entrega específicos
    """
    __tablename__ = "planner_supplier_price_agreement"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("planner_supplier.id"), nullable=False)
    item_id = Column(String(50), nullable=False)  # Reference to ItemMaster.item_id
    
    # Pricing
    unit_price_usd = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    moq = Column(Float, default=1.0)  # Minimum Order Quantity
    order_multiple = Column(Float, default=1.0)
    
    # Lead time específico (override del proveedor)
    lead_time_days = Column(Integer, nullable=True)
    
    # Vigencia
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=True)  # None = indefinida
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="price_agreements")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_agreement_supplier', 'supplier_id'),
        Index('idx_price_agreement_item', 'item_id'),
        Index('idx_price_agreement_validity', 'valid_from', 'valid_to'),
    )
    
    def is_valid(self, as_of_date: Optional[datetime] = None) -> bool:
        """
        Verifica si el acuerdo está vigente.
        
        Args:
            as_of_date: Fecha a verificar (default: hoy)
        
        Returns:
            True si el acuerdo está vigente
        """
        check_date = as_of_date or datetime.utcnow()
        
        if check_date < self.valid_from:
            return False
        
        if self.valid_to is not None and check_date > self.valid_to:
            return False
        
        return True
    
    def __repr__(self):
        return f"<PriceAgreement Supplier:{self.supplier_id} Item:{self.item_id} ${self.unit_price_usd}>"
