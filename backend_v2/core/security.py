"""
Backend v2.0 - Security helpers
CSRF protection (deprecated - use middleware instead)
Rate limiting (moved to core.rate_limiter)
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify, g

from core.config import settings
from core.rate_limiter import require_rate_limit as _require_rate_limit


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
    DEPRECATED: Use require_rate_limit decorator desde core.rate_limiter en su lugar.
    
    Esta clase se mantiene por compatibilidad pero no se usa.
    Fue reemplazada por un módulo dedicado con soporte para Redis.
    """
    
    def __init__(self):
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.limit = settings.RATE_LIMIT_PER_MINUTE
    
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
    DEPRECATED: Usar require_rate_limit desde core.rate_limiter en su lugar.
    
    Este decorator se mantiene solo para compatibilidad hacia atrás.
    """
    return _require_rate_limit(f)


# Singletons globales
csrf = CSRFProtection()
rate_limiter = RateLimiter()


def get_current_user_id() -> Optional[str]:
    """
    Obtiene el username del usuario autenticado desde flask.g
    
    Requiere que el endpoint tenga @require_role decorator aplicado,
    que es quien popula g.user.
    
    Returns:
        Username del usuario autenticado o None si no está autenticado
    
    Uso:
        @require_role("Solicitante")
        def create_solicitud():
            user_id = get_current_user_id()
            # user_id = "jperez"
    """
    user = getattr(g, "user", None)
    if not user:
        return None
    return user.get("username")
