"""
Rutas REST API para Solicitudes y Materiales
Endpoints para gestión de solicitudes de materiales
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from middleware.auth import require_role, admin_required
from services.solicitud_service import SolicitudService, MaterialService
from schemas.solicitud_schema import (
    SolicitudCreate,
    SolicitudDraft,
    SolicitudUpdate,
    SolicitudResponse,
    SolicitudDetailResponse,
    SolicitudListResponse,
    AprobacionCreate,
    MaterialSearchQuery,
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialListResponse,
    ErrorResponse,
    SuccessResponse,
    SolicitudCreatedResponse,
)
from core.security import get_current_user_id

bp = Blueprint("solicitudes", __name__, url_prefix="/api")


# ==================== Solicitudes Endpoints ====================

@bp.route("/solicitudes", methods=["POST"])
@require_role("Solicitante", "Planificador", "Administrador")
def crear_solicitud():
    """
    POST /api/solicitudes
    Crea una nueva solicitud de materiales
    
    Request Body:
        SolicitudCreate schema
    
    Response:
        201: SolicitudCreatedResponse
        400: ErrorResponse (validación)
        401: ErrorResponse (no autenticado)
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify(ErrorResponse(
                error={"code": "UNAUTHORIZED", "message": "No autenticado"}
            ).model_dump()), 401
        
        # Validar request body
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error={"code": "INVALID_REQUEST", "message": "Request body requerido"}
            ).model_dump()), 400
        
        # Validar con Pydantic
        solicitud_data = SolicitudCreate(**data)
        
        # Crear solicitud
        solicitud = SolicitudService.create_solicitud(
            user_id=user_id,
            data=solicitud_data.model_dump()
        )
        
        # Response
        response = SolicitudCreatedResponse(
            solicitud=SolicitudDetailResponse.model_validate(solicitud.to_dict(include_items=True))
        )
        
        return jsonify(response.model_dump()), 201
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes/drafts", methods=["POST"])
@require_role("Solicitante", "Planificador", "Administrador")
def crear_borrador():
    """
    POST /api/solicitudes/drafts
    Crea un borrador de solicitud (sin items obligatorios)
    
    Request Body:
        SolicitudDraft schema
    
    Response:
        201: SolicitudCreatedResponse
        400: ErrorResponse
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify(ErrorResponse(
                error={"code": "UNAUTHORIZED", "message": "No autenticado"}
            ).model_dump()), 401
        
        data = request.get_json() or {}
        draft_data = SolicitudDraft(**data)
        
        solicitud = SolicitudService.create_draft(
            user_id=user_id,
            data=draft_data.model_dump()
        )
        
        response = SolicitudCreatedResponse(
            solicitud=SolicitudDetailResponse.model_validate(solicitud.to_dict(include_items=True))
        )
        
        return jsonify(response.model_dump()), 201
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes", methods=["GET"])
@require_role("Solicitante", "Planificador", "Administrador")
def listar_solicitudes():
    """
    GET /api/solicitudes?status=...&page=1&per_page=10
    Lista solicitudes del usuario (o todas si es admin/planificador)
    
    Query Params:
        status: Filtrar por estado (opcional)
        page: Página (default 1)
        per_page: Items por página (default 10)
    
    Response:
        200: SolicitudListResponse
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify(ErrorResponse(
                error={"code": "UNAUTHORIZED", "message": "No autenticado"}
            ).model_dump()), 401
        
        # Query params
        status = request.args.get("status")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        
        # Administradores y planificadores ven todas las solicitudes
        from models.user import User
        from core.db import get_db
        
        with get_db() as db:
            user = db.query(User).filter(User.username == user_id).first()
            if user and user.role in ["Administrador", "Planificador"]:
                filter_user_id = None  # Ver todas
            else:
                filter_user_id = user_id  # Solo las propias
        
        # Listar
        result = SolicitudService.list_solicitudes(
            user_id=filter_user_id,
            status=status,
            page=page,
            per_page=per_page,
        )
        
        # Serializar
        solicitudes_response = [
            SolicitudResponse.model_validate(sol.to_dict())
            for sol in result["solicitudes"]
        ]
        
        response = SolicitudListResponse(
            solicitudes=solicitudes_response,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes/<int:solicitud_id>", methods=["GET"])
@require_role("Solicitante", "Planificador", "Administrador")
def obtener_solicitud(solicitud_id: int):
    """
    GET /api/solicitudes/<id>
    Obtiene detalle de una solicitud con sus items
    
    Response:
        200: SolicitudDetailResponse
        404: ErrorResponse
    """
    try:
        solicitud = SolicitudService.get_solicitud_by_id(solicitud_id)
        
        if not solicitud:
            return jsonify(ErrorResponse(
                error={"code": "NOT_FOUND", "message": f"Solicitud {solicitud_id} no encontrada"}
            ).model_dump()), 404
        
        # Verificar permisos: solo el dueño, planificador o admin pueden ver
        user_id = get_current_user_id()
        from models.user import User
        from core.db import get_db
        
        with get_db() as db:
            user = db.query(User).filter(User.username == user_id).first()
            if user and user.role not in ["Administrador", "Planificador"]:
                if solicitud.id_usuario != user_id:
                    return jsonify(ErrorResponse(
                        error={"code": "FORBIDDEN", "message": "No tiene permisos para ver esta solicitud"}
                    ).model_dump()), 403
        
        response = SolicitudDetailResponse.model_validate(solicitud.to_dict(include_items=True))
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes/<int:solicitud_id>", methods=["PATCH"])
@require_role("Solicitante", "Planificador", "Administrador")
def actualizar_solicitud(solicitud_id: int):
    """
    PATCH /api/solicitudes/<id>
    Actualiza una solicitud existente
    
    Request Body:
        SolicitudUpdate schema
    
    Response:
        200: SolicitudDetailResponse
        400: ErrorResponse
        404: ErrorResponse
    """
    try:
        user_id = get_current_user_id()
        
        # Verificar que la solicitud existe y pertenece al usuario
        solicitud = SolicitudService.get_solicitud_by_id(solicitud_id)
        if not solicitud:
            return jsonify(ErrorResponse(
                error={"code": "NOT_FOUND", "message": f"Solicitud {solicitud_id} no encontrada"}
            ).model_dump()), 404
        
        # Solo el dueño puede actualizar (o admin)
        from models.user import User
        from core.db import get_db
        
        with get_db() as db:
            user = db.query(User).filter(User.username == user_id).first()
            if user and user.role != "Administrador":
                if solicitud.id_usuario != user_id:
                    return jsonify(ErrorResponse(
                        error={"code": "FORBIDDEN", "message": "No tiene permisos para modificar esta solicitud"}
                    ).model_dump()), 403
        
        # Validar request body
        data = request.get_json() or {}
        update_data = SolicitudUpdate(**data)
        
        # Actualizar
        solicitud_updated = SolicitudService.update_solicitud(
            solicitud_id=solicitud_id,
            data=update_data.model_dump(exclude_unset=True)
        )
        
        response = SolicitudDetailResponse.model_validate(solicitud_updated.to_dict(include_items=True))
        
        return jsonify(response.model_dump()), 200
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes/<int:solicitud_id>/aprobar", methods=["POST"])
@require_role("Planificador", "Administrador")
def aprobar_solicitud(solicitud_id: int):
    """
    POST /api/solicitudes/<id>/aprobar
    Aprueba una solicitud (solo planificador/admin)
    
    Request Body:
        AprobacionCreate schema (opcional)
    
    Response:
        200: SolicitudDetailResponse
        400: ErrorResponse
    """
    try:
        user_id = get_current_user_id()
        
        data = request.get_json() or {}
        aprobacion_data = AprobacionCreate(decision="aprobada", comentario=data.get("comentario"))
        
        solicitud = SolicitudService.aprobar_solicitud(
            solicitud_id=solicitud_id,
            aprobador_id=user_id,
            comentario=aprobacion_data.comentario,
        )
        
        response = SolicitudDetailResponse.model_validate(solicitud.to_dict(include_items=True))
        
        return jsonify(response.model_dump()), 200
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/solicitudes/<int:solicitud_id>/rechazar", methods=["POST"])
@require_role("Planificador", "Administrador")
def rechazar_solicitud(solicitud_id: int):
    """
    POST /api/solicitudes/<id>/rechazar
    Rechaza una solicitud (solo planificador/admin)
    
    Request Body:
        AprobacionCreate schema (opcional)
    
    Response:
        200: SolicitudDetailResponse
        400: ErrorResponse
    """
    try:
        user_id = get_current_user_id()
        
        data = request.get_json() or {}
        aprobacion_data = AprobacionCreate(decision="rechazada", comentario=data.get("comentario"))
        
        solicitud = SolicitudService.rechazar_solicitud(
            solicitud_id=solicitud_id,
            aprobador_id=user_id,
            comentario=aprobacion_data.comentario,
        )
        
        response = SolicitudDetailResponse.model_validate(solicitud.to_dict(include_items=True))
        
        return jsonify(response.model_dump()), 200
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


# ==================== Materiales Endpoints ====================

@bp.route("/materiales", methods=["GET"])
def buscar_materiales():
    """
    GET /api/materiales?q=...&codigo=...&limit=100
    Busca materiales en el catálogo
    
    Query Params:
        q: Búsqueda general
        codigo: Filtrar por código
        descripcion: Filtrar por descripción
        centro: Filtrar por centro
        sector: Filtrar por sector
        limit: Límite de resultados (default 100)
    
    Response:
        200: MaterialListResponse
    """
    try:
        # Validar query params
        query_params = MaterialSearchQuery(**request.args.to_dict())
        
        # Buscar
        materiales = MaterialService.search_materiales(
            q=query_params.q,
            codigo=query_params.codigo,
            descripcion=query_params.descripcion,
            centro=query_params.centro,
            sector=query_params.sector,
            limit=query_params.limit,
        )
        
        # Serializar
        materiales_response = [
            MaterialResponse.model_validate(m.to_dict())
            for m in materiales
        ]
        
        response = MaterialListResponse(
            materiales=materiales_response,
            total=len(materiales_response),
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/materiales/<string:codigo>", methods=["GET"])
def obtener_material(codigo: str):
    """
    GET /api/materiales/<codigo>
    Obtiene un material por código
    
    Response:
        200: MaterialResponse
        404: ErrorResponse
    """
    try:
        material = MaterialService.get_material_by_codigo(codigo)
        
        if not material:
            return jsonify(ErrorResponse(
                error={"code": "NOT_FOUND", "message": f"Material {codigo} no encontrado"}
            ).model_dump()), 404
        
        response = MaterialResponse.model_validate(material.to_dict())
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/materiales", methods=["POST"])
@admin_required
def crear_material():
    """
    POST /api/materiales
    Crea un nuevo material (solo admin)
    
    Request Body:
        MaterialCreate schema
    
    Response:
        201: MaterialResponse
        400: ErrorResponse
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(ErrorResponse(
                error={"code": "INVALID_REQUEST", "message": "Request body requerido"}
            ).model_dump()), 400
        
        material_data = MaterialCreate(**data)
        
        material = MaterialService.create_material(material_data.model_dump())
        
        response = MaterialResponse.model_validate(material.to_dict())
        
        return jsonify(response.model_dump()), 201
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500


@bp.route("/materiales/<string:codigo>", methods=["PUT"])
@admin_required
def actualizar_material(codigo: str):
    """
    PUT /api/materiales/<codigo>
    Actualiza un material existente (solo admin)
    
    Request Body:
        MaterialUpdate schema
    
    Response:
        200: MaterialResponse
        400: ErrorResponse
        404: ErrorResponse
    """
    try:
        data = request.get_json() or {}
        update_data = MaterialUpdate(**data)
        
        material = MaterialService.update_material(
            codigo=codigo,
            data=update_data.model_dump(exclude_unset=True)
        )
        
        response = MaterialResponse.model_validate(material.to_dict())
        
        return jsonify(response.model_dump()), 200
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": str(e)}
        ).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        ).model_dump()), 500
