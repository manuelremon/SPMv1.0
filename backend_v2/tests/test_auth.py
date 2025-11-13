"""
Tests de autenticación para backend_v2
Valida login, logout, y decorator @auth_required
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


def test_login_success(client):
    """Test: Login con credenciales válidas retorna token"""
    response = client.post("/auth/login", json={
        "username": "admin@spm.com",
        "password": "admin123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["email"] == "admin@spm.com"
    assert data["user"]["role"] == "admin"
    
    # Verificar que cookie fue seteada
    assert "spm_token" in response.headers.get("Set-Cookie", "")


def test_login_invalid_credentials(client):
    """Test: Login con credenciales inválidas retorna 401"""
    response = client.post("/auth/login", json={
        "username": "admin@spm.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "invalid_credentials"


def test_login_missing_fields(client):
    """Test: Login sin username o password retorna 400"""
    response = client.post("/auth/login", json={
        "username": "admin@spm.com"
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "missing_fields"


def test_me_endpoint_authenticated(client):
    """Test: GET /auth/me con token válido retorna usuario"""
    # Login primero
    login_response = client.post("/auth/login", json={
        "username": "admin@spm.com",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200
    
    # Ahora llamar a /auth/me (cookie se mantiene en client)
    me_response = client.get("/auth/me")
    
    assert me_response.status_code == 200
    data = me_response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["email"] == "admin@spm.com"


def test_me_endpoint_unauthenticated(client):
    """Test: GET /auth/me sin token retorna 401"""
    response = client.get("/auth/me")
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "unauthorized"


def test_logout(client):
    """Test: POST /auth/logout limpia cookie de token"""
    # Login primero
    login_response = client.post("/auth/login", json={
        "username": "admin@spm.com",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200
    
    # Logout
    logout_response = client.post("/auth/logout")
    
    assert logout_response.status_code == 200
    data = logout_response.get_json()
    
    assert data["ok"] is True
    assert data["message"] == "Logged out successfully"
    
    # Verificar que ahora /auth/me falla
    me_response = client.get("/auth/me")
    assert me_response.status_code == 401
