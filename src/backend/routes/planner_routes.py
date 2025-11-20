"""
Rutas para el módulo de Planificación
Gestión de abastecimiento de Solicitudes de Materiales
"""

from flask import Blueprint, request, jsonify, current_app
from ..services.auth.auth import auth_required, get_current_user
from ..core.db import get_connection
import logging

bp = Blueprint('planner', __name__, url_prefix='/api/planner')
logger = logging.getLogger(__name__)

# Decorador para verificar que sea Planificador o Admin
def require_planner(f):
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'unauthorized'}), 401
        
        rol = (user.get('rol') or '').lower()
        if 'planificador' not in rol and 'administrador' not in rol and 'admin' not in rol:
            return jsonify({'error': 'forbidden', 'message': 'Se requiere rol de Planificador o Administrador'}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.get('/dashboard')
@auth_required
@require_planner
def get_dashboard():
    """Obtener dashboard de planificación con estadísticas"""
    try:
        with get_connection() as con:
            # Solicitudes pendientes
            pending = con.execute(
                'SELECT COUNT(*) as count FROM solicitudes WHERE status = ? AND created_at IS NOT NULL',
                ('pending_approval',)
            ).fetchone()
            
            # Solicitudes en proceso
            in_process = con.execute(
                'SELECT COUNT(*) as count FROM solicitudes WHERE status = ? AND created_at IS NOT NULL',
                ('in_process',)
            ).fetchone()
            
            # Solicitudes aprobadas
            approved = con.execute(
                'SELECT COUNT(*) as count FROM solicitudes WHERE status = ? AND created_at IS NOT NULL',
                ('approved',)
            ).fetchone()
            
            # Solicitudes completadas
            completed = con.execute(
                'SELECT COUNT(*) as count FROM solicitudes WHERE status = ? AND created_at IS NOT NULL',
                ('completed',)
            ).fetchone()
        
        return jsonify({
            'pending': pending['count'] if pending else 0,
            'in_process': in_process['count'] if in_process else 0,
            'approved': approved['count'] if approved else 0,
            'completed': completed['count'] if completed else 0
        }), 200
    except Exception as e:
        logger.error(f'Error en dashboard: {e}')
        return jsonify({'error': 'error_loading_dashboard'}), 500

@bp.get('/solicitudes')
@auth_required
@require_planner
def get_solicitudes():
    """Obtener lista de solicitudes para planificación"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        offset = (page - 1) * per_page
        
        with get_connection() as con:
            # Obtener solicitudes
            solicitudes = con.execute('''
                SELECT id, centro, sector, criticidad, status, 
                       COUNT(DISTINCT id_item) as items_count,
                       SUM(cantidad * precio_unitario) as total,
                       created_at
                FROM solicitudes
                LEFT JOIN solicitud_items ON solicitudes.id = solicitud_items.solicitud_id
                GROUP BY solicitudes.id
                ORDER BY solicitudes.created_at DESC
                LIMIT ? OFFSET ?
            ''', (per_page, offset)).fetchall()
            
            # Total count
            total = con.execute(
                'SELECT COUNT(DISTINCT id) as count FROM solicitudes'
            ).fetchone()
        
        return jsonify({
            'solicitudes': [dict(row) for row in solicitudes] if solicitudes else [],
            'total': total['count'] if total else 0,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f'Error obteniendo solicitudes: {e}')
        return jsonify({'error': 'error_loading_requests'}), 500

@bp.get('/solicitudes/<int:solicitud_id>')
@auth_required
@require_planner
def get_solicitud_detail(solicitud_id):
    """Obtener detalle de una solicitud"""
    try:
        with get_connection() as con:
            # Obtener solicitud
            solicitud = con.execute('''
                SELECT id, centro, sector, criticidad, status, 
                       justificacion, id_usuario, created_at
                FROM solicitudes
                WHERE id = ?
            ''', (solicitud_id,)).fetchone()
            
            if not solicitud:
                return jsonify({'error': 'not_found'}), 404
            
            # Obtener materiales
            materiales = con.execute('''
                SELECT id_item, material_codigo, cantidad, precio_unitario,
                       (cantidad * precio_unitario) as total
                FROM solicitud_items
                WHERE solicitud_id = ?
            ''', (solicitud_id,)).fetchall()
        
        return jsonify({
            'id': solicitud['id'],
            'centro': solicitud['centro'],
            'sector': solicitud['sector'],
            'criticidad': solicitud['criticidad'],
            'status': solicitud['status'],
            'materiales': [dict(row) for row in materiales] if materiales else [],
            'total': sum(m['total'] for m in materiales) if materiales else 0
        }), 200
    except Exception as e:
        logger.error(f'Error obteniendo detalles: {e}')
        return jsonify({'error': 'error_loading_details'}), 500

@bp.post('/solicitudes/<int:solicitud_id>/optimize')
@auth_required
@require_planner
def optimize_solicitud(solicitud_id):
    """Aplicar optimización a una solicitud (placeholder para integración con planner)"""
    try:
        with get_connection() as con:
            data = request.get_json() or {}
            
            # Actualizar estado a "approved" (aprobada/optimizada)
            con.execute('''
                UPDATE solicitudes 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', ('approved', solicitud_id))
            con.commit()
        
        return jsonify({
            'ok': True,
            'message': 'Solicitud optimizada correctamente'
        }), 200
    except Exception as e:
        logger.error(f'Error optimizando solicitud: {e}')
        return jsonify({'error': 'error_optimizing'}), 500
