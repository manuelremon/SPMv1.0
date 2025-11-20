"""
Protección CSRF - Token generation y validación
"""
import hashlib
import hmac
import secrets
from flask import request, jsonify, g


class CSRFProtection:
    """Maneja protección CSRF"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa con la aplicación Flask"""
        self.app = app
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    @staticmethod
    def generate_token() -> str:
        """Genera un token CSRF aleatorio"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sign_token(token: str, secret: str) -> str:
        """Firma un token CSRF"""
        signature = hmac.new(
            secret.encode(),
            token.encode(),
            hashlib.sha256
        ).digest()
        return token + "." + signature.hex()
    
    @staticmethod
    def verify_token(signed_token: str, secret: str) -> bool:
        """Verifica un token CSRF firmado"""
        try:
            token, signature = signed_token.rsplit(".", 1)
            expected_signature = hmac.new(
                secret.encode(),
                token.encode(),
                hashlib.sha256
            ).digest().hex()
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, AttributeError):
            return False
    
    def before_request(self):
        """Middleware antes de request"""
        # Generar token si no existe
        token = self.generate_token()
        g.csrf_token = token
    
    def after_request(self, response):
        """Middleware después de response"""
        # Agregar token a response
        if hasattr(g, 'csrf_token'):
            response.headers['X-CSRF-Token'] = g.csrf_token
        return response


def init_csrf_protection(app):
    """Factory para inicializar CSRF protection"""
    csrf = CSRFProtection(app)
    return csrf
