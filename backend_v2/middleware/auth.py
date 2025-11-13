"""
Backend v2.0 - Middleware de autenticación y roles
Decorators para control de acceso basado en roles
"""
from __future__ import annotations

from functools import wraps
from typing import Callable, List, Optional

from flask import request, jsonify, g

from core.jwt_manager import jwt_manager


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator que requiere uno de los roles especificados.
    
    Compatible con v1.0:
    - Lee token desde cookie
    - Verifica roles en payload['roles']
    - Retorna 403 si rol no permitido
    
    Uso:
        @app.get('/admin/users')
        @require_role('Administrador', 'Gerente')
        def list_users():
            return {"users": [...]}
    
    Args:
        *allowed_roles: Roles permitidos (uno o más)
    
    Returns:
        Decorator function
    
    Ejemplos de roles v1.0:
        - Administrador
        - Gerente
        - Planificador
        - Solicitante
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Leer token desde cookie
            from core.config import settings
            token = request.cookies.get(settings.JWT_COOKIE_NAME)
            
            if not token:
                return jsonify({
                    "ok": False,
                    "error": {
                        "code": "unauthorized",
                        "message": "Authentication required"
                    }
                }), 401
            
            # Verificar token
            payload = jwt_manager.verify_token(token)
            
            if not payload:
                return jsonify({
                    "ok": False,
                    "error": {
                        "code": "invalid_token",
                        "message": "Invalid or expired token"
                    }
                }), 401
            
            # Obtener roles del payload
            # v1.0 usa: roles=[] y rol=str
            user_roles = payload.get("roles", [])
            user_role = payload.get("rol", payload.get("role"))
            
            # Agregar rol principal si no está en lista
            if user_role and user_role not in user_roles:
                user_roles.append(user_role)
            
            # Verificar si tiene uno de los roles permitidos
            if allowed_roles and not any(role in user_roles for role in allowed_roles):
                return jsonify({
                    "ok": False,
                    "error": {
                        "code": "forbidden",
                        "message": f"Requires one of: {', '.join(allowed_roles)}",
                        "need_any_of": list(allowed_roles)
                    }
                }), 403
            
            # Guardar user en flask.g para acceso en handler
            g.user = {
                "id": payload.get("uid"),
                "username": payload.get("id_spm"),
                "role": user_role,
                "roles": user_roles,
                "email": payload.get("email"),
            }
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def require_permission(permission: str) -> Callable:
    """
    Decorator que verifica permisos granulares.
    
    TODO FASE 4.2: Implementar tabla de permisos
    Por ahora mapea permisos a roles.
    
    Uso:
        @app.delete('/projects/<int:id>')
        @require_permission('project:delete')
        def delete_project(id: int):
            ...
    
    Args:
        permission: Nombre del permiso (ej: 'project:delete')
    
    Returns:
        Decorator function
    """
    # Mapeo temporal de permisos a roles
    PERMISSION_ROLE_MAP = {
        "project:create": ["Administrador", "Gerente", "Planificador"],
        "project:read": ["Administrador", "Gerente", "Planificador", "Solicitante"],
        "project:update": ["Administrador", "Gerente", "Planificador"],
        "project:delete": ["Administrador", "Gerente"],
        "user:create": ["Administrador"],
        "user:read": ["Administrador", "Gerente"],
        "user:update": ["Administrador"],
        "user:delete": ["Administrador"],
        "material:create": ["Administrador", "Gerente", "Planificador"],
        "material:read": ["Administrador", "Gerente", "Planificador", "Solicitante"],
        "material:update": ["Administrador", "Gerente", "Planificador"],
        "material:delete": ["Administrador", "Gerente"],
    }
    
    allowed_roles = PERMISSION_ROLE_MAP.get(permission, ["Administrador"])
    
    return require_role(*allowed_roles)


def admin_required(f: Callable) -> Callable:
    """
    Decorator que requiere rol de Administrador.
    
    Shortcut para @require_role('Administrador')
    """
    return require_role("Administrador")(f)


def legacy_endpoint(f: Callable) -> Callable:
    """
    Decorator para marcar endpoints legacy de v1.0.
    
    Agrega headers:
    - X-Legacy-Endpoint: true
    - X-Legacy-Deprecation: Migrate to v2.0 API
    
    Uso:
        @app.get('/api/v1/old-endpoint')
        @legacy_endpoint
        def old_endpoint():
            return {"data": "..."}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        from flask import make_response
        
        logger = logging.getLogger(__name__)
        logger.warning(
            "Legacy endpoint accessed: %s %s - Consider migrating to v2.0",
            request.method,
            request.path
        )
        
        response = f(*args, **kwargs)
        
        # Si la respuesta es una tupla (body, status), crear respuesta
        if isinstance(response, tuple):
            body, status = response[:2]
            resp = make_response(body, status)
        else:
            resp = make_response(response)
        
        # Agregar headers legacy
        resp.headers["X-Legacy-Endpoint"] = "true"
        resp.headers["X-Legacy-Deprecation"] = "Migrate to v2.0 API"
        
        return resp
    
    return decorated_function
