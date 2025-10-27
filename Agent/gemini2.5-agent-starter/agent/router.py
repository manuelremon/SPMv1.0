def pick_model(task: str) -> str:
    low = ("resumen", "resume", "renombra", "rename", "buscar", "extrae", "formatea", "typo", "corrige typo")
    t = (task or "").lower()
    return "gemini-2.5-flash" if any(k in t for k in low) else "gemini-2.5-pro"
