from typing import List, Optional
from ..models.solicitud import Solicitud
from ..core.db import get_session


def create_solicitud(data: dict) -> dict:
    session = get_session()
    try:
        solicitud = Solicitud(
            codigo=data.get('codigo'),
            centro=data.get('centro'),
            codigo_material=data.get('codigo_material'),
            cantidad=data.get('cantidad', 0),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'normal'),
        )
        session.add(solicitud)
        session.commit()
        session.refresh(solicitud)
        return solicitud.to_dict()
    finally:
        session.close()


def list_solicitudes(limit: int = 50, offset: int = 0) -> List[dict]:
    session = get_session()
    try:
        q = session.query(Solicitud).order_by(Solicitud.created_at.desc()).limit(limit).offset(offset)
        return [s.to_dict() for s in q.all()]
    finally:
        session.close()


def get_solicitud(solicitud_id: int) -> Optional[dict]:
    session = get_session()
    try:
        s = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        return s.to_dict() if s else None
    finally:
        session.close()
