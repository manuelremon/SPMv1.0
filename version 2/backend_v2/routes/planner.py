from flask import Blueprint, request, jsonify
from ..services.planner_adapter import get_planner_dashboard, get_planner_queue, get_planner_solicitud, optimize_solicitud
from ..core.security import csrf_protect

bp = Blueprint('planner', __name__, url_prefix='/api/planner')


@bp.get('/dashboard')
def dashboard():
    user_id = request.args.get('user_id')
    return jsonify(get_planner_dashboard(user_id))


@bp.get('/solicitudes')
def queue_list():
    filters = {}
    # optional filters
    for k in ('centro', 'status', 'priority'):
        v = request.args.get(k)
        if v:
            filters[k] = v
    return jsonify({'items': get_planner_queue(filters=filters)})


@bp.get('/solicitudes/<int:solicitud_id>')
def solicitud_detail(solicitud_id: int):
    obj = get_planner_solicitud(solicitud_id)
    if not obj:
        return jsonify({'error': 'not found'}), 404
    return jsonify(obj)


@bp.post('/solicitudes/<int:solicitud_id>/optimize')
def optimize(solicitud_id: int):
    if not csrf_protect():
        return jsonify({'error': 'CSRF token missing or invalid'}), 403
    data = request.get_json() or {}
    plan = optimize_solicitud(solicitud_id, constraints=data.get('constraints'))
    if 'error' in plan:
        return jsonify(plan), 404
    return jsonify(plan)
