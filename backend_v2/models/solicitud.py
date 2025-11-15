"""
Modelo SQLAlchemy para Solicitudes y Materiales
Migrado desde v1.0 con normalización y mejoras
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, 
    Boolean, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from core.db import Base


class Material(Base):
    """
    Modelo de Material del catálogo
    v1.0 table: materiales
    """
    __tablename__ = "materiales"

    # Primary Key
    codigo = Column(String(100), primary_key=True)
    
    # Campos básicos
    descripcion = Column(String(500), nullable=False)
    descripcion_larga = Column(Text, nullable=True)
    unidad = Column(String(20), nullable=True)  # UNI, PZ, KG, etc.
    precio_usd = Column(Float, nullable=False, default=0.0)
    
    # Categorización
    centro = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    solicitud_items = relationship("SolicitudItem", back_populates="material")

    def __repr__(self):
        return f"<Material(codigo={self.codigo}, descripcion={self.descripcion})>"

    def to_dict(self):
        """Serializa a diccionario para responses"""
        return {
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "descripcion_larga": self.descripcion_larga,
            "unidad": self.unidad,
            "precio_usd": round(self.precio_usd, 2) if self.precio_usd else 0.0,
            "centro": self.centro,
            "sector": self.sector,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Solicitud(Base):
    """
    Modelo de Solicitud de Materiales
    v1.0 table: solicitudes
    """
    __tablename__ = "solicitudes"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Usuario solicitante
    id_usuario = Column(String(100), ForeignKey("users.username"), nullable=False)
    
    # Información de la solicitud
    centro = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=True)  # Opcional, puede ser None
    justificacion = Column(Text, nullable=False)
    centro_costos = Column(String(100), nullable=True)
    almacen_virtual = Column(String(100), nullable=True)
    
    # Criticidad
    criticidad = Column(String(20), nullable=False, default="Normal")
    fecha_necesidad = Column(DateTime, nullable=True)
    
    # Estado
    status = Column(
        String(50), 
        nullable=False, 
        default="draft",
        # Constraint para valores permitidos
    )
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'pendiente_de_aprobacion', 'aprobada', 'rechazada', "
            "'cancelada', 'finalizada', 'cancelacion_pendiente', 'cancelacion_rechazada', "
            "'en_tratamiento')",
            name="ck_solicitud_status"
        ),
    )
    
    # Aprobadores y planificadores
    aprobador_id = Column(String(100), ForeignKey("users.username"), nullable=True)
    planner_id = Column(String(100), ForeignKey("users.username"), nullable=True)
    
    # Monto total calculado
    total_monto = Column(Float, nullable=False, default=0.0)
    
    # Timestamps
    notificado_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usuario = relationship("User", foreign_keys=[id_usuario], backref="solicitudes")
    aprobador = relationship("User", foreign_keys=[aprobador_id], backref="solicitudes_aprobadas")
    planner = relationship("User", foreign_keys=[planner_id], backref="solicitudes_planificadas")
    items = relationship("SolicitudItem", back_populates="solicitud", cascade="all, delete-orphan")
    aprobaciones = relationship("Aprobacion", back_populates="solicitud", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Solicitud(id={self.id}, usuario={self.id_usuario}, status={self.status})>"

    @property
    def total_items(self) -> int:
        """Cantidad total de items en la solicitud"""
        items = object.__getattribute__(self, "__dict__").get("items")
        return len(items) if items else 0

    @property
    def total_cantidad(self) -> float:
        """Suma total de cantidades de todos los items"""
        items = object.__getattribute__(self, "__dict__").get("items")
        if not items:
            return 0.0
        return sum(item.cantidad for item in items)

    def to_dict(self, include_items: bool = False, include_aprobaciones: bool = False):
        """
        Serializa a diccionario para responses
        
        Args:
            include_items: Incluir lista de items
            include_aprobaciones: Incluir historial de aprobaciones
        """
        attrs = object.__getattribute__(self, "__dict__")
        
        result = {
            "id": attrs.get("id"),
            "id_usuario": attrs.get("id_usuario"),
            "centro": attrs.get("centro"),
            "sector": attrs.get("sector"),
            "justificacion": attrs.get("justificacion"),
            "centro_costos": attrs.get("centro_costos"),
            "almacen_virtual": attrs.get("almacen_virtual"),
            "criticidad": attrs.get("criticidad"),
            "fecha_necesidad": attrs.get("fecha_necesidad").isoformat() if attrs.get("fecha_necesidad") else None,
            "status": attrs.get("status"),
            "aprobador_id": attrs.get("aprobador_id"),
            "planner_id": attrs.get("planner_id"),
            "total_monto": round(attrs.get("total_monto", 0.0), 2),
            "total_items": self.total_items,
            "total_cantidad": self.total_cantidad,
            "notificado_at": attrs.get("notificado_at").isoformat() if attrs.get("notificado_at") else None,
            "created_at": attrs.get("created_at").isoformat() if attrs.get("created_at") else None,
            "updated_at": attrs.get("updated_at").isoformat() if attrs.get("updated_at") else None,
        }
        
        if include_items:
            result["items"] = [item.to_dict() for item in (self.items or [])]
        
        if include_aprobaciones:
            result["aprobaciones"] = [apr.to_dict() for apr in (self.aprobaciones or [])]
        
        return result


class SolicitudItem(Base):
    """
    Item individual de una solicitud
    v1.0: Almacenado en data_json, ahora normalizado
    """
    __tablename__ = "solicitud_items"

    # Primary Key
    id_item = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id", ondelete="CASCADE"), nullable=False)
    material_codigo = Column(String(100), ForeignKey("materiales.codigo"), nullable=False)
    
    # Datos del item
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=True)
    comentario = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    solicitud = relationship("Solicitud", back_populates="items")
    material = relationship("Material", back_populates="solicitud_items")

    def __repr__(self):
        return f"<SolicitudItem(id={self.id_item}, material={self.material_codigo}, cantidad={self.cantidad})>"

    @property
    def subtotal(self) -> float:
        """Calcula subtotal = cantidad * precio_unitario"""
        return round((self.cantidad or 0) * (self.precio_unitario or 0), 2)

    def to_dict(self):
        """Serializa a diccionario para responses"""
        attrs = object.__getattribute__(self, "__dict__")
        
        return {
            "id_item": attrs.get("id_item"),
            "solicitud_id": attrs.get("solicitud_id"),
            "material_codigo": attrs.get("material_codigo"),
            "cantidad": attrs.get("cantidad"),
            "precio_unitario": round(attrs.get("precio_unitario", 0.0), 2),
            "subtotal": self.subtotal,
            "comentario": attrs.get("comentario"),
            "created_at": attrs.get("created_at").isoformat() if attrs.get("created_at") else None,
        }


class Aprobacion(Base):
    """
    Registro de aprobaciones/rechazos de solicitudes
    v1.0: No existía tabla separada, se usaba data_json
    """
    __tablename__ = "aprobaciones"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id", ondelete="CASCADE"), nullable=False)
    
    # Usuario que aprobó/rechazó
    aprobador_id = Column(String(100), ForeignKey("users.username"), nullable=False)
    
    # Decisión
    decision = Column(String(20), nullable=False)  # "aprobada", "rechazada"
    comentario = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    solicitud = relationship("Solicitud", back_populates="aprobaciones")
    aprobador = relationship("User", foreign_keys=[aprobador_id])

    def __repr__(self):
        return f"<Aprobacion(id={self.id}, solicitud_id={self.solicitud_id}, decision={self.decision})>"

    def to_dict(self):
        """Serializa a diccionario para responses"""
        attrs = object.__getattribute__(self, "__dict__")
        
        return {
            "id": attrs.get("id"),
            "solicitud_id": attrs.get("solicitud_id"),
            "aprobador_id": attrs.get("aprobador_id"),
            "decision": attrs.get("decision"),
            "comentario": attrs.get("comentario"),
            "created_at": attrs.get("created_at").isoformat() if attrs.get("created_at") else None,
        }
