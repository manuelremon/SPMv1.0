"""
Backend v2.0 - Models package
SQLAlchemy models para backend_v2
"""
from core.db import Base
from models.user import User

__all__ = ["Base", "User"]
