"""
Backend v2.0 - Security helpers
CSRF protection y rate limiting
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from functools import wraps
from typing import Callable

from flask import request, jsonify

from core.config import settings


class CSRFProtection:
    """Helper para protección CSRF con tokens firmados"""
    
    @staticmethod
    def generate_token() -> str:
        """
        Genera un token CSRF aleatorio.
        
        Returns:
            Token CSRF de 32 caracteres hexadecimales
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def sign_token(token: str) -> str:
        """
        Firma un token CSRF con SECRET_KEY.
        
        Args:
            token: Token a firmar
        
        Returns:
            Token firmado (token:signature)
        """
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token}:{signature}"
    
    @staticmethod
    def verify_token(signed_token: str) -> bool:
        """
        Verifica que un token firmado sea válido.
        
        Args:
            signed_token: Token en formato token:signature
        
        Returns:
            True si el token es válido, False otherwise
        """
        try:
            token, signature = signed_token.split(":", 1)
            expected_signature = hmac.new(
                settings.SECRET_KEY.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Comparación segura contra timing attacks
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, AttributeError):
            return False


class RateLimiter:
    """
    Placeholder para rate limiting.
    
    TODO FASE 4: Implementar con Redis o en-memory cache
    Por ahora solo valida si está habilitado.
    """
    
    def __init__(self):
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        # TODO: Agregar storage (Redis client o LRU cache)
    
    def check_limit(self, identifier: str) -> bool:
        """
        Verifica si un identificador (IP, user_id) ha excedido el límite.
        
        Args:
            identifier: IP address o user ID
        
        Returns:
            True si está dentro del límite, False si excedió
        """
        if not self.enabled:
            return True
        
        # TODO FASE 4: Implementar conteo real
        # Por ahora siempre permite
        return True
    
    def record_request(self, identifier: str) -> None:
        """
        Registra una request para el identificador.
        
        Args:
            identifier: IP address o user ID
        """
        if not self.enabled:
            return
        
        # TODO FASE 4: Incrementar contador en Redis/cache
        pass


def require_csrf(f: Callable) -> Callable:
    """
    Decorator para endpoints que requieren validación CSRF.
    
    Busca token en header X-CSRF-Token o form data.
    
    Uso:
        @app.post('/api/users')
        @require_csrf
        def create_user():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Leer token del header o form
        token = request.headers.get("X-CSRF-Token")
        if not token:
            token = request.form.get("csrf_token")
        
        if not token:
            return jsonify({
                "ok": False,
                "error": {
                    "code": "csrf_missing",
                    "message": "CSRF token missing"
                }
            }), 403
        
        if not CSRFProtection.verify_token(token):
            return jsonify({
                "ok": False,
                "error": {
                    "code": "csrf_invalid",
                    "message": "CSRF token invalid"
                }
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_rate_limit(f: Callable) -> Callable:
    """
    Decorator para endpoints con rate limiting.
    
    Usa IP del cliente como identificador.
    
    Uso:
        @app.post('/api/auth/login')
        @require_rate_limit
        def login():
            ...
    """
    limiter = RateLimiter()
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener IP del cliente
        identifier = request.remote_addr or "unknown"
        
        if not limiter.check_limit(identifier):
            return jsonify({
                "ok": False,
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Max {settings.RATE_LIMIT_PER_MINUTE} requests per minute."
                }
            }), 429
        
        limiter.record_request(identifier)
        return f(*args, **kwargs)
    
    return decorated_function


# Singletons globales
csrf = CSRFProtection()
rate_limiter = RateLimiter()
