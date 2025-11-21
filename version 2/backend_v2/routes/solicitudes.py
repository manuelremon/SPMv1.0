from flask import Blueprint, request, jsonify
from ..services.solicitud_service import create_solicitud, list_solicitudes, get_solicitud
from ..core.security import csrf_protect

bp = Blueprint('solicitudes', __name__, url_prefix='/api/solicitudes')


@bp.get('')
def list_route():
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    return jsonify({'items': list_solicitudes(limit=limit, offset=offset)})


@bp.post('')
def create_route():
    if not csrf_protect():
        return jsonify({'error': 'CSRF token missing or invalid'}), 403
    data = request.get_json() or {}
    item = create_solicitud(data)
    return jsonify(item), 201


@bp.get('/<int:solicitud_id>')
def detail_route(solicitud_id: int):
    item = get_solicitud(solicitud_id)
    if not item:
        return jsonify({'error': 'not found'}), 404
    return jsonify(item)
