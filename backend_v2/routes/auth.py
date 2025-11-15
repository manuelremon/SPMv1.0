"""
Backend v2.0 - Authentication routes
POST /login, POST /register, GET /me, POST /logout, decorator @auth_required
"""
from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import Blueprint, request, jsonify, make_response
from pydantic import ValidationError

from core.config import settings
from core.jwt_manager import jwt_manager
from core.rate_limiter import require_rate_limit
from schemas.user_schema import (
    UserLogin,
    UserRegister,
    UserResponse,
    LoginResponse,
    ErrorResponse,
    SuccessResponse
)
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
    Endpoint de login con validación Pydantic.
    
    Request:
        {
            "username": "admin@spm.com",
            "password": "admin123"
        }
    
    Response (éxito):
        {
            "ok": true,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@spm.com",
                "role": "Administrador",
                "nombre": "Admin",
                "apellido": "Sistema",
                ...
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
        error = ErrorResponse(
            ok=False,
            error={"code": "bad_request", "message": "Request body required"}
        )
        return jsonify(error.model_dump()), 400
    
    try:
        # Validar con Pydantic
        login_data = UserLogin(**data)
    except ValidationError as e:
        error = ErrorResponse(
            ok=False,
            error={
                "code": "validation_error",
                "message": str(e.errors()[0]["msg"]) if e.errors() else "Validation failed"
            }
        )
        return jsonify(error.model_dump()), 400
    
    # Autenticar usuario con database
    user = AuthService.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        error = ErrorResponse(
            ok=False,
            error={
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            }
        )
        return jsonify(error.model_dump()), 401
    
    # Crear token JWT con claims compatibles v1.0
    token = jwt_manager.create_access_token(
        payload={
            "sub": str(user.id),
            "uid": user.id,
            "id_spm": user.username,
            "rol": user.role,
            "roles": [user.role],
            "email": user.email,
        }
    )
    
    # Crear refresh token
    refresh_token = jwt_manager.create_refresh_token(
        payload={
            "sub": str(user.id),
        }
    )
    
    # Crear respuesta con schema usando to_dict() para compatibilidad con Pydantic
    user_response = UserResponse.model_validate(user.to_dict())
    login_response = LoginResponse(ok=True, user=user_response)
    
    response = make_response(jsonify(login_response.model_dump()))
    jwt_manager.set_token_cookie(response, token, token_type="access")
    jwt_manager.set_token_cookie(response, refresh_token, token_type="refresh")
    
    return response, 200


@bp.post("/register")
@require_rate_limit
def register():
    """
    Endpoint de registro de nuevos usuarios.
    
    Request:
        {
            "username": "usuario123",
            "password": "securepass",
            "nombre": "Juan",
            "apellido": "Pérez",
            "role": "Solicitante",
            "email": "juan.perez@spm.com",
            "sector": "Operaciones"
        }
    
    Response (éxito):
        {
            "ok": true,
            "user": {...}
        }
    
    Response (error):
        {
            "ok": false,
            "error": {
                "code": "duplicate_user",
                "message": "Usuario 'usuario123' ya existe"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        error = ErrorResponse(
            ok=False,
            error={"code": "bad_request", "message": "Request body required"}
        )
        return jsonify(error.model_dump()), 400
    
    try:
        # Validar con Pydantic
        register_data = UserRegister(**data)
    except ValidationError as e:
        error = ErrorResponse(
            ok=False,
            error={
                "code": "validation_error",
                "message": str(e.errors()[0]["msg"]) if e.errors() else "Validation failed"
            }
        )
        return jsonify(error.model_dump()), 400
    
    try:
        # Crear usuario
        user = AuthService.create_user(
            username=register_data.username,
            password=register_data.password,
            nombre=register_data.nombre,
            apellido=register_data.apellido,
            role=register_data.role,
            email=register_data.email,
        )
    except ValueError as e:
        error = ErrorResponse(
            ok=False,
            error={"code": "duplicate_user", "message": str(e)}
        )
        return jsonify(error.model_dump()), 409
    except Exception as e:
        error = ErrorResponse(
            ok=False,
            error={"code": "server_error", "message": "Failed to create user"}
        )
        return jsonify(error.model_dump()), 500
    
    # Retornar usuario creado usando to_dict() para compatibilidad con Pydantic
    user_response = UserResponse.model_validate(user.to_dict())
    login_response = LoginResponse(ok=True, user=user_response)
    
    return jsonify(login_response.model_dump()), 201


@bp.get("/me")
@auth_required
def get_current_user(user_payload: dict):
    """
    Obtiene información completa del usuario autenticado.
    
    Response:
        {
            "ok": true,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@spm.com",
                "role": "Administrador",
                "nombre": "Admin",
                "apellido": "Sistema",
                "full_name": "Admin Sistema",
                "centros_list": ["Centro1", "Centro2"],
                ...
            }
        }
    """
    # Obtener user_id del token
    user_id = user_payload.get("uid") or int(user_payload.get("sub", 0))
    
    # Consultar usuario desde database
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        error = ErrorResponse(
            ok=False,
            error={"code": "user_not_found", "message": "User not found"}
        )
        return jsonify(error.model_dump()), 404
    
    # Retornar con schema usando to_dict() para compatibilidad con Pydantic
    user_response = UserResponse.model_validate(user.to_dict())
    login_response = LoginResponse(ok=True, user=user_response)
    
    return jsonify(login_response.model_dump()), 200


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
    success = SuccessResponse(ok=True, message="Logged out successfully")
    response = make_response(jsonify(success.model_dump()))
    
    jwt_manager.clear_token_cookie(response)
    
    return response, 200


@bp.post("/refresh")
def refresh_token():
    """
    Refresca el access token usando un refresh token válido.
    
    Endpoint para mantener sesiones activas sin re-autenticación.
    El refresh token se obtiene automáticamente en login y se almacena en cookie.
    
    Response (éxito):
        {
            "ok": true,
            "user": {...}
        }
        + Cookie: spm_token=<nuevo JWT>
    
    Response (error):
        {
            "ok": false,
            "error": {
                "code": "invalid_token",
                "message": "Refresh token invalid or expired"
            }
        }
    """
    # Leer refresh token desde cookie
    refresh_token_value = request.cookies.get(f"{settings.JWT_COOKIE_NAME}_refresh")
    
    if not refresh_token_value:
        error = ErrorResponse(
            ok=False,
            error={
                "code": "no_refresh_token",
                "message": "Refresh token missing"
            }
        )
        return jsonify(error.model_dump()), 401
    
    # Verificar refresh token (asegurar que es de tipo "refresh")
    payload = jwt_manager.verify_token(
        refresh_token_value,
        token_type=jwt_manager.TOKEN_TYPE_REFRESH
    )
    
    if not payload:
        error = ErrorResponse(
            ok=False,
            error={
                "code": "invalid_token",
                "message": "Refresh token invalid or expired"
            }
        )
        return jsonify(error.model_dump()), 401
    
    # Obtener user_id del payload
    user_id = int(payload.get("sub", 0))
    
    # Consultar usuario desde database
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        error = ErrorResponse(
            ok=False,
            error={"code": "user_not_found", "message": "User not found"}
        )
        return jsonify(error.model_dump()), 404
    
    # Crear nuevo access token
    new_access_token = jwt_manager.create_access_token(
        payload={
            "sub": str(user.id),
            "uid": user.id,
            "id_spm": user.username,
            "rol": user.role,
            "roles": [user.role],
            "email": user.email,
        }
    )
    
    # Crear respuesta con usuario actualizado
    user_response = UserResponse.model_validate(user.to_dict())
    login_response = LoginResponse(ok=True, user=user_response)
    
    response = make_response(jsonify(login_response.model_dump()))
    jwt_manager.set_token_cookie(response, new_access_token, token_type="access")
    
    return response, 200

