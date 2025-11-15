"""
Tests de solicitudes y materiales para backend_v2 - FASE 4.2
Valida CRUD solicitudes, materiales, validaciones, approval workflow
"""
import pytest
from app import create_app
from core.db import drop_db, init_db, get_db
from models.user import User
from models.solicitud import Material, Solicitud, SolicitudItem, Aprobacion
from services.auth_service import AuthService
from services.solicitud_service import SolicitudService, MaterialService


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
        seed_test_materiales()
    
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
        }
    ]
    
    for user_data in users_data:
        try:
            AuthService.create_user(**user_data)
        except ValueError:
            pass


def seed_test_materiales():
    """Crea materiales de prueba en database"""
    materiales_data = [
        {
            "codigo": "MAT-001",
            "descripcion": "Laptop Dell Latitude",
            "precio_usd": 1200.00,
            "centro": "Buenos Aires",
            "sector": "IT"
        },
        {
            "codigo": "MAT-002",
            "descripcion": "Monitor LG 27 pulgadas",
            "precio_usd": 450.00,
            "centro": "Buenos Aires",
            "sector": "IT"
        },
        {
            "codigo": "MAT-003",
            "descripcion": "Teclado Mecánico",
            "precio_usd": 85.00,
            "centro": "Buenos Aires",
            "sector": "IT"
        }
    ]
    
    for material_data in materiales_data:
        try:
            MaterialService.create_material(material_data)
        except ValueError:
            pass


@pytest.fixture
def client(app):
    """Fixture: Cliente de test"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Fixture: Función para hacer login de cada rol"""
    def _login(username, password):
        response = client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        assert response.status_code == 200
        # El token está en cookie, se maneja automáticamente por test_client
    
    return _login


# ============================================================================
# TESTS DE MATERIALES - Search
# ============================================================================

def test_search_materiales_all(client):
    """Test: Buscar todos los materiales sin filtros"""
    response = client.get("/api/materiales")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "materiales" in data
    assert "total" in data
    assert data["total"] >= 3  # Los materiales seed
    assert len(data["materiales"]) >= 3


def test_search_materiales_by_codigo(client):
    """Test: Buscar material por código exacto"""
    response = client.get("/api/materiales?codigo=MAT-001")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["total"] >= 1
    # Debe contener MAT-001
    codigos = [m["codigo"] for m in data["materiales"]]
    assert "MAT-001" in codigos


def test_search_materiales_by_descripcion(client):
    """Test: Buscar material por descripción (case-insensitive)"""
    response = client.get("/api/materiales?descripcion=laptop")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["total"] >= 1
    # Debe contener "Laptop" en descripción
    descripciones = [m["descripcion"].lower() for m in data["materiales"]]
    assert any("laptop" in desc for desc in descripciones)


def test_search_materiales_by_general_query(client):
    """Test: Búsqueda general (codigo OR descripcion)"""
    response = client.get("/api/materiales?q=monitor")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["total"] >= 1


def test_search_materiales_limit(client):
    """Test: Limitar resultados de búsqueda"""
    response = client.get("/api/materiales?limit=2")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data["materiales"]) <= 2


def test_get_material_by_codigo_success(client):
    """Test: Obtener material por código (existente)"""
    response = client.get("/api/materiales/MAT-001")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["codigo"] == "MAT-001"
    assert data["descripcion"] == "Laptop Dell Latitude"
    assert data["precio_usd"] == 1200.00


def test_get_material_by_codigo_not_found(client):
    """Test: Obtener material por código (no existe)"""
    response = client.get("/api/materiales/MAT-9999")
    
    assert response.status_code == 404
    data = response.get_json()
    
    assert "error" in data
    # Verificar que el código aparece en el mensaje (agnóstico al idioma)
    assert "mat-9999" in data["error"]["message"].lower()


# ============================================================================
# TESTS DE MATERIALES - Create/Update (Admin only)
# ============================================================================

