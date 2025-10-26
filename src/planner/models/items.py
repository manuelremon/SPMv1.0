"""
Modelo de maestro de ítems con soporte para:
- Unidades de medida (UoM) y conversiones
- Clasificación ABC
- Estructura de producto (BOM)
- Ítems equivalentes y sustitutos
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class ABCClassification(str, Enum):
    """Clasificación ABC para análisis de inventario"""
    A = "A"  # 80% del valor con 20% del volumen
    B = "B"  # 15% del valor con 30% del volumen
    C = "C"  # 5% del valor con 50% del volumen


class UnitOfMeasure(BaseModel):
    """Unidad de medida base"""
    code: str = Field(..., description="Código SAP/único de UoM (EA, KG, M, LT)")
    name: str = Field(..., description="Nombre descriptivo (Pieza, Kilogramo, Metro)")
    category: str = Field(..., description="Categoría (peso, longitud, cantidad)")
    conversion_to_base: float = Field(1.0, description="Factor para convertir a UoM base")
    
    class Config:
        use_enum_values = True


class BOMComponent(BaseModel):
    """Componente en lista de materiales (BOM)"""
    component_id: str = Field(..., description="ID del material componente")
    quantity: float = Field(..., ge=0, description="Cantidad requerida")
    unit_of_measure: str = Field(..., description="UoM del componente")
    sequence: int = Field(default=1, description="Secuencia en BOM")
    scrap_factor: float = Field(default=1.0, ge=1.0, description="Factor de desperdicio (1.05 = 5%)")
    
    class Config:
        use_enum_values = True


class EquivalentItem(BaseModel):
    """Ítem equivalente o sustituto"""
    equivalent_id: str = Field(..., description="ID del ítem equivalente")
    equivalent_code: str = Field(..., description="Código SAP del equivalente")
    conversion_factor: float = Field(default=1.0, ge=0, description="Factor conversión: equiv_qty = item_qty * factor")
    technical_specs_match: float = Field(default=0.9, ge=0, le=1, description="% de coincidencia técnica (0-1)")
    cost_differential: float = Field(default=0.0, description="Diferencia de costo vs. original (0.05 = +5%)")
    lead_time_delta: timedelta = Field(default_factory=timedelta, description="Diferencia en lead time")
    supplier_reliability: float = Field(default=0.95, ge=0, le=1, description="Confiabilidad del proveedor")
    notes: Optional[str] = None


class ItemMaster(BaseModel):
    """Maestro de material completo"""
    # Identificadores
    item_id: str = Field(..., description="ID único en el sistema")
    sap_code: str = Field(..., description="Código SAP")
    description: str = Field(..., description="Descripción técnica")
    long_description: Optional[str] = None
    
    # Clasificación
    abc_class: ABCClassification = Field(default=ABCClassification.C)
    criticality: str = Field(default="LOW", description="Criticidad: CRITICAL, HIGH, MEDIUM, LOW")
    procurement_type: str = Field(
        default="PURCHASE",
        description="Tipo: PURCHASE, MAKE, TRANSFER, IMPORT, VMI"
    )
    
    # Unidades y conversiones
    base_unit: str = Field(..., description="UoM base (EA, KG, etc.)")
    alternative_units: Dict[str, float] = Field(default_factory=dict, description="UoM alternativas y factores")
    
    # Especificaciones técnicas
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Specs técnicas (tensión, RPM, etc.)")
    
    # Cumplimiento normativo
    requires_traceability: bool = Field(default=False, description="¿Requiere trazabilidad?")
    compliance_standards: List[str] = Field(default_factory=list, description="Normas (ISO, FDA, etc.)")
    shelf_life_days: Optional[int] = Field(None, description="Vida útil en días (None = indefinida)")
    requires_cold_chain: bool = Field(default=False)
    
    # Estructura de producto
    is_assembly: bool = Field(default=False, description="¿Es un ensamble?")
    bom: List[BOMComponent] = Field(default_factory=list, description="Lista de materiales")
    
    # Ítems equivalentes
    equivalent_items: List[EquivalentItem] = Field(default_factory=list, description="Sustitutos autorizados")
    
    # Costos y precios
    standard_cost_usd: float = Field(default=0.0, ge=0, description="Costo estándar en USD")
    list_price_usd: float = Field(default=0.0, ge=0, description="Precio de lista en USD")
    annual_consumption_units: float = Field(default=0.0, ge=0, description="Consumo anual estimado")
    
    # Parámetros de control
    minimum_order_quantity: float = Field(default=1.0, ge=0)
    order_multiple: float = Field(default=1.0, ge=1, description="Múltiplo de orden (ej: pallet de 50)")
    safety_stock_days: float = Field(default=0, ge=0, description="Días de stock de seguridad")
    
    # Metadata
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("alternative_units")
    def validate_units(cls, v):
        """Validar que los factores sean positivos"""
        for unit, factor in v.items():
            if factor <= 0:
                raise ValueError(f"Factor para {unit} debe ser > 0")
        return v
    
    def get_quantity_in_base_unit(self, quantity: float, from_unit: str) -> float:
        """Convertir cantidad a UoM base"""
        if from_unit == self.base_unit:
            return quantity
        if from_unit in self.alternative_units:
            return quantity * self.alternative_units[from_unit]
        raise ValueError(f"UoM desconocida: {from_unit}")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "item_id": "MAT-001",
                "sap_code": "100001",
                "description": "Rodamiento 6208-2Z",
                "abc_class": "B",
                "criticality": "HIGH",
                "procurement_type": "PURCHASE",
                "base_unit": "EA",
                "standard_cost_usd": 12.50,
                "shelf_life_days": None,
                "requires_traceability": False,
            }
        }
