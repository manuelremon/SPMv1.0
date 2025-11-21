import json
from backend_v2.app import create_app
from backend_v2.core.init_db import build_db
from backend_v2.services.auth_service import create_user
from backend_v2.services.solicitud_service import create_solicitud
from backend_v2.core.rate_limiter import reset_buckets


def setup_app():
    app = create_app()
    # Use sqlite file for tests
    build_db(force=True)
    return app


def test_csrf_protection_on_planner_optimize():
    reset_buckets()
    app = setup_app()
    client = app.test_client()
    # create user
    create_user('testuser', 'secret')
    # create a solicitud
    s = create_solicitud({'codigo': 'sol1', 'cantidad': 10})
    # login
    resp = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'secret'})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    csrf = data.get('csrf')
    assert csrf
    # attempt to call optimize without csrf header
    resp2 = client.post(f"/api/planner/solicitudes/{s['id']}/optimize", json={})
    assert resp2.status_code == 403
    # call with csrf header
    resp3 = client.post(f"/api/planner/solicitudes/{s['id']}/optimize", json={}, headers={'X-CSRF-Token': csrf})
    assert resp3.status_code in (200, 404)
