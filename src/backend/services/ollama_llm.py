"""
Ollama LLM Integration for Form Intelligence
Supports multiple models: mistral, neural-chat, openchat, etc.
"""
import requests
import json
from typing import Optional, Dict
from datetime import datetime

class OllamaLLM:
    """Interface to Ollama local LLM"""
    
    # Recommended models:
    # - mistral: Fast, good for business logic (recommended)
    # - neural-chat: Good balance of speed and quality
    # - openchat: Similar to ChatGPT, slower
    # - orca-mini: Compact, fast
    
    DEFAULT_MODEL = "mistral"
    DEFAULT_BASE_URL = "http://127.0.0.1:11434"
    
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/generate"
        self._check_health()
    
    def _check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            print(f"⚠️ Ollama not available at {self.base_url}")
            return False
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name', '').split(':')[0] for m in data.get('models', [])]
                return self.model in models or any(self.model in m for m in models)
            return False
        except:
            return False
    
    def generate(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate response from Ollama"""
        
        # Build context-aware prompt
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            response = requests.post(
                self.endpoint,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '').strip()
            else:
                return f"Error: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "⏱️ Request timeout. Ollama might be busy."
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Is it running on port 11434?"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _build_prompt(self, user_prompt: str, context: Optional[Dict] = None) -> str:
        """Build a context-aware prompt for the LLM"""
        
        system_prompt = """Eres un asistente experto en planificación de materiales y logística.
Eres muy conciso, práctico y orientado a datos.
Responde en español.
Siempre base tu análisis en los datos proporcionados.
Si no hay datos suficientes, di claramente qué información falta."""
        
        prompt_parts = [system_prompt]
        
        # Add context if available
        if context:
            if "material_codigo" in context and context["material_codigo"]:
                prompt_parts.append(f"\nMaterial: {context['material_codigo']}")
            
            if "stock_info" in context:
                stock = context["stock_info"]
                prompt_parts.append(f"\n📦 Stock disponible: {stock.get('cantidad_disponible', 0)}")
                prompt_parts.append(f"   Reservado: {stock.get('cantidad_reservada', 0)}")
                prompt_parts.append(f"   Libre: {stock.get('cantidad_libre', 0)}")
                prompt_parts.append(f"   Punto de reorden: {stock.get('punto_reorden', 0)}")
            
            if "mrp_info" in context:
                mrp = context["mrp_info"]
                prompt_parts.append(f"\n📊 Demanda próximas semanas: {mrp.get('demanda_semana1', 0)}, {mrp.get('demanda_semana2', 0)}")
                prompt_parts.append(f"   Stock proyectado: {mrp.get('stock_proyectado', 0)}")
                prompt_parts.append(f"   Lead time: {mrp.get('lead_time_dias', 0)} días")
            
            if "consumption_history" in context:
                avg_consumption = context["consumption_history"].get("promedio_90_dias", 0)
                prompt_parts.append(f"\n📈 Consumo promedio (90 días): {avg_consumption}")
            
            if "pending_requests" in context:
                prompt_parts.append(f"\n📋 Solicitudes pendientes: {len(context['pending_requests'])}")
            
            if "user_info" in context:
                user = context["user_info"]
                prompt_parts.append(f"\n👤 Usuario: {user.get('centro', 'N/A')}")
        
        prompt_parts.append(f"\n\nPregunta del usuario: {user_prompt}")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def get_available_models() -> list:
        """Get list of available models in Ollama"""
        try:
            response = requests.get(
                f"{OllamaLLM.DEFAULT_BASE_URL}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name', '') for m in data.get('models', [])]
                return models
        except:
            pass
        return []


class OllamaHelper:
    """Helper for Ollama operations"""
    
    @staticmethod
    def setup_instructions() -> str:
        """Return setup instructions for Ollama"""
        return """
## 🚀 Setup Ollama

1. **Descargar Ollama:**
   https://ollama.ai (Windows, Mac, Linux)

2. **Instalar modelo recomendado (Mistral):**
   ```
   ollama pull mistral
   ```

3. **Alternativas:**
   - `ollama pull neural-chat` (equilibrio)
   - `ollama pull openchat` (ChatGPT-like)
   - `ollama pull orca-mini` (muy rápido)

4. **Correr Ollama:**
   ```
   ollama serve
   ```
   (Escucha en http://127.0.0.1:11434)

5. **Verificar modelos instalados:**
   ```
   ollama list
   ```

6. **Probar desde Python:**
   ```python
   from src.backend.services.ollama_llm import OllamaLLM
   llm = OllamaLLM("mistral")
   print(llm.generate("¿Cuál es 2+2?"))
   ```
"""


if __name__ == "__main__":
    print(OllamaHelper.setup_instructions())
    
    # Test connection
    llm = OllamaLLM("mistral")
    if llm.is_available():
        print("✅ Ollama connection OK")
        response = llm.generate("¿Qué es la planificación de materiales?")
        print(f"Response: {response}")
    else:
        print("❌ Ollama not available. Follow setup instructions above.")
