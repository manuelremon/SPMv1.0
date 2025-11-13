"""
Backend v2.0 - User schemas
Schemas Pydantic para validación y serialización de usuarios
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


class UserLogin(BaseModel):
    """
    Schema para login.
    Compatible con v1.0 que acepta: id/username/usuario
    """
    username: str = Field(..., min_length=1, description="Username, email o id_spm")
    password: str = Field(..., min_length=1, description="Contraseña")
    
    @field_validator("username")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        """Normaliza username a lowercase y trim"""
        return v.strip().lower()
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "admin", "password": "admin123"},
                {"username": "planificador@spm.com", "password": "plan123"}
            ]
        }
    )


class UserRegister(BaseModel):
    """
    Schema para registro de nuevo usuario.
    Compatible con RegisterRequest de v1.0
    """
    username: str = Field(..., min_length=1, max_length=100, description="ID SPM del usuario")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="Solicitante", max_length=50, description="Rol del usuario")
    email: Optional[EmailStr] = Field(None, description="Email del usuario")
    
    @field_validator("username")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.strip().lower()
    
    @model_validator(mode="after")
    def extract_email_from_username(self) -> "UserRegister":
        """Si username contiene @ y email no fue provisto, extraer email del username"""
        if not self.email and "@" in self.username:
            self.email = self.username.lower()
        return self


class UserUpdate(BaseModel):
    """Schema para actualización de perfil de usuario"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=5, max_length=30)
    sector: Optional[str] = Field(None, max_length=100)
    posicion: Optional[str] = Field(None, max_length=100)
    centros: Optional[str] = Field(None, max_length=500, description="Centros separados por coma")


class UserResponse(BaseModel):
    """
    Schema para respuesta de usuario.
    Compatible con _public_profile de v1.0
    """
    id: int
    username: str
    id_spm: str  # legacy compatibility
    email: Optional[str] = None
    mail: Optional[str] = None  # legacy compatibility
    nombre: str
    apellido: str
    full_name: str
    role: str
    rol: str  # legacy compatibility
    sector: Optional[str] = None
    posicion: Optional[str] = None
    centros: list[str] = Field(default_factory=list)
    telefono: Optional[str] = None
    id_ypf: Optional[str] = None
    id_red: Optional[str] = None  # legacy compatibility
    jefe: Optional[str] = None
    gerente1: Optional[str] = None
    gerente2: Optional[str] = None
    is_active: bool
    estado_registro: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema para respuesta de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="TTL en segundos")


class LoginResponse(BaseModel):
    """Schema para respuesta de login exitoso"""
    ok: bool = True
    user: UserResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ok": True,
                    "user": {
                        "id": 1,
                        "username": "admin",
                        "id_spm": "admin",
                        "email": "admin@spm.com",
                        "nombre": "Admin",
                        "apellido": "Sistema",
                        "role": "admin",
                        "is_active": True
                    }
                }
            ]
        }
    )


class ErrorResponse(BaseModel):
    """Schema para respuesta de error"""
    ok: bool = False
    error: dict[str, str]
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ok": False,
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Usuario o contraseña incorrectos"
                    }
                }
            ]
        }
    )


class SuccessResponse(BaseModel):
    """Schema genérico para respuestas exitosas"""
    ok: bool = True
    message: Optional[str] = None
