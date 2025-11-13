"""
Tests de autenticación para backend_v2 - FASE 4.1
Valida login, registro, logout, roles y database real
"""
import pytest
from app import create_app
from core.db import drop_db, init_db, get_db
from models.user import User
from services.auth_service import AuthService


@pytest.fixture
def app():
    """Fixture: Aplicación Flask configurada para tests"""
    app = create_app({
        "TESTING": True,
        "ENV": "test",
        "DATABASE_URL": "sqlite:///:memory:"
    })
    
    with app.app_context():
        init_db()
        seed_test_users()
    
    yield app
    
    with app.app_context():
        drop_db()


def seed_test_users():
    """Crea usuarios de prueba en database"""
    users_data = [
        {
            "username": "admin",
            "password": "admin123",
            "nombre": "Admin",
            "apellido": "Sistema",
            "role": "Administrador",
            "email": "admin@spm.com",
            "is_active": True,
            "estado_registro": "Activo"
        },
        {
            "username": "planificador",
            "password": "plan123",
            "nombre": "Plan",
            "apellido": "SPM",
            "role": "Planificador",
            "email": "planificador@spm.com",
            "is_active": True,
            "estado_registro": "Activo"
        },
        {
            "username": "usuario",
            "password": "user123",
            "nombre": "Usuario",
            "apellido": "Prueba",
            "role": "Solicitante",
            "email": "usuario@spm.com",
            "is_active": True,
            "estado_registro": "Activo"
        },
        {
            "username": "inactivo",
            "password": "test123",
            "nombre": "Usuario",
            "apellido": "Inactivo",
            "role": "Solicitante",
            "email": "inactivo@spm.com",
            "is_active": False,
            "estado_registro": "Suspendido"
        }
    ]
    
    for user_data in users_data:
        try:
            AuthService.create_user(**user_data)
        except ValueError:
            # Usuario ya existe
            pass


@pytest.fixture
def client(app):
    """Fixture: Cliente de test"""
    return app.test_client()


# ============================================================================
# TESTS DE LOGIN
# ============================================================================

def test_login_success_admin(client):
    """Test: Login con credenciales de admin válidas"""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["username"] == "admin"
    assert data["user"]["email"] == "admin@spm.com"
    assert data["user"]["role"] == "Administrador"
    assert data["user"]["nombre"] == "Admin"
    assert data["user"]["apellido"] == "Sistema"
    
    # Verificar legacy aliases
    assert data["user"]["id_spm"] == "admin"
    assert data["user"]["rol"] == "Administrador"
    assert data["user"]["mail"] == "admin@spm.com"
    
    # Verificar cookie
    assert "spm_token" in response.headers.get("Set-Cookie", "")


