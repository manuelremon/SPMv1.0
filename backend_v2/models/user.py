"""
Backend v2.0 - User model
Modelo SQLAlchemy para tabla usuarios
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class User(Base):
    """
    Modelo de usuario del sistema.
    
    Migrado desde v1.0 tabla 'usuarios' con las siguientes adaptaciones:
    - id_spm → username (PK)
    - contrasena → password_hash
    - mail → email
    - Nuevos campos: is_active, created_at, updated_at
    
    Campos heredados de v1.0:
    - nombre, apellido, rol, sector, posicion
    - telefono, centros, id_ypf (id_red)
    - jefe, gerente1, gerente2
    - estado_registro
    """
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificadores
    username: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        index=True,
        comment="ID SPM del usuario (legacy: id_spm)"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Email del usuario (legacy: mail)"
    )
    
    # Autenticación
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hash bcrypt de la contraseña (legacy: contrasena)"
    )
    
    # Datos personales
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Rol y permisos
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Solicitante",
        comment="Rol del usuario: admin, Planificador, Solicitante, etc. (legacy: rol)"
    )
    
    # Datos organizacionales
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    posicion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    centros: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Centros separados por coma"
    )
    
    # Contacto
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    # IDs legacy de Red YPF
    id_ypf: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID en sistema YPF (legacy: id_red / id_ypf)"
    )
    
    # Jerarquía
    jefe: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gerente1: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gerente2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Usuario activo/inactivo"
    )
    estado_registro: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Pendiente",
        comment="Legacy: Pendiente, Aprobado, Rechazado"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        # Usar __dict__ para evitar lazy loading con objetos detached
        nombre = object.__getattribute__(self, "__dict__").get("nombre", "")
        apellido = object.__getattribute__(self, "__dict__").get("apellido", "")
        return f"{nombre} {apellido}".strip()
    
    @property
    def centros_list(self) -> list[str]:
        """Retorna centros como lista"""
        # Usar __dict__ para evitar lazy loading con objetos detached
        centros = object.__getattribute__(self, "__dict__").get("centros")
        if not centros:
            return []
        return [c.strip() for c in centros.replace(";", ",").split(",") if c.strip()]
    
    def to_dict(self) -> dict:
        """
        Serializa usuario a diccionario.
        Compatible con formato legacy de v1.0
        """
        # Usar __dict__ para evitar lazy loading con objetos detached
        attrs = object.__getattribute__(self, "__dict__")
        
        return {
            "id": attrs.get("id"),
            "username": attrs.get("username"),
            "id_spm": attrs.get("username"),  # legacy compatibility
            "email": attrs.get("email"),
            "mail": attrs.get("email"),  # legacy compatibility
            "nombre": attrs.get("nombre"),
            "apellido": attrs.get("apellido"),
            "full_name": self.full_name,
            "role": attrs.get("role"),
            "rol": attrs.get("role"),  # legacy compatibility
            "sector": attrs.get("sector"),
            "posicion": attrs.get("posicion"),
            "centros": self.centros_list,
            "telefono": attrs.get("telefono"),
            "id_ypf": attrs.get("id_ypf"),
            "id_red": attrs.get("id_ypf"),  # legacy compatibility
            "jefe": attrs.get("jefe"),
            "gerente1": attrs.get("gerente1"),
            "gerente2": attrs.get("gerente2"),
            "is_active": attrs.get("is_active"),
            "estado_registro": attrs.get("estado_registro"),
            "created_at": attrs.get("created_at").isoformat() if attrs.get("created_at") else None,
            "updated_at": attrs.get("updated_at").isoformat() if attrs.get("updated_at") else None,
        }
