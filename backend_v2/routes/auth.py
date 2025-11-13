"""
Backend v2.0 - Authentication routes
POST /login, GET /me, decorator @auth_required
"""
from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import Blueprint, request, jsonify, make_response

from core.config import settings
from core.jwt_manager import jwt_manager
from core.security import require_rate_limit
from services.auth_service import AuthService

bp = Blueprint("auth", __name__, url_prefix="/auth")


def auth_required(f: Callable) -> Callable:
    """
    Decorator para endpoints que requieren autenticación.
    
    Lee token JWT desde cookie y valida.
    Inyecta user_payload en kwargs.
    
    Uso:
        @app.get('/api/protected')
        @auth_required
        def protected_route(user_payload):
            return {"user_id": user_payload["sub"]}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Leer token desde cookie
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
        
        # Inyectar payload en kwargs
        kwargs["user_payload"] = payload
        return f(*args, **kwargs)
    
    return decorated_function


@bp.post("/login")
@require_rate_limit
def login():
    """
    Endpoint de login.
    
    Request:
        {
            "username": "admin@spm.com",
            "password": "admin123"
        }
    
    Response (éxito):
        {
            "ok": true,
            "user": {
                "id": "user123",
                "email": "admin@spm.com",
                "role": "admin"
            }
        }
        + Cookie: spm_token=<JWT>
    
    Response (error):
        {
            "ok": false,
            "error": {
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "ok": False,
            "error": {
                "code": "bad_request",
                "message": "Request body required"
            }
        }), 400
    
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({
            "ok": False,
            "error": {
                "code": "missing_fields",
                "message": "Username and password required"
            }
        }), 400
    
    # Autenticar usuario (stub por ahora)
    auth_service = AuthService()
    user = auth_service.authenticate_user(username, password)
    
    if not user:
        return jsonify({
            "ok": False,
            "error": {
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            }
        }), 401
    
    # Crear token JWT
    token = jwt_manager.create_access_token(
        payload={
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    )
    
    # Crear respuesta con cookie
    response = make_response(jsonify({
        "ok": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }))
    
    jwt_manager.set_token_cookie(response, token)
    
    return response, 200


@bp.get("/me")
@auth_required
def get_current_user(user_payload: dict):
    """
    Obtiene información del usuario autenticado actual.
    
    Response:
        {
            "ok": true,
            "user": {
                "id": "user123",
                "email": "admin@spm.com",
                "role": "admin"
            }
        }
    """
    return jsonify({
        "ok": True,
        "user": {
            "id": user_payload["sub"],
            "email": user_payload.get("email"),
            "role": user_payload.get("role")
        }
    }), 200


@bp.post("/logout")
@auth_required
def logout(user_payload: dict):
    """
    Cierra sesión eliminando cookie de token.
    
    Response:
        {
            "ok": true,
            "message": "Logged out successfully"
        }
    """
    response = make_response(jsonify({
        "ok": True,
        "message": "Logged out successfully"
    }))
    
    jwt_manager.clear_token_cookie(response)
    
    return response, 200
