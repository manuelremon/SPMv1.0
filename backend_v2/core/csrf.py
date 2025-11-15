"""
Backend v2.0 - CSRF Middleware
Protección contra Cross-Site Request Forgery (CSRF/XSRF)
Token-based protection con validación de origen
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from functools import wraps
from typing import Callable

from flask import request, jsonify, session, g

from core.config import settings


class CSRFProtection:
    """
    Gestor de tokens CSRF con firma HMAC-SHA256.
    
    Implementa doble validación:
    1. Token en sesión vs token en request (mismo cliente)
    2. Firma HMAC para prevenir tampering
    """
    
    @staticmethod
    def generate_token() -> str:
        """
        Genera un token CSRF aleatorio de 32 bytes.
        
        Returns:
            Token CSRF en formato hexadecimal
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def sign_token(token: str, secret: str) -> str:
        """
        Firma un token CSRF con HMAC-SHA256.
        
        Args:
            token: Token a firmar
            secret: Llave secreta (usualmente SECRET_KEY)
        
        Returns:
            Token firmado en formato "token:signature"
        """
        signature = hmac.new(
            secret.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token}:{signature}"
    
    @staticmethod
    def verify_token(signed_token: str, secret: str) -> bool:
        """
        Verifica que un token firmado sea válido.
        
        Usa comparación timing-safe para prevenir timing attacks.
        
        Args:
            signed_token: Token en formato "token:signature"
            secret: Llave secreta (usualmente SECRET_KEY)
        
        Returns:
            True si el token es válido y no fue alterado
        """
        try:
            token, signature = signed_token.split(":", 1)
            expected_signature = hmac.new(
                secret.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Comparación timing-safe contra timing attacks
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, AttributeError, TypeError):
            return False


def csrf_exempt(f: Callable) -> Callable:
    """
    Marca un endpoint como exento de validación CSRF.
    
    Uso (ej: para websockets, webhooks, APIs públicas):
        @app.post('/api/webhook/external')
        @csrf_exempt
        def external_webhook():
            ...
    """
    f._csrf_exempt = True
    return f


def require_csrf(f: Callable) -> Callable:
    """
    Decorator para validar token CSRF en endpoints que modifican datos.
    
    Busca token en:
    1. Header X-CSRF-Token (recomendado para AJAX)
    2. Form data csrf_token (recomendado para formularios HTML)
    3. Query parameter csrf_token (respaldo)
    
    Uso:
        @app.post('/api/users')
        @require_csrf
        def create_user():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Leer token de múltiples fuentes
        token = (
            request.headers.get("X-CSRF-Token")
            or request.form.get("csrf_token")
            or request.args.get("csrf_token")
        )
        
        if not token:
            return jsonify({
                "ok": False,
                "error": {
                    "code": "csrf_missing",
                    "message": "CSRF token missing",
                    "required_header": "X-CSRF-Token"
                }
            }), 403
        
        # Verificar firma del token
        if not CSRFProtection.verify_token(token, settings.SECRET_KEY):
            return jsonify({
                "ok": False,
                "error": {
                    "code": "csrf_invalid",
                    "message": "CSRF token invalid or expired"
                }
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def init_csrf_protection(app):
    """
    Inicializa protección CSRF en la aplicación Flask.
    
    - Genera token CSRF para cada sesión
    - Aplica validación automática a POST/PUT/PATCH/DELETE
    - Expone endpoint GET /api/csrf para obtener token
    
    Args:
        app: Instancia de Flask
    
    Uso (en app.py, dentro de create_app):
        from core.middleware.csrf import init_csrf_protection
        
        app = Flask(__name__)
        init_csrf_protection(app)
    """
    
    @app.before_request
    def csrf_before_request():
        """
        Genera y valida tokens CSRF antes de cada request.
        """
        # Generar token para sesión (se guarda en g)
        if "csrf_token" not in session:
            session["csrf_token"] = CSRFProtection.generate_token()
        
        g.csrf_token = CSRFProtection.sign_token(
            session["csrf_token"],
            settings.SECRET_KEY
        )
        
        # Validar CSRF en métodos que modifican datos
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Saltar validación si está exento
            if getattr(request.endpoint and app.view_functions.get(request.endpoint), "_csrf_exempt", False):
                return
            
            # Validar token
            token = (
                request.headers.get("X-CSRF-Token")
                or request.form.get("csrf_token")
                or request.args.get("csrf_token")
            )
            
            if not token:
                return jsonify({
                    "ok": False,
                    "error": {
                        "code": "csrf_missing",
                        "message": "CSRF token missing"
                    }
                }), 403
            
            if not CSRFProtection.verify_token(token, settings.SECRET_KEY):
                return jsonify({
                    "ok": False,
                    "error": {
                        "code": "csrf_invalid",
                        "message": "CSRF token invalid"
                    }
                }), 403
    
    @app.get("/api/csrf")
    def get_csrf_token():
        """
        Endpoint para obtener token CSRF.
        
        Llamar a este endpoint desde el frontend para obtener un token
        que se debe incluir en todos los requests que modifican datos.
        
        Response:
            {
                "ok": true,
                "csrf_token": "abc123...:signature..."
            }
        """
        return jsonify({
            "ok": True,
            "csrf_token": g.get("csrf_token", "")
        })


# Singleton global
csrf = CSRFProtection()

