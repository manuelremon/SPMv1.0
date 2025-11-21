from typing import Dict, List, Optional
from ..services.solicitud_service import list_solicitudes, get_solicitud


def get_planner_dashboard(user_id: str) -> Dict:
    # Very small sample implementation: counts
    pending = list_solicitudes(limit=100)
    return {
        'queue_count': len(pending),
        'pending_solicitudes': [s for s in pending if s.get('status') == 'pending'],
        'expected_load': {
            'approx_hour': len(pending) // 2,
        }
    }


def get_planner_queue(filters: Optional[dict] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
    # simple filter skeleton (center, status)
    items = list_solicitudes(limit=limit, offset=offset)
    if not filters:
        return items
    def matches(s):
        for k, v in (filters or {}).items():
            if s.get(k) != v:
                return False
        return True
    return [s for s in items if matches(s)]


def get_planner_solicitud(solicitud_id: int) -> Optional[Dict]:
    return get_solicitud(solicitud_id)


def optimize_solicitud(solicitud_id: int, constraints: Optional[dict] = None) -> Dict:
    obj = get_solicitud(solicitud_id)
    if not obj:
        return {'error': 'not found'}
    # Very simple plan: if stock insufficient, recommend to buy.
    plan = {
        'plan_id': f'p-{solicitud_id}',
        'score': 0.75,
        'actions': [
            {'type': 'split_stock', 'stock_qty': 0, 'to_buy': obj.get('cantidad', 0)}
        ],
        'estimated_cost': 0.0
    }
    return plan
