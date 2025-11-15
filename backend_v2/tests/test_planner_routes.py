"""
Tests de integración para las rutas del módulo Planner (FASE 6).

Verifica que los endpoints REST funcionen correctamente end-to-end:
- POST /planner/analyze - Análisis de opciones de sourcing
- GET /planner/algorithms - Listar algoritmos disponibles
"""

import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from core.db import init_db, drop_db
from services.auth_service import AuthService


@pytest.fixture
def app():
    """Fixture que crea aplicación Flask para testing"""
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    
    with app.app_context():
        init_db()
        # Crear usuario de prueba
        try:
            AuthService.create_user(
                username="planner_test",
                password="Test123!@#",
                nombre="Planner",
                apellido="Test",
                role="Administrador",
                email="planner@test.com",
                is_active=True,
                estado_registro="Activo"
            )
        except ValueError:
            pass
    
    yield app
    
    with app.app_context():
        drop_db()


@pytest.fixture
def client(app):
    """Fixture que provee cliente HTTP para tests"""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Fixture que autentica el client para tests que requieren auth"""
    response = client.post(
        "/auth/login",
        json={
            "username": "planner_test",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200
    return client


class TestPlannerAnalyze:
    """Tests para POST /planner/analyze"""
    
    def test_analyze_success(self, auth_client):
        """Test análisis exitoso con todos los parámetros"""
        response = auth_client.post(
            "/planner/analyze",
            json={
                "item_id": "MAT-001",
                "demand_quantity": 100.0,
                "required_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "criticality": "HIGH",
                "budget_limit": 50000.0
            }
        )
        
        # DEBUG: Print response if not 200
        if response.status_code != 200:
            print(f"\n\n{'='*60}")
            print(f"ERROR: Status {response.status_code}")
            print(f"{'='*60}")
            import json as j
            try:
                err_data = j.loads(response.data.decode())
                print(j.dumps(err_data, indent=2))
            except:
                print(response.data.decode())
            print(f"{'='*60}\n")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["ok"] is True
        assert data["item_id"] == "MAT-001"
        assert data["demand_quantity"] == 100.0
        assert data["criticality"] == "HIGH"
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) == 8
        
        rec = data["recommendations"][0]
        assert "algorithm" in rec
        assert "proposed_quantity" in rec
        assert "estimated_cost" in rec
        assert "confidence_score" in rec
        assert 0 <= rec["confidence_score"] <= 1
        
        assert "best_option" in data
        assert "total_cost_range" in data
        assert "algorithms_executed" in data
        assert data["algorithms_executed"] == 8
    
    def test_analyze_minimal(self, auth_client):
        """Test análisis con parámetros mínimos"""
        response = auth_client.post(
            "/planner/analyze",
            json={
                "item_id": "MAT-002",
                "demand_quantity": 50.0,
                "required_date": (datetime.now() + timedelta(days=15)).isoformat()
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["ok"] is True
        assert data["criticality"] == "MEDIUM"
    
    def test_analyze_validation_missing_fields(self, auth_client):
        """Test validación - campos faltantes"""
        response = auth_client.post(
            "/planner/analyze",
            json={"item_id": "MAT-004"}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["ok"] is False
    
    def test_analyze_unauthorized(self, client):
        """Test sin autenticación"""
        response = client.post(
            "/planner/analyze",
            json={
                "item_id": "MAT-007",
                "demand_quantity": 100.0,
                "required_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
        )
        
        assert response.status_code == 401


class TestPlannerAlgorithms:
    """Tests para GET /planner/algorithms"""
    
    def test_get_algorithms_success(self, auth_client):
        """Test listado de algoritmos exitoso"""
        response = auth_client.get("/planner/algorithms")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["ok"] is True
        assert "algorithms" in data
        assert data["total"] == 8
        
        expected_algorithms = [
            "RESERVE_DYNAMIC",
            "PURCHASE_MULTICRITERION",
            "RELEASE_MARGINAL_COST",
            "TRANSFER_TDABC",
            "CTP_JOHNSON",
            "DISASSEMBLY_KNAPSACK",
            "EXPEDITE_PROBABILITY",
            "SUBSTITUTES_GRAPH"
        ]
        
        for algo in expected_algorithms:
            assert algo in data["algorithms"]
    
    def test_get_algorithms_unauthorized(self, client):
        """Test sin autenticación"""
        response = client.get("/planner/algorithms")
        assert response.status_code == 401

