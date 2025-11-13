"""
Backend v2.0 - Database layer
SQLAlchemy engine y session factory preparado para Postgres
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from core.config import settings

# Base para modelos SQLAlchemy
Base = declarative_base()

# Engine global
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Valida conexiones antes de usar
    pool_recycle=3600,   # Recicla conexiones cada hora
)


# SQLite-specific: habilitar foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Habilita foreign keys en SQLite (no afecta Postgres)"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para obtener sesión de DB.
    
    Uso:
        with get_db() as db:
            user = db.query(User).filter_by(email=email).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    Usar solo en desarrollo o para tests.
    En producción usar Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Elimina todas las tablas. Solo para tests."""
    Base.metadata.drop_all(bind=engine)
