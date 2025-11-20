"""
Authentication routes
"""
from flask import Blueprint, jsonify, request
import bcrypt
from datetime import datetime, timedelta
import jwt
from core.config import settings

bp = Blueprint('auth', __name__)

# Usuario de prueba (en producción usa BD)
DEMO_USER = {
    "id": "1",
    "username": "admin",
    "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
    "email": "admin@spm.local",
    "nombre": "Administrador",
    "rol": "admin"
}


def generate_tokens(user_id: str) -> dict:
    """Genera access y refresh tokens"""
    now = datetime.utcnow()
    
    # Access token (1 hora)
    access_payload = {
        "user_id": user_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(hours=1)
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    # Refresh token (7 días)
    refresh_payload = {
        "user_id": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=7)
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            "ok": False,
            "error": {
                "code": "validation_error",
                "message": "Username and password are required"
            }
        }), 400
    
    # Verificar credenciales (solo demo user)
    if username != DEMO_USER['username']:
        return jsonify({
            "ok": False,
            "error": {
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            }
        }), 401
    
    if not bcrypt.checkpw(password.encode(), DEMO_USER['password_hash'].encode()):
        return jsonify({
            "ok": False,
            "error": {
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            }
        }), 401
    
    # Generar tokens
    tokens = generate_tokens(DEMO_USER['id'])
    
    response = jsonify({
        "ok": True,
        "message": "Login successful",
        "user": {
            "id": DEMO_USER['id'],
            "username": DEMO_USER['username'],
            "email": DEMO_USER['email'],
            "nombre": DEMO_USER['nombre'],
            "rol": DEMO_USER['rol']
        },
        "access_token": tokens['access_token'],
        "refresh_token": tokens['refresh_token']
    })
    
    # Cookies HttpOnly
    response.set_cookie(
        'spm_token',
        tokens['access_token'],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=3600
    )
    response.set_cookie(
        'spm_token_refresh',
        tokens['refresh_token'],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=604800
    )
    
    return response, 200


@bp.route('/me', methods=['GET'])
def get_me():
    """Obtener usuario actual"""
    # En producción, validar JWT desde cookie
    return jsonify({
        "ok": True,
        "user": {
            "id": DEMO_USER['id'],
            "username": DEMO_USER['username'],
            "email": DEMO_USER['email'],
            "nombre": DEMO_USER['nombre'],
            "rol": DEMO_USER['rol']
        }
    }), 200


@bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    tokens = generate_tokens(DEMO_USER['id'])
    
    response = jsonify({
        "ok": True,
        "message": "Token refreshed",
        "access_token": tokens['access_token']
    })
    
    response.set_cookie(
        'spm_token',
        tokens['access_token'],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=3600
    )
    
    return response, 200


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout"""
    response = jsonify({
        "ok": True,
        "message": "Logged out successfully"
    })
    
    response.set_cookie('spm_token', '', max_age=0)
    response.set_cookie('spm_token_refresh', '', max_age=0)
    
    return response, 200


@bp.route('/register', methods=['POST'])
def register():
    """Registro de usuario (básico para demo)"""
    return jsonify({
        "ok": False,
        "error": {
            "code": "not_implemented",
            "message": "Registration endpoint not available in demo"
        }
    }), 501
