from ..core.base import Base

# expose Base for models
from .user import Base as UserBase

__all__ = ["UserBase"]
