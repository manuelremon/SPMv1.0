"""
Dashboard Statistics Service
Proporciona estadísticas y datos para el dashboard
"""
from datetime import datetime, timedelta
from ...core.db import get_db
import json

def _get_json_field(row, data_json_column):
    """Helper para extraer datos de la columna data_json"""
    try:
        if isinstance(row[data_json_column], dict):
            return row[data_json_column]
        if isinstance(row[data_json_column], str):
            return json.loads(row[data_json_column])
    except:
        pass
    return {}

def get_user_stats(user_id):
    """Obtiene estadísticas del usuario"""
    try:
        db = get_db()
        
        # Contar solicitudes por estado (usando 'status' en lugar de 'estado')
        # Note: get_db() returns cursor with row_factory set to dict mode
        pending = db.execute(
            "SELECT COUNT(*) as count FROM solicitudes WHERE id_usuario = ? AND status = 'pendiente_de_aprobacion'",
            (user_id,)
        ).fetchone()
        pending_count = pending['count'] if pending else 0
        
        approved = db.execute(
            "SELECT COUNT(*) as count FROM solicitudes WHERE id_usuario = ? AND status = 'aprobada'",
            (user_id,)
        ).fetchone()
        approved_count = approved['count'] if approved else 0
        
        in_process = db.execute(
            "SELECT COUNT(*) as count FROM solicitudes WHERE id_usuario = ? AND status = 'en_proceso'",
            (user_id,)
        ).fetchone()
        in_process_count = in_process['count'] if in_process else 0
        
        rejected = db.execute(
            "SELECT COUNT(*) as count FROM solicitudes WHERE id_usuario = ? AND status = 'rechazada'",
            (user_id,)
        ).fetchone()
        rejected_count = rejected['count'] if rejected else 0
        
        # Contar materiales
        materials = db.execute(
            "SELECT COUNT(*) as count FROM materiales"
        ).fetchone()
        total_materials = materials['count'] if materials else 0
        
        # Calcular tasa de aprobación
        total_reviewed = approved_count + rejected_count
        approval_rate = int((approved_count / total_reviewed * 100) if total_reviewed > 0 else 0)
        
        # Últimas solicitudes (extraer título de data_json)
        # db.row_factory already set to dict mode via get_db()
        recent = db.execute("""
            SELECT id, data_json, status, created_at 
            FROM solicitudes 
            WHERE id_usuario = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (user_id,)).fetchall()
        
        recent_requests = []
        for r in recent:
            data = _get_json_field(r, 'data_json')
            titulo = data.get('justificacion', 'Sin título')[:50]
            recent_requests.append({
                "id": r['id'],
                "title": titulo,
                "status": r['status'],
                "date": r.get('created_at', '')
            })
        
        return {
            "pending": pending_count,
            "approved": approved_count,
            "in_process": in_process_count,
            "rejected": rejected_count,
            "total_materials": total_materials,
            "approval_rate": approval_rate,
            "recent_requests": recent_requests
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        import traceback
        traceback.print_exc()
        return {
            "pending": 0,
            "approved": 0,
            "in_process": 0,
            "rejected": 0,
            "total_materials": 0,
            "approval_rate": 0,
            "recent_requests": []
        }


def get_dashboard_activity():
    """Obtiene actividad reciente del sistema"""
    try:
        db = get_db()
        
        # Últimas acciones (solicitudes creadas/aprobadas)
        # Note: db already has row_factory set to dict mode via get_db()
        activity = db.execute("""
            SELECT id, data_json, status, created_at, id_usuario
            FROM solicitudes
            ORDER BY created_at DESC
            LIMIT 10
        """).fetchall()
        
        items = []
        status_map = {
            'pendiente_de_aprobacion': '📋',
            'aprobada': '✅',
            'en_proceso': '⏳',
            'rechazada': '❌',
            'finalizada': '✔️',
            'draft': '📝',
            'cancelada': '⛔'
        }
        
        status_text = {
            'pendiente_de_aprobacion': 'Pendiente aprobación',
            'aprobada': 'Aprobada',
            'en_proceso': 'En proceso',
            'rechazada': 'Rechazada',
            'finalizada': 'Finalizada',
            'draft': 'Borrador',
            'cancelada': 'Cancelada'
        }
        
        for a in activity:
            try:
                # Extraer datos de data_json
                data_json_str = a.get('data_json', '{}')
                if isinstance(data_json_str, str):
                    data = json.loads(data_json_str) if data_json_str else {}
                else:
                    data = data_json_str if isinstance(data_json_str, dict) else {}
                
                titulo = data.get('justificacion', 'Sin descripción')[:40]
                status = a.get('status', 'unknown')
                icon = status_map.get(status, '📝')
                
                items.append({
                    "id": a.get('id'),
                    "title": f"{icon} {titulo}",
                    "status": status,
                    "status_text": status_text.get(status, 'Desconocido'),
                    "date": a.get('created_at', ''),
                    "user_id": a.get('id_usuario', '')
                })
            except Exception as e:
                print(f"Error processing activity item: {e}")
                continue
        
        return items
    except Exception as e:
        print(f"Error getting dashboard activity: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_chart_data():
    """Obtiene datos para gráficos"""
    try:
        db = get_db()
        
        # Datos para gráfico de estados (usar 'status' en lugar de 'estado')
        states = db.execute("""
            SELECT status, COUNT(*) as count 
            FROM solicitudes 
            GROUP BY status
        """).fetchall()
        
        # Datos para tendencia (últimos 7 días) - usar 'created_at' en lugar de 'fecha_creacion'
        today = datetime.now()
        trend_data = []
        
        for i in range(6, -1, -1):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            count_row = db.execute(
                "SELECT COUNT(*) as count FROM solicitudes WHERE DATE(created_at) = ?",
                (date,)
            ).fetchone()
            count = count_row['count'] if count_row else 0
            trend_data.append({
                "date": date.split('-')[2],  # Solo el día
                "count": count
            })
        
        # Distribución por centro
        centers = db.execute("""
            SELECT centro, COUNT(*) as count 
            FROM solicitudes 
            WHERE centro IS NOT NULL AND centro != ''
            GROUP BY centro
            ORDER BY count DESC
            LIMIT 5
        """).fetchall()
        
        # Mapear estados a nombres más legibles
        status_names = {
            'pendiente_de_aprobacion': 'Pendiente Aprobación',
            'aprobada': 'Aprobada',
            'en_proceso': 'En Proceso',
            'rechazada': 'Rechazada',
            'finalizada': 'Finalizada',
            'draft': 'Borrador',
            'cancelada': 'Cancelada'
        }
        
        return {
            "states": [
                {
                    "name": status_names.get(s['status'], s['status']), 
                    "status": s['status'],
                    "count": s['count']
                } 
                for s in states
            ],
            "trend": trend_data,
            "centers": [
                {"name": c['centro'] or 'Sin centro', "count": c['count']} 
                for c in centers
            ]
        }
    except Exception as e:
        print(f"Error getting chart data: {e}")
        import traceback
        traceback.print_exc()
        return {
            "states": [],
            "trend": [],
            "centers": []
        }
