"""
Tests de humo para backend_v2
Valida que endpoints /health y /ready funcionen
"""
import pytest
from app import create_app
from core.db import drop_db, init_db


@pytest.fixture
def app():
    """Fixture: Aplicación Flask configurada para tests"""
    app = create_app({
        "TESTING": True,
        "ENV": "test"
    })
    
    with app.app_context():
        init_db()
    
    yield app
    
    with app.app_context():
        drop_db()


@pytest.fixture
def client(app):
    """Fixture: Cliente de test"""
    return app.test_client()


def test_health_endpoint(client):
    """Test: GET /health retorna 200 OK"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["status"] == "healthy"
    assert data["service"] == "spm-backend-v2"


def test_readiness_endpoint(client):
    """Test: GET /ready retorna 200 OK con DB conectada"""
    response = client.get("/ready")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_404_error_handler(client):
    """Test: Endpoints no existentes retornan 404"""
    response = client.get("/nonexistent")
    
    assert response.status_code == 404
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "not_found"
