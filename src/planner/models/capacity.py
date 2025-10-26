"""
Modelo de capacidades y restricciones:
- Capacidad de recursos (máquinas, proveedores, almacenes)
- Restricciones de tiempo (lead time, availability windows)
- Limitaciones técnicas y normativas
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field, validator


class CapacityType(str, Enum):
    """Tipo de capacidad"""
    SUPPLIER_CAPACITY = "SUPPLIER_CAPACITY"      # Capacidad de producción del proveedor
    WAREHOUSE_CAPACITY = "WAREHOUSE_CAPACITY"    # Espacio en almacén
    TRANSPORT_CAPACITY = "TRANSPORT_CAPACITY"    # Capacidad de transporte
    MACHINE_CAPACITY = "MACHINE_CAPACITY"        # Capacidad de máquina (para fabricación)
    CASH_FLOW = "CASH_FLOW"                      # Límite de flujo de caja
    CUSTOMS_CAPACITY = "CUSTOMS_CAPACITY"        # Capacidad aduanal


class ResourceCapacity(BaseModel):
    """Capacidad de un recurso"""
    resource_id: str = Field(..., description="ID del recurso (proveedor, almacén, etc.)")
    resource_type: str = Field(..., description="Tipo: SUPPLIER, WAREHOUSE, CUSTOMS")
    capacity_type: CapacityType = Field(...)
    
    # Capacidad
    capacity_value: float = Field(..., ge=0, description="Valor de capacidad disponible")
    capacity_unit: str = Field(..., description="Unidad (kg, piezas, m³, USD, etc.)")
    
    # Ocupación
    reserved_value: float = Field(default=0, ge=0, description="Valor reservado")
    allocated_value: float = Field(default=0, ge=0, description="Valor asignado")
    
    # Ventanas de disponibilidad
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    @property
    def available_capacity(self) -> float:
        """Capacidad realmente disponible"""
        return max(0, self.capacity_value - self.reserved_value - self.allocated_value)
    
    @property
    def utilization_percentage(self) -> float:
        """% utilizado"""
        if self.capacity_value <= 0:
            return 0
        return ((self.reserved_value + self.allocated_value) / self.capacity_value) * 100
    
    def can_allocate(self, required_value: float) -> bool:
        """¿Puede asignarse la cantidad requerida?"""
        return self.available_capacity >= required_value
    
    def allocate(self, value: float, is_hard: bool = True) -> bool:
        """Asignar capacidad"""
        if not self.can_allocate(value):
            return False
        
        if is_hard:
            self.allocated_value += value
        else:
            self.reserved_value += value
        
        self.updated_at = datetime.utcnow()
        return True
    
    def release(self, value: float, is_hard: bool = True) -> None:
        """Liberar capacidad"""
        if is_hard:
            self.allocated_value = max(0, self.allocated_value - value)
        else:
            self.reserved_value = max(0, self.reserved_value - value)
        
        self.updated_at = datetime.utcnow()
    
    class Config:
        use_enum_values = True


class CapacityConstraint(BaseModel):
    """Restricción de capacidad en una solicitud"""
    constraint_id: str = Field(..., description="ID único de restricción")
    solicitud_id: str = Field(..., description="ID de la solicitud")
    
    # Restricción
    resource_id: str = Field(..., description="Recurso restringido")
    required_value: float = Field(..., ge=0, description="Valor requerido")
    capacity_unit: str = Field(...)
    
    # Ventana de tiempo
    required_by_date: Optional[datetime] = None
    latest_possible_date: Optional[datetime] = None
    
    # Prioridad
    priority: int = Field(default=100, ge=1, le=1000, description="Prioridad (1=crítica, 1000=baja)")
    
    # Status
    is_satisfied: bool = Field(default=False)
    satisfaction_date: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    def mark_satisfied(self) -> None:
        """Marcar restricción como satisfecha"""
        self.is_satisfied = True
        self.satisfaction_date = datetime.utcnow()
    
    class Config:
        use_enum_values = True
