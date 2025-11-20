import json
from backend_v2.app import create_app
from backend_v2.core.init_db import build_db
from backend_v2.services.auth_service import create_user
from backend_v2.core.rate_limiter import reset_buckets


def test_create_and_list_solicitudes():
    reset_buckets()
    app = create_app()
    build_db(force=True)
    create_user('u', 'p')
    client = app.test_client()
    # create solicitud via POST (need csrf)
    login = client.post('/api/auth/login', json={'username': 'u', 'password': 'p'})
    body = json.loads(login.data)
    csrf = body.get('csrf')
    assert csrf
    # create
    resp = client.post('/api/solicitudes', json={'codigo': 's1', 'cantidad': 10}, headers={'X-CSRF-Token': csrf})
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert data['codigo'] == 's1'
    # list
    resp2 = client.get('/api/solicitudes')
    list_data = json.loads(resp2.data)
    assert 'items' in list_data and len(list_data['items']) >= 1
