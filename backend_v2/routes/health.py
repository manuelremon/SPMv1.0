"""
Backend v2.0 - Health check endpoints
"""
from flask import Blueprint, jsonify
from sqlalchemy import text

from core.db import engine

bp = Blueprint("health", __name__)


@bp.get("/health")
def health_check():
    """
    Health check básico.
    Retorna 200 si el servicio está vivo.
    """
    return jsonify({
        "ok": True,
        "status": "healthy",
        "service": "spm-backend-v2"
    }), 200


@bp.get("/ready")
def readiness_check():
    """
    Readiness check.
    Verifica que el servicio esté listo para recibir tráfico.
    Valida conectividad a base de datos.
    """
    try:
        # Intentar conexión a BD
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            "ok": True,
            "status": "ready",
            "service": "spm-backend-v2",
            "database": "connected"
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "status": "not_ready",
            "service": "spm-backend-v2",
            "database": "disconnected",
            "error": str(e)
        }), 503
