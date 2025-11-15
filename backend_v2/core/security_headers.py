"""
Backend v2.0 - Security Headers Middleware
Agrega headers HTTP de seguridad recomendados por OWASP
"""
from __future__ import annotations

from flask import Flask


def init_security_headers(app: Flask) -> None:
    """
    Inicializa headers de seguridad HTTP en la aplicación.
    
    Headers implementados:
    - Strict-Transport-Security (HSTS): Fuerza HTTPS
    - X-Content-Type-Options: Previene MIME sniffing
    - X-Frame-Options: Previene clickjacking
    - X-XSS-Protection: Protección XSS (navegadores antiguos)
    - Content-Security-Policy: Restricción de recursos
    - Referrer-Policy: Control de referrer
    - Permissions-Policy: Control de features del navegador
    
    Uso (en app.py, dentro de create_app):
        from core.middleware.security_headers import init_security_headers
        
        app = Flask(__name__)
        init_security_headers(app)
    """
    
    @app.after_request
    def add_security_headers(response):
        """
        Agrega headers de seguridad a TODAS las respuestas.
        """
        
        # HSTS: Fuerza HTTPS durante 1 año (31536000 segundos)
        # Recomendado: 31536000 (1 año), máximo permitido
        # preload: Permite incluir en listas de navegadores (solo para dominios conocidos)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # X-Content-Type-Options: Previene MIME sniffing
        # Obliga al navegador a respetar el Content-Type
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options: Previene clickjacking
        # DENY: No permite ser embedded en ningún frame
        # SAMEORIGIN: Solo permite ser embedded en el mismo origen
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection: Protección XSS (algunos navegadores antiguos)
        # Nota: Content-Security-Policy es más efectivo
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content-Security-Policy: Restricción de recursos que el navegador puede cargar
        # Previene XSS, inyección de código, etc.
        csp = "; ".join([
            "default-src 'self'",                    # Solo scripts/estilos del mismo origen
            "script-src 'self'",                      # Solo scripts locales (sin inline)
            "style-src 'self' 'unsafe-inline'",       # Estilos inline permitidos (componentes React/Vue)
            "img-src 'self' data: https:",            # Imágenes locales, data URLs, y HTTPS
            "font-src 'self' data:",                  # Fuentes locales
            "connect-src 'self'",                     # Conexiones XHR/fetch solo al mismo origen
            "frame-ancestors 'none'",                 # No permitir embedding en frames
            "base-uri 'self'",                        # Solo permite <base> del mismo origen
            "form-action 'self'",                     # Solo formularios al mismo origen
        ])
        response.headers["Content-Security-Policy"] = csp
        
        # Referrer-Policy: Control de qué información se envía en referrer
        # strict-no-referrer: Nunca enviar referrer
        # strict-no-referrer-when-downgrade: No enviar si HTTP→HTTPS
        response.headers["Referrer-Policy"] = "strict-no-referrer"
        
        # Permissions-Policy: Control de features del navegador
        # Previene acceso a micrófono, cámara, ubicación, etc.
        permissions_policy = ", ".join([
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "usb=()",
            "payment=()",
            "vibrate=()",
        ])
        response.headers["Permissions-Policy"] = permissions_policy
        
        return response


