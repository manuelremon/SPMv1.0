"""
Modelo de inventario con soporte para:
- Lotes con trazabilidad
- Ubicaciones de almacén
- Estados de calidad (QC)
- Reservas duras/blandas
- Control FEFO (First Expire, First Out)
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field, validator


class QCStatus(str, Enum):
    """Estado de calidad del lote"""
    INSPECTING = "INSPECTING"      # En inspección
    APPROVED = "APPROVED"          # Aprobado
    CONDITIONAL = "CONDITIONAL"    # Aprobado condicionalmente
    REJECTED = "REJECTED"          # Rechazado
    QUARANTINE = "QUARANTINE"      # En cuarentena


class LotLocation(BaseModel):
    """Ubicación física de un lote"""
    warehouse_code: str = Field(..., description="Código de almacén (ALM-1, ALM-2)")
    zone: str = Field(..., description="Zona (recepción, almacenaje, obsoletos)")
    rack: str = Field(..., description="Estante/Rack")
    level: int = Field(..., ge=1, description="Nivel (1, 2, 3...)")
    position: str = Field(..., description="Posición (A1, B5, etc.)")
    
    def full_location(self) -> str:
        """Ubicación completa formateada"""
        return f"{self.warehouse_code}-{self.zone}-{self.rack}-{self.level}-{self.position}"


class InventoryLot(BaseModel):
    """Lote único de material con trazabilidad"""
    # Identificación
    lot_number: str = Field(..., description="Número de lote (SAP/proveedor)")
    serial_number: Optional[str] = None  # Para series
    item_id: str = Field(..., description="ID del material")
    
    # Cantidad
    quantity_received: float = Field(..., ge=0, description="Cantidad recibida")
    quantity_on_hand: float = Field(..., ge=0, description="Cantidad disponible")
    quantity_reserved_hard: float = Field(default=0, ge=0, description="Reservas duras (confirmadas)")
    quantity_reserved_soft: float = Field(default=0, ge=0, description="Reservas blandas (tentativas)")
    quantity_allocated: float = Field(default=0, ge=0, description="Asignadas a SO (salidas)")
    
    # Fechas
    receipt_date: datetime = Field(..., description="Fecha de recepción")
    expiration_date: Optional[datetime] = None  # Vencimiento (None = no aplica)
    shelf_life_days: Optional[int] = None  # Vida útil en días
    
    # Calidad
    qc_status: QCStatus = Field(default=QCStatus.INSPECTING)
    qc_approver: Optional[str] = None
    qc_date: Optional[datetime] = None
    qc_notes: Optional[str] = None
    
    # Ubicación física
    locations: List[LotLocation] = Field(default_factory=list, description="Ubicaciones ocupadas")
    
    # Trazabilidad
    supplier_id: str = Field(..., description="ID del proveedor")
    purchase_order: str = Field(..., description="Orden de compra")
    invoice_number: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_movement_date: Optional[datetime] = None
    
    @validator("quantity_on_hand")
    def validate_qty_available(cls, v, values):
        """Validar que qty_on_hand <= qty_received"""
        if "quantity_received" in values and v > values["quantity_received"]:
            raise ValueError("Cantidad disponible no puede exceder cantidad recibida")
        return v
    
    @property
    def quantity_available(self) -> float:
        """Cantidad verdaderamente disponible (sin reservas)"""
        return max(0, self.quantity_on_hand - self.quantity_reserved_hard - self.quantity_allocated)
    
    @property
    def is_expired(self) -> bool:
        """¿El lote expiró?"""
        if self.expiration_date is None:
            return False
        return datetime.utcnow() > self.expiration_date
    
    @property
    def days_to_expiration(self) -> Optional[int]:
        """Días para expiración"""
        if self.expiration_date is None:
            return None
        delta = self.expiration_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_critical_expiration(self, threshold_days: int = 30) -> bool:
        """¿Está próximo a expirar? (dentro de 30 días por defecto)"""
        dte = self.days_to_expiration
        return dte is not None and dte <= threshold_days
    
    class Config:
        use_enum_values = True


class InventorySnapshot(BaseModel):
    """Fotografía de inventario en un momento del tiempo"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    warehouse_code: str = Field(..., description="Almacén")
    item_id: str = Field(...)
    
    # Totales
    total_on_hand: float = Field(..., ge=0)
    total_reserved_hard: float = Field(default=0, ge=0)
    total_reserved_soft: float = Field(default=0, ge=0)
    total_allocated: float = Field(default=0, ge=0)
    
    # Distribución por lote
    lots: List[InventoryLot] = Field(default_factory=list)
    
    # Salud del inventario
    expired_quantity: float = Field(default=0, ge=0)
    critical_expiration_quantity: float = Field(default=0, ge=0)
    quality_hold_quantity: float = Field(default=0, ge=0)
    
    # Análisis FEFO
    oldest_lot_receipt_date: Optional[datetime] = None
    
    @property
    def quantity_available(self) -> float:
        """Cantidad realmente disponible"""
        return max(0, 
                   self.total_on_hand - 
                   self.total_reserved_hard - 
                   self.total_allocated -
                   self.expired_quantity -
                   self.quality_hold_quantity
        )
    
    def get_allocation_sequence_fefo(self) -> List[InventoryLot]:
        """Retorna lotes ordenados por FEFO (First Expire, First Out)"""
        approved_lots = [
            lot for lot in self.lots 
            if lot.qc_status == QCStatus.APPROVED and not lot.is_expired
        ]
        # Ordenar por fecha expiración (ascendente) y luego por recepción (ascendente)
        return sorted(
            approved_lots,
            key=lambda x: (x.expiration_date or datetime.max, x.receipt_date)
        )
    
    class Config:
        use_enum_values = True