def test_login_success_with_email(client):
    """Test: Login usando email en lugar de username"""
    response = client.post("/auth/login", json={
        "username": "planificador@spm.com",
        "password": "plan123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["username"] == "planificador"


def test_login_invalid_username(client):
    """Test: Login con username inexistente"""
    response = client.post("/auth/login", json={
        "username": "noexiste",
        "password": "password123"
    })
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "invalid_credentials"


def test_login_invalid_password(client):
    """Test: Login con password incorrecta"""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "invalid_credentials"


def test_login_inactive_user(client):
    """Test: Login con usuario inactivo retorna 401"""
    response = client.post("/auth/login", json={
        "username": "inactivo",
        "password": "test123"
    })
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "invalid_credentials"


def test_login_missing_username(client):
    """Test: Login sin username retorna 400"""
    response = client.post("/auth/login", json={
        "password": "admin123"
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "validation_error"


def test_login_missing_password(client):
    """Test: Login sin password retorna 400"""
    response = client.post("/auth/login", json={
        "username": "admin"
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data["ok"] is False


def test_login_empty_body(client):
    """Test: Login sin body retorna 415 (Unsupported Media Type)"""
    response = client.post("/auth/login")
    
    # Flask devuelve 415 cuando no hay Content-Type: application/json
    assert response.status_code == 415


# ============================================================================
# TESTS DE REGISTRO
# ============================================================================

def test_register_success(client):
    """Test: Registro de nuevo usuario exitoso"""
    response = client.post("/auth/register", json={
        "username": "nuevo_usuario",
        "password": "password123",
        "nombre": "Nuevo",
        "apellido": "Usuario",
        "role": "Solicitante",
        "email": "nuevo@spm.com"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["username"] == "nuevo_usuario"
    assert data["user"]["email"] == "nuevo@spm.com"
    assert data["user"]["role"] == "Solicitante"


def test_register_duplicate_username(client):
    """Test: Registro con username existente retorna 409"""
    response = client.post("/auth/register", json={
        "username": "admin",
        "password": "newpass123",
        "nombre": "Admin",
        "apellido": "Nuevo",
        "role": "Solicitante"
    })
    
    assert response.status_code == 409
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "duplicate_user"


def test_register_weak_password(client):
    """Test: Registro con contraseña débil (<6 chars) retorna 400"""
    response = client.post("/auth/register", json={
        "username": "test_user",
        "password": "12345",
        "nombre": "Test",
        "apellido": "User",
        "role": "Solicitante"
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "validation_error"


def test_register_missing_required_fields(client):
    """Test: Registro sin campos requeridos retorna 400"""
    response = client.post("/auth/register", json={
        "username": "incomplete",
        "password": "password123"
        # Falta nombre y apellido
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "validation_error"


def test_register_auto_extract_email(client):
    """Test: Registro extrae email de username si contiene @"""
    response = client.post("/auth/register", json={
        "username": "juan.perez@spm.com",
        "password": "password123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "role": "Solicitante"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["user"]["email"] == "juan.perez@spm.com"


# ============================================================================
# TESTS DE /auth/me
# ============================================================================

def test_me_authenticated_admin(client):
    """Test: /auth/me con admin retorna datos completos"""
    # Login
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    
    # GET /me
    response = client.get("/auth/me")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["ok"] is True
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "Administrador"
    assert data["user"]["full_name"] == "Admin Sistema"


def test_me_no_token(client):
    """Test: /auth/me sin token retorna 401"""
    response = client.get("/auth/me")
    
    assert response.status_code == 401
    data = response.get_json()
    
    assert data["ok"] is False
    assert data["error"]["code"] == "unauthorized"


# ============================================================================
# TESTS DE LOGOUT
# ============================================================================

def test_logout_success(client):
    """Test: Logout limpia cookie y retorna success"""
    # Login
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    
    # Logout
    response = client.post("/auth/logout")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["ok"] is True
    assert data["message"] == "Logged out successfully"
    
    # Verificar que cookie fue limpiada
    # (client mantiene cookies entre requests, verificamos con /me)
    me_response = client.get("/auth/me")
    assert me_response.status_code == 401


# ============================================================================
# TESTS DE AuthService
# ============================================================================

def test_auth_service_hash_password():
    """Test: AuthService genera hash bcrypt válido"""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert len(hashed) > 50


def test_auth_service_verify_password():
    """Test: AuthService verifica password correctamente"""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    
    assert AuthService.verify_password(hashed, password) is True
    assert AuthService.verify_password(hashed, "wrongpassword") is False


def test_auth_service_authenticate_user_success(app):
    """Test: AuthService autentica usuario válido"""
    with app.app_context():
        user = AuthService.authenticate_user("admin", "admin123")
        
        assert user is not None
        assert user.username == "admin"
        assert user.role == "Administrador"


def test_auth_service_authenticate_user_invalid(app):
    """Test: AuthService retorna None para credenciales inválidas"""
    with app.app_context():
        user = AuthService.authenticate_user("admin", "wrongpassword")
        assert user is None


def test_auth_service_get_user_by_username(app):
    """Test: AuthService obtiene usuario por username"""
    with app.app_context():
        user = AuthService.get_user_by_username("planificador")
        
        assert user is not None
        assert user.username == "planificador"
        assert user.email == "planificador@spm.com"


def test_auth_service_get_user_by_email(app):
    """Test: AuthService obtiene usuario por email"""
    with app.app_context():
        user = AuthService.get_user_by_username("usuario@spm.com")
        
        assert user is not None
        assert user.username == "usuario"


# ============================================================================
# TESTS DE MODELO User
# ============================================================================

def test_user_model_to_dict(app):
    """Test: User.to_dict() incluye legacy field aliases"""
    with app.app_context():
        user = AuthService.get_user_by_username("admin")
        user_dict = user.to_dict()
        
        # Campos nuevos v2
        assert user_dict["id"] == user.id
        assert user_dict["username"] == "admin"
        assert user_dict["email"] == "admin@spm.com"
        assert user_dict["role"] == "Administrador"
        
        # Legacy aliases v1
        assert user_dict["id_spm"] == "admin"
        assert user_dict["rol"] == "Administrador"
        assert user_dict["mail"] == "admin@spm.com"


def test_user_model_full_name_property(app):
    """Test: User.full_name concatena nombre + apellido"""
    with app.app_context():
        user = AuthService.get_user_by_username("admin")
        assert user.full_name == "Admin Sistema"


def test_user_model_centros_list_property(app):
    """Test: User.centros_list parsea centros string"""
    with app.app_context():
        # Crear usuario con centros
        user = AuthService.create_user(
            username="test_centros",
            password="test123",
            nombre="Test",
            apellido="Centros",
            centros="Centro1,Centro2;Centro3"
        )
        
        centros = user.centros_list
        assert isinstance(centros, list)
        assert len(centros) == 3
        assert "Centro1" in centros
        assert "Centro2" in centros
        assert "Centro3" in centros
