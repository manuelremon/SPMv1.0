"""
Inicialización de la base de datos con SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from core.config import settings

db = SQLAlchemy()


def init_db():
    """Inicializa la base de datos"""
    from flask import current_app
    
    # Crear todas las tablas
    with current_app.app_context():
        db.create_all()
        current_app.logger.info("Database initialized")
