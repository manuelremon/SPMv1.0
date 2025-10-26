"""
FormIntelligence Service v2 - Enhanced with Ollama, Excel Data, Auth, History
"""

import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
from ..core.db import get_connection
from ..services.data_providers import ExcelDataProvider
from ..services.ollama_llm import OllamaLLM


class FormIntelligenceEngineV2:
    """Enhanced Form Intelligence Engine with LLM, Excel data, auth, and history"""
    
    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.llm = None
        self.conversation_history = {}  # Per user
        
        if use_ollama:
            self.llm = OllamaLLM("mistral")
            if not self.llm.is_available():
                print("⚠️ Ollama not available - will use templates")
                self.use_ollama = False
    
    def chat_with_context(
        self,
        user_id: str,
        message: str,
        material_codigo: Optional[str] = None,
        centro: Optional[str] = None,
        context_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Chat endpoint with full context awareness and history
        
        Args:
            user_id: JWT user identifier
            message: User message
            material_codigo: Current material (if selected)
            centro: User's center
            context_data: Additional form context
        
        Returns:
            Dict with response, context_used, suggestions, etc.
        """
        
        # Initialize user history if needed
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build rich context
        context = self._build_context(material_codigo, centro, context_data)
        
        # Generate response
        if self.use_ollama and self.llm.is_available():
            response = self.llm.generate(message, context=context)
        else:
            response = self._generate_template_response(message, context)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(message, context)
        
        # Store in history
        self.conversation_history[user_id].append({
            "role": "assistant",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "context_used": bool(context),
            "suggestions": suggestions,
            "material_codigo": material_codigo,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for user (last N messages)"""
        if user_id not in self.conversation_history:
            return []
        
        history = self.conversation_history[user_id]
        return history[-limit:] if history else []
    
    def clear_conversation_history(self, user_id: str) -> bool:
        """Clear conversation history for user"""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
            return True
        return False
    
    def _build_context(
        self,
        material_codigo: Optional[str],
        centro: Optional[str],
        additional_context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI"""
        
        context = {
            "material_codigo": material_codigo,
            "centro": centro,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get stock data from Excel
        if material_codigo:
            stock = ExcelDataProvider.load_stock(material_codigo)
            context["stock_info"] = stock
            
            # Get MRP data
            mrp = ExcelDataProvider.load_mrp(material_codigo)
            context["mrp_info"] = mrp
            
            # Get consumption history
            consumption = ExcelDataProvider.load_consumption_history(material_codigo)
            if consumption:
                quantities = [c.get("cantidad_consumida", 0) for c in consumption]
                context["consumption_history"] = {
                    "promedio_90_dias": sum(quantities) / len(quantities) if quantities else 0,
                    "total_records": len(consumption)
                }
        
        # Merge with additional context
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def _generate_suggestions(self, message: str, context: Dict) -> List[str]:
        """Generate contextual suggestions"""
        
        suggestions = []
        message_lower = message.lower()
        
        # Smart suggestion based on message intent
        if "consumo" in message_lower or "histórico" in message_lower:
            if context.get("consumption_history"):
                avg = context["consumption_history"].get("promedio_90_dias", 0)
                suggestions.append(f"💡 Consumo promedio: {avg:.2f} unidades/día")
        
        if "stock" in message_lower:
            if context.get("stock_info"):
                stock = context["stock_info"]
                if stock.get("cantidad_libre", 0) < stock.get("punto_reorden", 0):
                    suggestions.append("⚠️ Stock por debajo del punto de reorden")
                else:
                    suggestions.append("✅ Stock en niveles adecuados")
        
        if "mrp" in message_lower or "pedido" in message_lower:
            if context.get("mrp_info"):
                mrp = context["mrp_info"]
                if mrp.get("necesidad_produccion", 0) > 0:
                    suggestions.append(f"📦 Necesidad: {mrp['necesidad_produccion']} unidades")
        
        # Add quick actions
        if context.get("material_codigo"):
            suggestions.append("📊 Ver análisis completo")
            suggestions.append("📋 Ver historial")
        
        return suggestions[:3]  # Max 3 suggestions
    
    def _generate_template_response(self, message: str, context: Dict) -> str:
        """Fallback template-based response when Ollama unavailable"""
        
        message_lower = message.lower()
        material = context.get("material_codigo", "sin especificar")
        centro = context.get("centro", "sin especificar")
        
        # Consumption queries
        if "consumo" in message_lower:
            if context.get("consumption_history"):
                avg = context["consumption_history"]["promedio_90_dias"]
                total = context["consumption_history"]["total_records"]
                return f"📈 El material {material} ha consumido un promedio de {avg:.2f} unidades/día en los últimos 90 días ({total} registros)."
            return f"No hay datos de consumo para {material}."
        
        # Stock queries
        if "stock" in message_lower:
            if context.get("stock_info"):
                stock = context["stock_info"]
                return f"📦 {material}: {stock.get('cantidad_libre', 0)} unidades libres. Punto reorden: {stock.get('punto_reorden', 0)}."
            return f"No hay datos de stock para {material}."
        
        # MRP queries
        if "mrp" in message_lower or "pedido" in message_lower:
            if context.get("mrp_info"):
                mrp = context["mrp_info"]
                need = mrp.get("necesidad_produccion", 0)
                if need > 0:
                    return f"📊 Se recomienda ordenar {need} unidades. Lead time: {mrp.get('lead_time_dias', 0)} días."
                return "✅ No hay necesidad de producción en el corto plazo."
            return "No hay datos de MRP."
        
        # Default response
        return f"Analizando {material} en {centro}. ¿Puedes ser más específico sobre qué información necesitas?"
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "ollama_available": self.use_ollama and (self.llm.is_available() if self.llm else False),
            "excel_stock": ExcelDataProvider.file_exists(ExcelDataProvider.STOCK_FILE),
            "excel_mrp": ExcelDataProvider.file_exists(ExcelDataProvider.MRP_FILE),
            "active_conversations": len(self.conversation_history),
            "timestamp": datetime.now().isoformat()
        }


# Global singleton instance
_instance: Optional[FormIntelligenceEngineV2] = None

def get_form_intelligence_engine() -> FormIntelligenceEngineV2:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = FormIntelligenceEngineV2(use_ollama=True)
    return _instance
