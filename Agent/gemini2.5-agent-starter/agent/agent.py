from __future__ import annotations
from google import genai
from google.genai import types
from .tools import tool_declarations, handle_tool_call
from .router import pick_model

SYSTEM_PROMPT = (
    "Eres un agente senior de refactor y pruebas. "
    "Siempre propones un plan, haces cambios mínimos, ejecutas tests y reportas diff. "
    "Si falta contexto, pides leer archivos específicos. "
    "Nunca inventes rutas; pide confirmación si no existen."
)

def call_agent(user_task: str, history: list | None = None, budget: int | None = -1):
    client = genai.Client()  # toma API key de env GEMINI_API_KEY o parámetro
    history = history or []
    model = pick_model(user_task)

    # Declaración de herramientas
    tools = types.Tool(function_declarations=tool_declarations())

    # Config base
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tools],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        ),
    )

    # Añadir thinking si el SDK lo soporta (algunos releases usan .thinking, otros .thinking_config)
    try:
        cfg.thinking = types.ThinkingConfig(budget_tokens=budget)
    except Exception:
        try:
            cfg.thinking_config = types.ThinkingConfig(thinking_budget=budget)  # compat
        except Exception:
            pass

    contents = [*history, types.Content(role="user", parts=[types.Part.from_text(user_task)])]

    while True:
        resp = client.models.generate_content(model=model, contents=contents, config=cfg)

        cand = resp.candidates[0]
        parts = cand.content.parts

        # ¿Solicitó llamadas a funciones?
        tool_calls = [p.function_call for p in parts if getattr(p, "function_call", None)]
        if tool_calls:
            # agregar el turno del modelo
            contents.append(cand.content)
            # ejecutar herramientas y devolver al modelo
            fr_parts = []
            for tc in tool_calls:
                fr = handle_tool_call(tc)
                fr_parts.append(types.Part.from_function_response(fr))
            contents.append(types.Content(role="user", parts=fr_parts))
            # continuar iteración
            continue

        # Respuesta final
        return {
            "model": model,
            "text": resp.text,
            "usage": {
                "input_tokens": getattr(resp, "usage_metadata", None) and getattr(resp.usage_metadata, "prompt_token_count", None),
                "output_tokens": getattr(resp, "usage_metadata", None) and getattr(resp.usage_metadata, "candidates_token_count", None),
                "thinking_tokens": getattr(resp, "usage_metadata", None) and getattr(resp.usage_metadata, "thoughts_token_count", None),
            },
        }
