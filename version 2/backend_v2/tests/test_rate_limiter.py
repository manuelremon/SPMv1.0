from backend_v2.app import create_app
from backend_v2.core.init_db import build_db
from backend_v2.services.auth_service import create_user
from backend_v2.core.rate_limiter import reset_buckets


def test_login_rate_limit_exceeded():
    reset_buckets()
    app = create_app()
    build_db(force=True)
    create_user('ratetest', 'secret')
    client = app.test_client()
    # perform 6 attempts, limit is 5/min in the in_memory_limit
    for i in range(6):
        resp = client.post('/api/auth/login', json={'username': 'ratetest', 'password': 'secret'})
        if i < 5:
            assert resp.status_code == 200
        else:
            assert resp.status_code == 429
