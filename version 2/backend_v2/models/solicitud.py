from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.base import Base


class Solicitud(Base):
    __tablename__ = 'solicitudes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(64), nullable=False, index=True)
    centro = Column(String(64), nullable=True)
    codigo_material = Column(String(64), nullable=True)
    cantidad = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default='pending')
    priority = Column(String(16), default='normal')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'centro': self.centro,
            'codigo_material': self.codigo_material,
            'cantidad': self.cantidad,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
        }
