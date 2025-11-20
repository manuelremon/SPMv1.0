"""
Solicitudes routes - CRUD básico
"""
from flask import Blueprint, jsonify, request

bp = Blueprint('solicitudes', __name__, url_prefix='/api/solicitudes')

# Mock data
SOLICITUDES_DB = [
    {
        "id": 1,
        "asunto": "Solicitud de Materiales - Oficina Central",
        "descripcion": "Se necesitan materiales para equipar la nueva oficina",
        "estado": "Enviada",
        "prioridad": "Alta",
        "fecha_creacion": "2025-11-15T10:30:00Z",
        "usuario_id": "1",
        "usuario": {"id": "1", "nombre": "Admin"}
    },
    {
        "id": 2,
        "asunto": "Mantenimiento Equipos",
        "descripcion": "Reemplazo de componentes dañados",
        "estado": "En Proceso",
        "prioridad": "Media",
        "fecha_creacion": "2025-11-10T14:15:00Z",
        "usuario_id": "1",
        "usuario": {"id": "1", "nombre": "Admin"}
    }
]


@bp.route('', methods=['GET'])
def list_solicitudes():
    """Listar solicitudes"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return jsonify({
        "ok": True,
        "total": len(SOLICITUDES_DB),
        "page": page,
        "page_size": page_size,
        "results": SOLICITUDES_DB[start:end]
    }), 200


@bp.route('/<int:solicitud_id>', methods=['GET'])
def get_solicitud(solicitud_id):
    """Obtener una solicitud específica"""
    solicitud = next((s for s in SOLICITUDES_DB if s['id'] == solicitud_id), None)
    
    if not solicitud:
        return jsonify({
            "ok": False,
            "error": {
                "code": "not_found",
                "message": "Solicitud not found"
            }
        }), 404
    
    return jsonify({
        "ok": True,
        "solicitud": solicitud
    }), 200


@bp.route('', methods=['POST'])
def create_solicitud():
    """Crear una nueva solicitud"""
    data = request.get_json()
    
    new_id = max(s['id'] for s in SOLICITUDES_DB) + 1 if SOLICITUDES_DB else 1
    
    new_solicitud = {
        "id": new_id,
        "asunto": data.get('asunto'),
        "descripcion": data.get('descripcion'),
        "estado": "Borrador",
        "prioridad": data.get('prioridad', 'Media'),
        "fecha_creacion": "2025-11-20T18:00:00Z",
        "usuario_id": "1",
        "usuario": {"id": "1", "nombre": "Admin"}
    }
    
    SOLICITUDES_DB.append(new_solicitud)
    
    return jsonify({
        "ok": True,
        "message": "Solicitud created",
        "solicitud": new_solicitud
    }), 201


@bp.route('/<int:solicitud_id>', methods=['PUT'])
def update_solicitud(solicitud_id):
    """Actualizar una solicitud"""
    solicitud = next((s for s in SOLICITUDES_DB if s['id'] == solicitud_id), None)
    
    if not solicitud:
        return jsonify({
            "ok": False,
            "error": {
                "code": "not_found",
                "message": "Solicitud not found"
            }
        }), 404
    
    data = request.get_json()
    solicitud.update(data)
    
    return jsonify({
        "ok": True,
        "message": "Solicitud updated",
        "solicitud": solicitud
    }), 200


@bp.route('/<int:solicitud_id>', methods=['DELETE'])
def delete_solicitud(solicitud_id):
    """Eliminar una solicitud"""
    solicitud = next((s for s in SOLICITUDES_DB if s['id'] == solicitud_id), None)
    
    if not solicitud:
        return jsonify({
            "ok": False,
            "error": {
                "code": "not_found",
                "message": "Solicitud not found"
            }
        }), 404
    
    SOLICITUDES_DB.remove(solicitud)
    
    return jsonify({
        "ok": True,
        "message": "Solicitud deleted"
    }), 200
