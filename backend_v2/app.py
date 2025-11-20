"""
Backend v2.0 - Flask Application Factory
API REST limpia con CORS, blueprints, error handlers
"""
from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from core.config import settings
from core.db import init_db, db
from core.csrf import init_csrf_protection
from core.security_headers import init_security_headers
from routes import health, auth, solicitudes, planner


def create_app(config_override: dict | None = None) -> Flask:
    """
    Factory para crear aplicación Flask.
    
    Args:
        config_override: Configuración custom para tests (opcional)
    
    Returns:
        Instancia de Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración
    app.config.from_mapping(
        SECRET_KEY=settings.SECRET_KEY,
        DEBUG=settings.DEBUG,
        ENV=settings.ENV,
        SESSION_COOKIE_SECURE=settings.JWT_COOKIE_SECURE,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=settings.JWT_COOKIE_SAMESITE,
        SQLALCHEMY_DATABASE_URI=settings.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    if config_override:
        app.config.update(config_override)
    
    # Logging
    _configure_logging(app)
    
    # Inicializar DB
    db.init_app(app)
    
    # Protección CSRF
    init_csrf_protection(app)
    
    # Security headers
    init_security_headers(app)
    
    # CORS
    CORS(
        app,
        origins=settings.CORS_ORIGINS,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    
    # Inicializar DB (solo en dev/test)
    if settings.ENV in ["development", "test"]:
        with app.app_context():
            init_db()
    
    # Registrar blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(solicitudes.bp)
    app.register_blueprint(planner.planner_bp, url_prefix="/api/planner")
    
    # Error handlers
    _register_error_handlers(app)
    
    # Logging de inicio
    app.logger.info(f"SPM Backend v2.0 initialized (ENV={settings.ENV})")
    
    return app


def _configure_logging(app: Flask) -> None:
    """Configura logging según entorno"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Formato de logs
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    
    # Handler de archivo (solo si no es test)
    if settings.ENV != "test":
        log_file = Path(settings.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    app.logger.addHandler(console_handler)
    
    app.logger.setLevel(log_level)


def _register_error_handlers(app: Flask) -> None:
    """Registra handlers para errores HTTP comunes"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "ok": False,
            "error": {
                "code": "not_found",
                "message": "Resource not found"
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return jsonify({
            "ok": False,
            "error": {
                "code": "internal_error",
                "message": "Internal server error"
            }
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "ok": False,
            "error": {
                "code": "method_not_allowed",
                "message": "Method not allowed"
            }
        }), 405


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=True
    )
