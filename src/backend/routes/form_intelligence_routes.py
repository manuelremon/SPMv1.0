"""
API Routes para Form Intelligence.

Endpoints:
- POST /api/form-intelligence/analyze - Análisis completo de material
- POST /api/form-intelligence/suggest - Sugerencias para campo
- POST /api/form-intelligence/chat - Chat IA contextual
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import json

bp = Blueprint("form_intelligence", __name__, url_prefix="/api/form-intelligence")


def get_form_intelligence():
    """Lazy import para evitar circular dependencies."""
    from src.backend.services.form_intelligence import get_form_intelligence_engine
    return get_form_intelligence_engine()


@bp.route("/analyze", methods=["POST"])
def analyze_material():
    """
    Análisis completo de un material.
    
    Request body:
    {
        "material_codigo": "MAT001",
        "cantidad": 100,
        "centro": "C001",  # opcional
        "almacen": "ALM01"  # opcional
    }
    """
    try:
        data = request.get_json() or {}
        material_codigo = data.get("material_codigo", "").strip()
        cantidad = float(data.get("cantidad", 0))
        centro = data.get("centro")
        almacen = data.get("almacen")

        if not material_codigo:
            return jsonify({"error": "material_codigo requerido"}), 400

        engine = get_form_intelligence()
        analysis = engine.analyze_material(
            material_codigo, cantidad, centro, almacen
        )

        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({"error": f"Valor inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/suggest", methods=["POST"])
def suggest_for_field():
    """
    Sugerencias para un campo específico durante rellenado del formulario.
    
    Request body:
    {
        "field_type": "material_search",  # material_search, cantidad, centro, etc
        "query": "acero",
        "centro": "C001",
        "limit": 10
    }
    """
    try:
        data = request.get_json() or {}
        field_type = data.get("field_type", "").strip()
        query = data.get("query", "").strip()
        centro = data.get("centro")
        limit = int(data.get("limit", 10))

        if field_type == "material_search":
            return _suggest_materials(query, centro, limit)
        elif field_type == "cantidad":
            return _suggest_cantidad(data)
        elif field_type == "centro":
            return _suggest_centro(query, limit)
        else:
            return jsonify({"error": f"field_type no soportado: {field_type}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _suggest_materials(query: str, centro: str = None, limit: int = 10) -> tuple:
    """Sugiere materiales basado en búsqueda."""
    try:
        from src.backend.core.db import get_connection

        con = get_connection()
        sql = """
            SELECT 
                codigo,
                descripcion,
                descripcion_larga,
                unidad,
                precio_usd
            FROM materiales
            WHERE (LOWER(codigo) LIKE ? 
                   OR LOWER(descripcion) LIKE ?
                   OR LOWER(descripcion_larga) LIKE ?)
                AND activo = 1
            LIMIT ?
        """
        query_param = f"%{query.lower()}%"
        rows = con.execute(sql, (query_param, query_param, query_param, limit)).fetchall()

        suggestions = [
            {
                "codigo": row[0],
                "descripcion": row[1],
                "descripcion_larga": row[2],
                "unidad": row[3],
                "precio_usd": row[4],
            }
            for row in rows
        ]

        return jsonify({"suggestions": suggestions, "count": len(suggestions)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _suggest_cantidad(data: Dict[str, Any]) -> tuple:
    """Sugiere cantidad basado en consumo histórico."""
    try:
        material_codigo = data.get("material_codigo", "").strip()
        centro = data.get("centro")

        if not material_codigo:
            return jsonify({"error": "material_codigo requerido"}), 400

        engine = get_form_intelligence()
        analysis = engine.analyze_material(material_codigo, 0, centro)

        consumo = analysis.get("consumo_historico", {})
        avg_qty = consumo.get("consumo_promedio", 0)
        total_qty = consumo.get("consumo_total", 0)

        suggestions = {
            "consumo_promedio_un": avg_qty,
            "consumo_mensual_estimado": avg_qty * 30,
            "cantidad_sugerida": max(avg_qty * 30, 50),  # Al menos 50 UN
            "fundamento": "Basado en consumo de últimos 90 días",
        }

        return jsonify(suggestions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _suggest_centro(query: str, limit: int = 10) -> tuple:
    """Sugiere centros."""
    try:
        from src.backend.core.db import get_connection

        con = get_connection()
        sql = """
            SELECT codigo, nombre
            FROM catalog_centros
            WHERE (LOWER(codigo) LIKE ? OR LOWER(nombre) LIKE ?)
                AND activo = 1
            LIMIT ?
        """
        query_param = f"%{query.lower()}%"
        rows = con.execute(sql, (query_param, query_param, limit)).fetchall()

        suggestions = [{"codigo": row[0], "nombre": row[1]} for row in rows]

        return jsonify({"suggestions": suggestions, "count": len(suggestions)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/chat", methods=["POST"])
def chat_with_ai():
    """
    Chat contextual con IA sobre materiales y formularios.
    
    Request body:
    {
        "message": "¿Cuál es el consumo promedio de este material?",
        "material_codigo": "MAT001",
        "centro": "C001",
        "context": {...}  # contexto del formulario actual
    }
    """
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        material_codigo = data.get("material_codigo", "").strip()
        centro = data.get("centro", "").strip() if data.get("centro") else None

        if not message:
            return jsonify({"error": "message requerido"}), 400

        try:
            engine = get_form_intelligence()

            # Preparar contexto si hay material
            context = ""
            if material_codigo:
                try:
                    context = engine.get_chat_context(material_codigo)
                except Exception as e:
                    print(f"Error getting chat context: {e}")
                    context = ""

            # Simular respuesta IA (en producción: usar LLM real)
            response = _generate_ai_response(message, material_codigo, centro, context)

            return (
                jsonify(
                    {
                        "message": message,
                        "response": response,
                        "context_used": bool(context),
                    }
                ),
                200,
            )
        except Exception as e:
            print(f"Error in chat logic: {e}")
            raise

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def _generate_ai_response(
    message: str, material_codigo: str = "", centro: str = "", context: str = ""
) -> str:
    """
    Genera respuesta IA contextual.
    
    En producción, esto llamaría a LLM real (Ollama, OpenAI, etc).
    """
    # Rutas inteligentes de respuesta
    msg_lower = message.lower()
    material_text = material_codigo if material_codigo else "el material"

    if "consumo" in msg_lower:
        return f"El consumo histórico de {material_text} en los últimos 90 días está disponible en los datos contextuales. Puedo hacer análisis de tendencias si lo necesitas."

    elif "stock" in msg_lower:
        return f"El estado actual del stock para {material_text} está siendo consultado. Tenemos información de disponibilidad por almacén."

    elif "alternativa" in msg_lower or "equivalente" in msg_lower:
        return f"Hay materiales alternativos disponibles para {material_text} con especificación técnica compatible."

    elif "cantidad" in msg_lower or "cuánto" in msg_lower:
        return f"Basado en el consumo histórico, una cantidad sugerida sería calculada automáticamente. ¿Necesitas el consumo promedio mensual?"

    elif "mrp" in msg_lower or "planificación" in msg_lower:
        return f"El estado MRP de {material_text} está siendo monitoreado. Tenemos información sobre punto de pedido y stock máximo."

    elif "solicitud" in msg_lower or "duplicado" in msg_lower:
        return f"Verificando solicitudes en curso para {material_text}... Podemos evitar duplicados."

    else:
        return f"Entendido tu pregunta sobre {material_text}. Estoy analizando los datos contextuales. ¿Puedes ser más específico? Puedo ayudarte con: consumo, stock, alternativas, cantidades, estado MRP, o solicitudes en curso."


@bp.route("/status", methods=["GET"])
def form_intelligence_status():
    """Estado del servicio de inteligencia."""
    try:
        return (
            jsonify(
                {
                    "status": "operacional",
                    "version": "1.0",
                    "features": [
                        "analizar_material",
                        "sugerencias_campo",
                        "chat_contextual",
                        "validacion_inteligente",
                        "prediccion_siguiente_paso",
                    ],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
