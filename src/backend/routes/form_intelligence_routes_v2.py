"""
Form Intelligence Routes v2 - With Ollama, Excel, Auth, and History
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any, Tuple
import json
import jwt
from datetime import datetime

bp = Blueprint("form_intelligence_v2", __name__, url_prefix="/api/form-intelligence")


def get_form_intelligence():
    """Get FormIntelligence engine v2"""
    from src.backend.services.form_intelligence_v2 import get_form_intelligence_engine
    return get_form_intelligence_engine()


def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Try to get user from JWT token
        try:
            from src.backend.core.config import Settings
            token = None
            
            # Try Authorization header
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            # Try cookies (for browser requests)
            if not token:
                token = request.cookies.get('auth_token')
            
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            # Decode JWT
            payload = jwt.decode(
                token,
                Settings.JWT_SECRET,
                algorithms=["HS256"]
            )
            
            # Attach user info to request
            request.user_id = payload.get('sub')
            request.user_info = {
                "id": payload.get('sub'),
                "centro": payload.get('centro'),
                "role": payload.get('role')
            }
            
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            # If JWT parsing fails, use anonymous ID
            request.user_id = "anonymous"
            request.user_info = {"id": "anonymous"}
        
        return f(*args, **kwargs)
    
    return decorated


@bp.route("/chat", methods=["POST"])
@require_auth
def chat_with_ai() -> Tuple[Dict[str, Any], int]:
    """
    Enhanced chat endpoint with context, history, and Ollama
    
    Request:
    {
        "message": "¿Cuál es el consumo histórico?",
        "material_codigo": "MAT-001",  # optional
        "centro": "CC-10",  # optional
        "context": { ... }  # optional additional context
    }
    
    Response:
    {
        "response": "...",
        "context_used": true,
        "suggestions": [...],
        "conversation_history": [...],
        "timestamp": "..."
    }
    """
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        
        if not message:
            return jsonify({"error": "message required"}), 400
        
        material_codigo = data.get("material_codigo")
        centro = data.get("centro", request.user_info.get("centro"))
        context = data.get("context", {})
        
        # Get engine
        engine = get_form_intelligence()
        
        # Chat with context
        result = engine.chat_with_context(
            user_id=request.user_id,
            message=message,
            material_codigo=material_codigo,
            centro=centro,
            context_data=context
        )
        
        # Add conversation history
        result["conversation_history"] = engine.get_conversation_history(request.user_id, limit=5)
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/analyze", methods=["POST"])
@require_auth
def analyze_material() -> Tuple[Dict[str, Any], int]:
    """
    Complete material analysis with all available data
    
    Request:
    {
        "material_codigo": "MAT-001",
        "centro": "CC-10",  # optional
        "cantidad": 100  # optional
    }
    """
    try:
        data = request.get_json() or {}
        material_codigo = data.get("material_codigo", "").strip()
        
        if not material_codigo:
            return jsonify({"error": "material_codigo required"}), 400
        
        from src.backend.services.data_providers import ExcelDataProvider
        
        # Load all data from Excel
        stock = ExcelDataProvider.load_stock(material_codigo)
        mrp = ExcelDataProvider.load_mrp(material_codigo)
        consumption = ExcelDataProvider.load_consumption_history(material_codigo)
        
        # Calculate statistics
        quantities = [c.get("cantidad_consumida", 0) for c in consumption] if consumption else []
        
        analysis = {
            "material_codigo": material_codigo,
            "stock": stock,
            "mrp": mrp,
            "consumption": {
                "records": len(consumption),
                "promedio_90_dias": sum(quantities) / len(quantities) if quantities else 0,
                "maximo": max(quantities) if quantities else 0,
                "minimo": min(quantities) if quantities else 0
            },
            "analysis_date": datetime.now().isoformat(),
            "user_id": request.user_id
        }
        
        return jsonify(analysis), 200
    
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/suggest", methods=["POST"])
@require_auth
def suggest_field() -> Tuple[Dict[str, Any], int]:
    """
    Get field-specific suggestions
    
    Request:
    {
        "field": "cantidad",
        "material_codigo": "MAT-001",
        "current_value": "100"
    }
    """
    try:
        data = request.get_json() or {}
        field = data.get("field", "").strip()
        material_codigo = data.get("material_codigo")
        
        if not field:
            return jsonify({"error": "field required"}), 400
        
        from src.backend.services.data_providers import ExcelDataProvider
        
        suggestions = []
        
        if field == "cantidad" and material_codigo:
            stock = ExcelDataProvider.load_stock(material_codigo)
            suggestions.append({
                "type": "info",
                "text": f"Stock disponible: {stock.get('cantidad_libre', 0)} unidades"
            })
        
        elif field == "material_codigo":
            # Suggest based on user's center
            suggestions.append({
                "type": "info",
                "text": "Selecciona de los 44,461 materiales disponibles"
            })
        
        return jsonify({
            "field": field,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        print(f"Suggest error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/status", methods=["GET"])
def get_status() -> Tuple[Dict[str, Any], int]:
    """Get service status (no auth required for monitoring)"""
    try:
        engine = get_form_intelligence()
        status = engine.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/history/<string:user_id>", methods=["GET"])
@require_auth
def get_history(user_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get conversation history for user
    Only users can see their own history
    """
    try:
        # Security: only allow users to see their own history
        if request.user_id != user_id and request.user_info.get("role") != "admin":
            return jsonify({"error": "Forbidden"}), 403
        
        engine = get_form_intelligence()
        limit = request.args.get("limit", default=20, type=int)
        
        history = engine.get_conversation_history(user_id, limit=limit)
        
        return jsonify({
            "user_id": user_id,
            "messages": history,
            "count": len(history)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/history/<string:user_id>", methods=["DELETE"])
@require_auth
def clear_history(user_id: str) -> Tuple[Dict[str, Any], int]:
    """Clear conversation history for user"""
    try:
        # Security: only allow users to clear their own history
        if request.user_id != user_id and request.user_info.get("role") != "admin":
            return jsonify({"error": "Forbidden"}), 403
        
        engine = get_form_intelligence()
        success = engine.clear_conversation_history(user_id)
        
        return jsonify({
            "success": success,
            "message": "History cleared" if success else "No history to clear"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/setup/excel", methods=["POST"])
def setup_excel() -> Tuple[Dict[str, Any], int]:
    """
    Setup: Create sample Excel files for development
    This is a development endpoint - should be protected in production
    """
    try:
        from src.backend.services.data_providers import create_sample_excel_files
        create_sample_excel_files()
        
        from src.backend.services.data_providers import ExcelDataProvider
        
        return jsonify({
            "success": True,
            "message": "Sample Excel files created",
            "stock_file": ExcelDataProvider.STOCK_FILE,
            "mrp_file": ExcelDataProvider.MRP_FILE,
            "location": "data/"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/setup/ollama", methods=["GET"])
def get_ollama_setup() -> Tuple[Dict[str, Any], int]:
    """Get Ollama setup instructions"""
    try:
        from src.backend.services.ollama_llm import OllamaHelper
        
        return jsonify({
            "instructions": OllamaHelper.setup_instructions(),
            "recommended_model": "mistral",
            "base_url": "http://127.0.0.1:11434"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
