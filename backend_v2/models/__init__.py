"""
Backend v2.0 - Models package
SQLAlchemy models para backend_v2
"""
from core.db import Base
from models.user import User
from models.solicitud import Material, Solicitud, SolicitudItem, Aprobacion

__all__ = ["Base", "User", "Material", "Solicitud", "SolicitudItem", "Aprobacion"]
