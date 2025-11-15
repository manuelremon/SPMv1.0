"""
Routes - Planner Module (FASE 6)

Este módulo expone los endpoints REST para el sistema de planeación inteligente.
Orquesta 8 algoritmos de sourcing y proporciona recomendaciones optimizadas.

Endpoints:
  - POST /planner/analyze: Analiza opciones de sourcing
  - GET /planner/recommendations/<id>: Recupera recomendaciones guardadas
  - POST /planner/execute-plan: Ejecuta un plan aprobado
  - GET /planner/status/<plan_id>: Consulta estado de ejecución
  - GET /planner/algorithms: Lista algoritmos disponibles
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from core.db import get_db
from middleware.auth import auth_required
from schemas.planner_schema import (
    AnalyzeRequest, AnalyzeResponse, ExecutePlanRequest,
    ExecutePlanResponse, PlanStatusResponse, ErrorResponse
)
from services.planner.planner_service import get_planner_service


planner_bp = Blueprint("planner", __name__, url_prefix="/planner")


@planner_bp.post("/analyze")
@auth_required
def analyze_sourcing(user_payload):
    """
    POST /planner/analyze
    
    Analiza opciones de sourcing ejecutando todos los algoritmos disponibles.
    Requiere autenticación.
    
    Body:
      - item_id: str
      - demand_quantity: float
      - required_date: datetime (ISO 8601)
      - criticality: str (CRITICAL|HIGH|MEDIUM|LOW)
      - budget_limit: float (opcional)
    
    Returns:
      - 200: AnalyzeResponse con recomendaciones
      - 400: ValidationError
      - 500: Error interno
    """
    try:
        # Validar request con Pydantic
        data = request.get_json()
        analyze_req = AnalyzeRequest(**data)
        
        # Ejecutar análisis con context manager
        with get_db() as db_session:
            service = get_planner_service()
            result = service.analyze_sourcing_options(
                item_id=analyze_req.item_id,
                demand_quantity=analyze_req.demand_quantity,
                required_date=analyze_req.required_date,
                criticality=analyze_req.criticality,
                budget_limit=analyze_req.budget_limit,
                db_session=db_session
            )
        
        # Validar response con Pydantic
        response = AnalyzeResponse(**result)
        return jsonify(response.model_dump()), 200
    
    except ValidationError as e:
        return jsonify(ErrorResponse(
            ok=False,
            error={
                "code": "validation_error",
                "message": "Datos de entrada inválidos",
                "details": e.errors()
            }
        ).model_dump()), 400
    
    except Exception as e:
        return jsonify(ErrorResponse(
            ok=False,
            error={
                "code": "internal_error",
                "message": str(e)
            }
        ).model_dump()), 500


@planner_bp.get("/recommendations/<solicitud_id>")
@auth_required
def get_recommendations(user_payload, solicitud_id: str):
    """
    GET /planner/recommendations/<solicitud_id>
    
    Recupera recomendaciones guardadas para una solicitud.
    [PLACEHOLDER - Requiere implementación de persistencia]
    """
    return jsonify({
        "ok": False,
        "error": {
            "code": "not_implemented",
            "message": "Feature not yet implemented"
        }
    }), 501


@planner_bp.post("/execute-plan")
@auth_required
def execute_plan(user_payload):
    """
    POST /planner/execute-plan
    
    Ejecuta un plan de sourcing aprobado.
    [PLACEHOLDER - Requiere implementación de lógica de ejecución]
    
    Body:
      - item_id: str
      - algorithm: str (enum)
      - quantity: float
      - approved_by: str (opcional)
      - notes: str (opcional)
    
    Returns:
      - 200: ExecutePlanResponse con plan_id
      - 400: ValidationError
      - 500: Error interno
    """
    try:
        data = request.get_json()
        plan_req = ExecutePlanRequest(**data)
        
        # PLACEHOLDER: Crear registro de ejecución en DB
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        response = ExecutePlanResponse(
            ok=True,
            plan_id=plan_id,
            status="PENDING_EXECUTION",
            message="Plan creado exitosamente",
            timestamp=datetime.now()
        )
        
        return jsonify(response.model_dump()), 200
    
    except ValidationError as e:
        return jsonify(ErrorResponse(
            ok=False,
            error={
                "code": "validation_error",
                "message": "Datos de entrada inválidos",
                "details": e.errors()
            }
        ).model_dump()), 400
    
    except Exception as e:
        return jsonify(ErrorResponse(
            ok=False,
            error={
                "code": "internal_error",
                "message": str(e)
            }
        ).model_dump()), 500


@planner_bp.get("/status/<plan_id>")
@auth_required
def get_plan_status(user_payload, plan_id: str):
    """
    GET /planner/status/<plan_id>
    
    Consulta el estado de ejecución de un plan.
    [PLACEHOLDER - Requiere implementación de tracking]
    
    Returns:
      - 200: PlanStatusResponse
      - 404: Plan no encontrado
      - 500: Error interno
    """
    try:
        # PLACEHOLDER: Consultar DB
        response = PlanStatusResponse(
            ok=True,
            plan_id=plan_id,
            status="PENDING_EXECUTION",
            item_id="MAT-001",
            quantity=100.0,
            algorithm_used="RESERVE_DYNAMIC",
            created_at=datetime.now(),
            completed_at=None,
            error_message=None
        )
        
        return jsonify(response.model_dump()), 200
    
    except Exception as e:
        return jsonify(ErrorResponse(
            ok=False,
            error={
                "code": "internal_error",
                "message": str(e)
            }
        ).model_dump()), 500


@planner_bp.get("/algorithms")
@auth_required
def get_available_algorithms(user_payload):
    """
    GET /planner/algorithms
    
    Lista todos los algoritmos disponibles en el sistema.
    
    Returns:
      - 200: Lista de algoritmos con nombres
      - 500: Error interno
    """
    try:
        service = get_planner_service()
        algorithms = service.get_available_algorithms()
        
        return jsonify({
            "ok": True,
            "algorithms": algorithms,
            "total": len(algorithms)
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": {
                "code": "internal_error",
                "message": str(e)
            }
        }), 500