def test_create_material_as_admin(client, auth_headers):
    """Test: Crear material como admin"""
    auth_headers("admin", "admin123")  # Login as admin
    
    response = client.post("/api/materiales", json={
        "codigo": "MAT-TEST-001",
        "descripcion": "Material de prueba",
        "precio_usd": 99.99,
        "centro": "Mendoza",
        "sector": "Test"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert data["codigo"] == "MAT-TEST-001"
    assert data["precio_usd"] == 99.99


def test_create_material_duplicate_codigo(client, auth_headers):
    """Test: Crear material con código duplicado"""
    auth_headers("admin", "admin123")
    
    response = client.post("/api/materiales", json={
        "codigo": "MAT-001",  # Ya existe
        "descripcion": "Duplicado",
        "precio_usd": 100.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert "error" in data
    assert "ya existe" in data["error"]["message"].lower()


def test_update_material_as_admin(client, auth_headers):
    """Test: Actualizar material como admin"""
    auth_headers("admin", "admin123")
    
    response = client.put("/api/materiales/MAT-001", json={
        "precio_usd": 1500.00,
        "descripcion": "Laptop Dell Latitude (Actualizado)"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["codigo"] == "MAT-001"
    assert data["precio_usd"] == 1500.00
    assert "Actualizado" in data["descripcion"]


def test_update_material_not_found(client, auth_headers):
    """Test: Actualizar material que no existe"""
    auth_headers("admin", "admin123")
    
    response = client.put("/api/materiales/MAT-9999", json={
        "precio_usd": 100.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert "error" in data


# ============================================================================
# TESTS DE SOLICITUDES - Create
# ============================================================================

def test_create_solicitud_success(client, auth_headers):
    """Test: Crear solicitud con items válidos"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "sector": "IT",
        "justificacion": "Necesito equipamiento para desarrollo",
        "items": [
            {"material_codigo": "MAT-001", "cantidad": 2},
            {"material_codigo": "MAT-002", "cantidad": 1}
        ]
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert "solicitud" in data
    sol = data["solicitud"]
    
    assert sol["centro"] == "Buenos Aires"
    assert sol["status"] == "pendiente_de_aprobacion"  # Con items va a aprobación
    assert sol["id_usuario"] == "usuario"
    assert len(sol["items"]) == 2
    
    # Verificar total calculado
    # 2 * 1200 + 1 * 450 = 2850
    assert sol["total_monto"] == 2850.00


def test_create_solicitud_without_items(client, auth_headers):
    """Test: Crear solicitud sin items (debe fallar)"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Solicitud sin items para testing",
        "items": []
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert "error" in data


def test_create_solicitud_invalid_material(client, auth_headers):
    """Test: Crear solicitud con material que no existe"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Solicitud con material inválido para testing",
        "items": [
            {"material_codigo": "MAT-9999", "cantidad": 1}
        ]
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert "error" in data
    assert "no encontrado" in data["error"]["message"].lower()


def test_create_solicitud_negative_cantidad(client, auth_headers):
    """Test: Crear solicitud con cantidad negativa (validación Pydantic)"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Solicitud con cantidad negativa para testing",
        "items": [
            {"material_codigo": "MAT-001", "cantidad": -5}
        ]
    })
    
    assert response.status_code == 400


def test_create_solicitud_auto_price_lookup(client, auth_headers):
    """Test: Crear solicitud sin precio (auto lookup desde catálogo)"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Testing auto price lookup from catalog",
        "items": [
            {"material_codigo": "MAT-001", "cantidad": 1}
            # Sin precio_unitario
        ]
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    # Debe tener el precio del catálogo
    sol = data["solicitud"]
    assert sol["total_monto"] == 1200.00  # Precio de MAT-001


# ============================================================================
# TESTS DE SOLICITUDES - Draft
# ============================================================================

def test_create_draft_without_items(client, auth_headers):
    """Test: Crear borrador sin items (permitido)"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/solicitudes/drafts", json={
        "centro": "Buenos Aires",
        "justificacion": "Borrador inicial para testing de drafts",
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    sol = data["solicitud"]
    assert sol["status"] == "draft"  # Estado draft
    assert sol["items"] == []


# ============================================================================
# TESTS DE SOLICITUDES - List
# ============================================================================

def test_list_solicitudes_as_usuario(client, auth_headers):
    """Test: Listar solicitudes como usuario normal (solo las propias)"""
    auth_headers("usuario", "user123")
    
    # Crear solicitud primero
    client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Test",
        "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
    })
    
    response = client.get("/api/solicitudes")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "solicitudes" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    
    # Todas las solicitudes deben ser del usuario
    for sol in data["solicitudes"]:
        assert sol["id_usuario"] == "usuario"


def test_list_solicitudes_as_admin(client, auth_headers, app):
    """Test: Listar solicitudes como admin (todas)"""
    # Crear solicitudes con diferentes usuarios
    with app.app_context():
        sol1_data = {
            "centro": "Buenos Aires",
            "justificacion": "Solicitud número 1 para testing",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        SolicitudService.create_solicitud("usuario", sol1_data)
        SolicitudService.create_solicitud("planificador", sol1_data)
    
    auth_headers("admin", "admin123")
    
    response = client.get("/api/solicitudes")
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Admin debe ver todas las solicitudes
    assert data["total"] >= 2
    
    usuarios = {sol["id_usuario"] for sol in data["solicitudes"]}
    assert len(usuarios) >= 2  # Al menos 2 usuarios diferentes


def test_list_solicitudes_filter_by_status(client, auth_headers):
    """Test: Filtrar solicitudes por status"""
    auth_headers("usuario", "user123")
    
    response = client.get("/api/solicitudes?status=borrador")
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Todas deben tener status=borrador
    for sol in data["solicitudes"]:
        assert sol["status"] == "borrador"


def test_list_solicitudes_pagination(client, auth_headers):
    """Test: Paginación de solicitudes"""
    auth_headers("usuario", "user123")
    
    response = client.get("/api/solicitudes?page=1&per_page=5")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["page"] == 1
    assert data["per_page"] == 5
    assert len(data["solicitudes"]) <= 5


# ============================================================================
# TESTS DE SOLICITUDES - Get Detail
# ============================================================================

def test_get_solicitud_by_id_success(client, auth_headers, app):
    """Test: Obtener detalle de solicitud"""
    # Crear solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Detalle completo de la solicitud",
            "items": [{"material_codigo": "MAT-001", "cantidad": 2}]
        }
        sol = SolicitudService.create_solicitud("usuario", sol_data)
        sol_id = sol.id
    
    auth_headers("usuario", "user123")
    
    response = client.get(f"/api/solicitudes/{sol_id}")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["id"] == sol_id
    assert data["centro"] == "Buenos Aires"
    assert len(data["items"]) == 1


def test_get_solicitud_not_found(client, auth_headers):
    """Test: Obtener solicitud que no existe"""
    auth_headers("usuario", "user123")
    
    response = client.get("/api/solicitudes/99999")
    
    assert response.status_code == 404
    data = response.get_json()
    
    assert "error" in data


def test_get_solicitud_forbidden(client, auth_headers, app):
    """Test: Obtener solicitud de otro usuario (forbidden)"""
    # Crear solicitud con planificador
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Solicitud del planificador para testing",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("planificador", sol_data)
        sol_id = sol.id
    
    # Intentar acceder como usuario
    auth_headers("usuario", "user123")
    
    response = client.get(f"/api/solicitudes/{sol_id}")
    
    assert response.status_code == 403
    data = response.get_json()
    
    assert "error" in data


# ============================================================================
# TESTS DE SOLICITUDES - Update
# ============================================================================

def test_update_solicitud_success(client, auth_headers, app):
    """Test: Actualizar solicitud en estado borrador"""
    # Crear solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Justificación original de la solicitud",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("usuario", sol_data)
        sol_id = sol.id
    
    auth_headers("usuario", "user123")
    
    response = client.patch(f"/api/solicitudes/{sol_id}", json={
        "justificacion": "Justificación actualizada con más detalles",
        "items": [
            {"material_codigo": "MAT-002", "cantidad": 2}
        ]
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["justificacion"] == "Justificación actualizada con más detalles"
    assert len(data["items"]) == 1
    assert data["items"][0]["material_codigo"] == "MAT-002"
    # Total = 2 * 450 = 900
    assert data["total_monto"] == 900.00


def test_update_solicitud_approved_fails(client, auth_headers, app):
    """Test: No se puede actualizar solicitud aprobada"""
    # Crear y aprobar solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Solicitud para aprobar en testing",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("usuario", sol_data)
        sol_id = sol.id
        
        # Aprobar
        SolicitudService.aprobar_solicitud(sol_id, "planificador", "OK")
    
    auth_headers("usuario", "user123")
    
    response = client.patch(f"/api/solicitudes/{sol_id}", json={
        "justificacion": "Intentar actualizar solicitud aprobada",
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert "error" in data


# ============================================================================
# TESTS DE SOLICITUDES - Aprobar/Rechazar
# ============================================================================

def test_aprobar_solicitud_as_planificador(client, auth_headers, app):
    """Test: Aprobar solicitud como planificador"""
    # Crear solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Solicitud para testing de aprobación",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("usuario", sol_data)
        sol_id = sol.id
    
    auth_headers("planificador", "plan123")
    
    response = client.post(f"/api/solicitudes/{sol_id}/aprobar", json={
        "comentario": "Aprobado por planificador"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["status"] == "aprobada"
    assert data["aprobador_id"] == "planificador"


def test_rechazar_solicitud_as_planificador(client, auth_headers, app):
    """Test: Rechazar solicitud como planificador"""
    # Crear solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Solicitud para testing de rechazo",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("usuario", sol_data)
        sol_id = sol.id
    
    auth_headers("planificador", "plan123")
    
    response = client.post(f"/api/solicitudes/{sol_id}/rechazar", json={
        "comentario": "No cumple requisitos"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["status"] == "rechazada"


# ============================================================================
# TESTS DE AUTHORIZATION
# ============================================================================

def test_create_solicitud_unauthorized(client):
    """Test: Crear solicitud sin autenticación"""
    response = client.post("/api/solicitudes", json={
        "centro": "Buenos Aires",
        "justificacion": "Testing sin autenticación requerida",
        "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
    })
    
    assert response.status_code == 401


def test_create_material_as_usuario_forbidden(client, auth_headers):
    """Test: Usuario normal no puede crear materiales"""
    auth_headers("usuario", "user123")
    
    response = client.post("/api/materiales", json={
        "codigo": "MAT-NEW",
        "descripcion": "Test",
        "precio_usd": 100.0
    })
    
    assert response.status_code == 403


def test_aprobar_solicitud_as_usuario_forbidden(client, auth_headers, app):
    """Test: Usuario normal no puede aprobar solicitudes"""
    # Crear solicitud
    with app.app_context():
        sol_data = {
            "centro": "Buenos Aires",
            "justificacion": "Test de listado de solicitudes",
            "items": [{"material_codigo": "MAT-001", "cantidad": 1}]
        }
        sol = SolicitudService.create_solicitud("planificador", sol_data)
        sol_id = sol.id
    
    auth_headers("usuario", "user123")
    
    response = client.post(f"/api/solicitudes/{sol_id}/aprobar", json={
        "comentario": "Intentar aprobar"
    })
    
    assert response.status_code == 403
