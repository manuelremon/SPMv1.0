"""
Security Headers - OWASP compliant
"""
from flask import Flask


def init_security_headers(app: Flask):
    """Inicializa headers de seguridad OWASP"""
    
    @app.after_request
    def set_security_headers(response):
        # HSTS - Force HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Clickjacking protection
        response.headers['X-Frame-Options'] = 'DENY'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-no-referrer'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        return response
    
    return app
