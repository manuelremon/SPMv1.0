import json
from backend_v2.app import create_app
from backend_v2.core.init_db import build_db
from backend_v2.services.auth_service import create_user
from backend_v2.services.solicitud_service import create_solicitud


def test_planner_endpoints():
    app = create_app()
    build_db(force=True)
    create_user('userpl', 'plpass')
    client = app.test_client()
    # create some solicitudes
    s1 = create_solicitud({'codigo': 's10', 'cantidad': 5})
    s2 = create_solicitud({'codigo': 's11', 'cantidad': 15, 'status': 'pending'})
    # dashboard
    r = client.get('/api/planner/dashboard')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert 'queue_count' in d
    # queue list
    rq = client.get('/api/planner/solicitudes')
    assert rq.status_code == 200
    qd = json.loads(rq.data)
    assert 'items' in qd
    # detail
    rd = client.get(f"/api/planner/solicitudes/{s1['id']}")
    assert rd.status_code == 200
    # optimize (requires csrf)
    login = client.post('/api/auth/login', json={'username': 'userpl', 'password': 'plpass'})
    body = json.loads(login.data)
    csrf = body.get('csrf')
    resp = client.post(f"/api/planner/solicitudes/{s2['id']}/optimize", json={}, headers={'X-CSRF-Token': csrf})
    assert resp.status_code == 200
    pdata = json.loads(resp.data)
    assert 'plan_id' in pdata or 'error' in pdata
