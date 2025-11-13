"""
Backend v2.0 - Middleware package
Decorators de autenticación y control de acceso
"""
from __future__ import annotations

from middleware.auth import (
    require_role,
    require_permission,
    admin_required,
    legacy_endpoint
)

__all__ = [
    "require_role",
    "require_permission",
    "admin_required",
    "legacy_endpoint",
]
