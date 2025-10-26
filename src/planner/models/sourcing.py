"""
Modelo de opciones y rutas de abastecimiento:
- Alternativas de abastecimiento por material
- Parámetros de costo, tiempo, confiabilidad
- Rutas operacionales (stock, compra, fabricación, etc.)
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class SourcingPathType(str, Enum):
    """Tipo de ruta de abastecimiento"""
    STOCK_LOCAL = "STOCK_LOCAL"              # Stock local
    STOCK_LIBERATION = "STOCK_LIBERATION"    # Liberar stock (remover reserva)
    DISASSEMBLY = "DISASSEMBLY"              # Desarmador de ensambles
    EQUIVALENT = "EQUIVALENT"                # Ítem equivalente
    RECOVERY = "RECOVERY"                    # Recupero (reciclaje/reacondicionamiento)
    MANUFACTURING = "MANUFACTURING"         # Fabricación interna
    TRANSFER = "TRANSFER"                    # Transferencia entre almacenes
    INTERCOMPANY = "INTERCOMPANY"           # Venta intercompany
    VMI = "VMI"                              # Vendor Managed Inventory
    LOAN = "LOAN"                            # Préstamo
    EXPEDITE = "EXPEDITE"                    # Acelerar (pago premium)
    PURCHASE = "PURCHASE"                    # Compra regular
    PURCHASE_IMPORT = "PURCHASE_IMPORT"      # Compra de importación


class SourcingOption(BaseModel):
    """Opción única de abastecimiento"""
    option_id: str = Field(..., description="ID único: item_id:path_type:supplier_id")
    item_id: str = Field(...)
    sourcing_path: SourcingPathType = Field(...)
    
    # Proveedor/Fuente
    supplier_id: Optional[str] = None  # None para stock local
    supplier_name: Optional[str] = None
    
    # Especificaciones técnicas
    quantity_available: float = Field(..., ge=0, description="Cantidad disponible por esta ruta")
    unit_of_measure: str = Field(...)
    
    # Costos
    unit_cost_usd: float = Field(..., ge=0)
    transportation_cost_usd: float = Field(default=0, ge=0)
    customs_duty_usd: float = Field(default=0, ge=0)
    handling_cost_usd: float = Field(default=0, ge=0)
    
    @property
    def total_cost_per_unit(self) -> float:
        """Costo total por unidad"""
        return (self.unit_cost_usd + 
                self.transportation_cost_usd + 
                self.customs_duty_usd + 
                self.handling_cost_usd)
    
    # Lead time
    lead_time_days_mean: float = Field(..., ge=0)
    lead_time_days_std: float = Field(default=0, ge=0)
    lead_time_days_p95: Optional[float] = None
    
    # Confiabilidad
    on_time_percentage: float = Field(default=0.95, ge=0, le=1)
    quality_acceptance_rate: float = Field(default=0.99, ge=0, le=1)
    availability_percentage: float = Field(default=0.95, ge=0, le=1)
    
    # Restricciones
    minimum_order_quantity: float = Field(default=0, ge=0)
    order_multiple: float = Field(default=1, ge=1)
    maximum_order_quantity: Optional[float] = None
    
    # Ventanas de tiempo
    order_deadline: Optional[datetime] = None
    delivery_window_start: Optional[datetime] = None
    delivery_window_end: Optional[datetime] = None
    
    # Metadata
    competitive_rank: int = Field(default=999, description="Ranking de competitividad")
    ranking_score: float = Field(default=0, description="Score multicriteria")
    feasible: bool = Field(default=True, description="¿Es técnicamente viable?")
    feasibility_notes: Optional[str] = None
    
    # Histórico
    last_used_date: Optional[datetime] = None
    success_rate: float = Field(default=0.95, ge=0, le=1, description="Tasa de éxito histórico")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "option_id": "MAT-001:PURCHASE:SUP-001",
                "item_id": "MAT-001",
                "sourcing_path": "PURCHASE",
                "supplier_id": "SUP-001",
                "supplier_name": "ABC Parts Inc",
                "quantity_available": 100.0,
                "unit_of_measure": "EA",
                "unit_cost_usd": 12.50,
                "lead_time_days_mean": 14.0,
                "on_time_percentage": 0.96,
                "quality_acceptance_rate": 0.99,
                "competitive_rank": 1,
            }
        }


class SourcingPath(BaseModel):
    """Ruta completa de abastecimiento con opciones jerarquizadas"""
    path_id: str = Field(..., description="ID de ruta: solicitud_id:material_id")
    solicitud_id: str = Field(...)
    material_id: str = Field(...)
    required_quantity: float = Field(..., ge=0)
    required_date: datetime = Field(...)
    
    # Opciones jerarquizadas por orden de preferencia
    options: List[SourcingOption] = Field(
        default_factory=list,
        description="Opciones ordenadas: stock → liberación → ... → compra"
    )
    
    # Resultado del planeamiento
    selected_option_id: Optional[str] = None
    selected_quantity: Optional[float] = None
    selected_cost: Optional[float] = None
    
    # Análisis de viabilidad
    total_feasible_quantity: float = Field(default=0, ge=0)
    total_feasible_cost: float = Field(default=0, ge=0)
    has_feasible_solution: bool = Field(default=False)
    
    # Metadata
    analyzed_at: Optional[datetime] = None
    optimized_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    def add_option(self, option: SourcingOption, rank: int = None) -> None:
        """Agregar opción a la ruta"""
        if rank is not None:
            self.options.insert(rank, option)
        else:
            self.options.append(option)
    
    def get_next_viable_option(self, skip_ids: List[str] = None) -> Optional[SourcingOption]:
        """Obtener próxima opción viable en orden jerarquizado"""
        skip_ids = skip_ids or []
        for option in self.options:
            if option.feasible and option.option_id not in skip_ids:
                if option.quantity_available >= self.required_quantity:
                    return option
        return None
    
    def calculate_total_feasible(self) -> None:
        """Calcular totales de cantidad y costo factibles"""
        self.total_feasible_quantity = sum(
            opt.quantity_available for opt in self.options if opt.feasible
        )
        self.total_feasible_cost = self.total_feasible_quantity * sum(
            opt.total_cost_per_unit for opt in self.options if opt.feasible
        ) / max(1, len([o for o in self.options if o.feasible]))
        self.has_feasible_solution = self.total_feasible_quantity >= self.required_quantity
    
    class Config:
        use_enum_values = True
