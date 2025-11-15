"""
Schemas Pydantic para Solicitudes y Materiales
Validación de requests/responses para el módulo de solicitudes
"""

from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


# ==================== Material Schemas ====================

class MaterialBase(BaseModel):
    """Schema base para Material"""
    codigo: str = Field(..., min_length=1, max_length=100, description="Código único del material")
    descripcion: str = Field(..., min_length=1, max_length=500, description="Descripción corta")
    descripcion_larga: Optional[str] = Field(None, description="Descripción detallada")
    unidad: Optional[str] = Field(None, max_length=20, description="Unidad de medida")
    precio_usd: float = Field(default=0.0, ge=0, description="Precio en USD")
    centro: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=100)


class MaterialCreate(MaterialBase):
    """Schema para crear un material"""
    pass


class MaterialUpdate(BaseModel):
    """Schema para actualizar un material"""
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    descripcion_larga: Optional[str] = None
    unidad: Optional[str] = Field(None, max_length=20)
    precio_usd: Optional[float] = Field(None, ge=0)
    centro: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=100)


class MaterialResponse(MaterialBase):
    """Schema de respuesta para Material"""
    created_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MaterialSearchQuery(BaseModel):
    """Schema para búsqueda de materiales"""
    q: Optional[str] = Field(None, description="Búsqueda general")
    codigo: Optional[str] = Field(None, description="Filtrar por código")
    descripcion: Optional[str] = Field(None, description="Filtrar por descripción")
    centro: Optional[str] = Field(None, description="Filtrar por centro")
    sector: Optional[str] = Field(None, description="Filtrar por sector")
    limit: int = Field(default=100, ge=1, le=10000, description="Límite de resultados")


# ==================== Solicitud Item Schemas ====================

class SolicitudItemBase(BaseModel):
    """Schema base para item de solicitud"""
    material_codigo: str = Field(..., min_length=1, max_length=100, description="Código del material")
    cantidad: float = Field(..., gt=0, description="Cantidad solicitada")
    precio_unitario: Optional[float] = Field(None, ge=0, description="Precio unitario")
    comentario: Optional[str] = Field(None, description="Comentario opcional")


class SolicitudItemCreate(SolicitudItemBase):
    """Schema para crear item de solicitud"""
    
    @field_validator("cantidad")
    @classmethod
    def cantidad_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class SolicitudItemResponse(SolicitudItemBase):
    """Schema de respuesta para item de solicitud"""
    id_item: int
    solicitud_id: int
    subtotal: float
    created_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Solicitud Schemas ====================

class SolicitudBase(BaseModel):
    """Schema base para Solicitud"""
    centro: str = Field(..., min_length=1, max_length=100, description="Centro solicitante")
    sector: Optional[str] = Field(None, max_length=100, description="Sector solicitante")
    justificacion: str = Field(..., min_length=10, description="Justificación de la solicitud")
    centro_costos: Optional[str] = Field(None, max_length=100, description="Centro de costos")
    almacen_virtual: Optional[str] = Field(None, max_length=100, description="Almacén virtual")
    criticidad: Literal["Normal", "Alta"] = Field(default="Normal", description="Criticidad de la solicitud")
    fecha_necesidad: Optional[date] = Field(None, description="Fecha en que se necesitan los materiales")


class SolicitudDraft(SolicitudBase):
    """Schema para borrador de solicitud (sin items obligatorios)"""
    pass


class SolicitudCreate(SolicitudBase):
    """Schema para crear solicitud completa"""
    items: List[SolicitudItemCreate] = Field(..., min_length=1, description="Items de la solicitud")
    
    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: List[SolicitudItemCreate]) -> List[SolicitudItemCreate]:
        if not v or len(v) == 0:
            raise ValueError("La solicitud debe tener al menos un item")
        return v
    
    @field_validator("justificacion")
    @classmethod
    def justificacion_min_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("La justificación debe tener al menos 10 caracteres")
        return v


class SolicitudUpdate(BaseModel):
    """Schema para actualizar solicitud"""
    centro: Optional[str] = Field(None, min_length=1, max_length=100)
    sector: Optional[str] = Field(None, min_length=1, max_length=100)
    justificacion: Optional[str] = Field(None, min_length=10)
    centro_costos: Optional[str] = Field(None, max_length=100)
    almacen_virtual: Optional[str] = Field(None, max_length=100)
    criticidad: Optional[Literal["Normal", "Alta"]] = None
    fecha_necesidad: Optional[date] = None
    items: Optional[List[SolicitudItemCreate]] = None


class SolicitudResponse(SolicitudBase):
    """Schema de respuesta para Solicitud (sin items)"""
    id: int
    id_usuario: str
    status: str
    aprobador_id: Optional[str] = None
    planner_id: Optional[str] = None
    total_monto: float
    total_items: int
    total_cantidad: float
    notificado_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SolicitudDetailResponse(SolicitudResponse):
    """Schema de respuesta detallada con items"""
    items: List[SolicitudItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class SolicitudListResponse(BaseModel):
    """Schema de respuesta para lista de solicitudes"""
    ok: bool = True
    solicitudes: List[SolicitudResponse]
    total: int
    page: int = 1
    per_page: int = 10


# ==================== Aprobacion Schemas ====================

class AprobacionCreate(BaseModel):
    """Schema para crear aprobación/rechazo"""
    decision: Literal["aprobada", "rechazada"] = Field(..., description="Decisión de aprobación")
    comentario: Optional[str] = Field(None, description="Comentario opcional")


class AprobacionResponse(BaseModel):
    """Schema de respuesta para Aprobacion"""
    id: int
    solicitud_id: int
    aprobador_id: str
    decision: str
    comentario: Optional[str] = None
    created_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Response Wrappers ====================

class ErrorResponse(BaseModel):
    """Schema de respuesta de error"""
    ok: bool = False
    error: dict = Field(..., description="Detalles del error")


class SuccessResponse(BaseModel):
    """Schema de respuesta exitosa genérica"""
    ok: bool = True
    message: str


class SolicitudCreatedResponse(BaseModel):
    """Schema de respuesta al crear solicitud"""
    ok: bool = True
    solicitud: SolicitudDetailResponse


class MaterialListResponse(BaseModel):
    """Schema de respuesta para lista de materiales"""
    ok: bool = True
    materiales: List[MaterialResponse]
    total: int
