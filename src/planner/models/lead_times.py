"""
Modelo de lead times con distribuciones probabilísticas:
- Lead times como distribuciones N(μ, σ²)
- Histórico para actualización bayesiana
- Variabilidad por proveedor/ruta
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator
import statistics


class LeadTimeDistribution(BaseModel):
    """Distribución de lead time en días"""
    # Parámetros
    mean_days: float = Field(..., ge=0.1, description="Media (μ) en días")
    std_dev_days: float = Field(default=0.0, ge=0, description="Desviación estándar (σ) en días")
    min_days: float = Field(default=0.1, ge=0.1, description="Lead time mínimo realista")
    max_days: float = Field(default=365, ge=0.1, description="Lead time máximo realista")
    
    # Percentiles
    p50_days: Optional[float] = None  # Mediana
    p95_days: Optional[float] = None  # 95-percentil (servicio level)
    p99_days: Optional[float] = None  # 99-percentil (peor caso)
    
    # Metadata
    confidence_level: float = Field(default=0.75, ge=0, le=1, description="Confianza en la estimación (0-1)")
    sample_size: int = Field(default=0, description="Número de observaciones")
    
    def calculate_service_level_lead_time(self, service_level: float = 0.95) -> float:
        """Calcular LT para nivel de servicio usando distribución normal"""
        import math
        if self.std_dev_days == 0:
            return self.mean_days
        
        # Z-score para nivel de servicio
        z = {
            0.50: 0.0,
            0.68: 1.0,
            0.90: 1.282,
            0.95: 1.645,
            0.99: 2.326,
        }
        z_value = z.get(service_level, 1.645)
        
        return self.mean_days + z_value * self.std_dev_days
    
    def update_with_observation(self, actual_lead_time_days: float, weight: float = 1.0) -> None:
        """Actualizar distribución con observación real (bayesiano simplificado)"""
        # Ajuste simple: mover media hacia observación
        alpha = weight / (weight + self.sample_size + 1)
        self.mean_days = (1 - alpha) * self.mean_days + alpha * actual_lead_time_days
        self.sample_size += 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "mean_days": 14.0,
                "std_dev_days": 3.5,
                "min_days": 7,
                "max_days": 30,
                "p95_days": 20.7,
                "confidence_level": 0.90,
                "sample_size": 45,
            }
        }


class LeadTimeHistory(BaseModel):
    """Histórico de entregas para análisis de lead times"""
    # Identificadores
    item_id: str = Field(...)
    supplier_id: str = Field(...)
    sourcing_path: str = Field(..., description="Ruta: STOCK, PURCHASE, IMPORT, etc.")
    
    # Observaciones
    purchase_order: str = Field(...)
    po_date: datetime = Field(...)
    promised_date: Optional[datetime] = None
    actual_delivery_date: datetime = Field(...)
    
    # Análisis
    promised_lead_time_days: Optional[int] = None
    actual_lead_time_days: int = Field(...)
    variance_days: Optional[int] = None  # Positivo = retraso
    on_time: bool = Field(...)
    
    # Calidad de entrega
    quantity_delivered: float = Field(..., ge=0)
    quantity_short: float = Field(default=0, ge=0)
    quality_issues: Optional[str] = None
    
    # Metadata
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    @validator("variance_days", always=True)
    def calculate_variance(cls, v, values):
        """Calcular varianza si no se proporciona"""
        if v is None and "promised_date" in values and "actual_delivery_date" in values:
            if values["promised_date"]:
                delta = values["actual_delivery_date"] - values["promised_date"]
                return delta.days
        return v
    
    @validator("on_time", always=True)
    def check_on_time(cls, v, values):
        """Validar si llegó a tiempo"""
        if "promised_date" in values and "actual_delivery_date" in values:
            if values["promised_date"]:
                return values["actual_delivery_date"] <= values["promised_date"]
        return True
    
    class Config:
        use_enum_values = True


class LeadTimeEstimate(BaseModel):
    """Estimación de lead time por ruta/proveedor"""
    item_id: str = Field(...)
    supplier_id: str = Field(...)
    sourcing_path: str = Field(..., description="Ruta: STOCK, PURCHASE, IMPORT, TRANSFER, etc.")
    
    # Distribuciones
    distribution: LeadTimeDistribution = Field(...)
    
    # Performance
    historical_data: List[LeadTimeHistory] = Field(default_factory=list)
    on_time_percentage: float = Field(default=0.95, ge=0, le=1)
    
    # Last update
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def get_recommended_lead_time(self, service_level: float = 0.95) -> float:
        """Lead time recomendado para nivel de servicio"""
        return self.distribution.calculate_service_level_lead_time(service_level)
    
    def add_observation(self, history: LeadTimeHistory) -> None:
        """Agregar observación histórica y actualizar distribución"""
        self.historical_data.append(history)
        
        # Actualizar parámetros
        if history.actual_lead_time_days > 0:
            self.distribution.update_with_observation(history.actual_lead_time_days)
        
        # Recalcular on-time %
        if self.historical_data:
            on_time_count = sum(1 for h in self.historical_data if h.on_time)
            self.on_time_percentage = on_time_count / len(self.historical_data)
        
        self.last_updated = datetime.utcnow()
    
    class Config:
        use_enum_values = True
