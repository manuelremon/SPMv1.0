"""
Backend v2.0 - Schemas package
Pydantic schemas para validación y serialización
"""
from schemas.user_schema import (
    UserLogin,
    UserRegister,
    UserUpdate,
    UserResponse,
    TokenResponse,
    LoginResponse,
    ErrorResponse,
    SuccessResponse,
)
from schemas.solicitud_schema import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialSearchQuery,
    SolicitudItemCreate,
    SolicitudItemResponse,
    SolicitudDraft,
    SolicitudCreate,
    SolicitudUpdate,
    SolicitudResponse,
    SolicitudDetailResponse,
    SolicitudListResponse,
    AprobacionCreate,
    AprobacionResponse,
    SolicitudCreatedResponse,
    MaterialListResponse,
)

__all__ = [
    "UserLogin",
    "UserRegister",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "LoginResponse",
    "ErrorResponse",
    "SuccessResponse",
    "MaterialCreate",
    "MaterialUpdate",
    "MaterialResponse",
    "MaterialSearchQuery",
    "SolicitudItemCreate",
    "SolicitudItemResponse",
    "SolicitudDraft",
    "SolicitudCreate",
    "SolicitudUpdate",
    "SolicitudResponse",
    "SolicitudDetailResponse",
    "SolicitudListResponse",
    "AprobacionCreate",
    "AprobacionResponse",
    "SolicitudCreatedResponse",
    "MaterialListResponse",
]
