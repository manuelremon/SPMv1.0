# Gemini 2.5 Pro Agent Starter (Windows + VS Code)

## Requisitos
- Python 3.10+
- PowerShell o CMD
- Clave de API: GEMINI_API_KEY

## Instalación rápida
```powershell
py -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
setx GEMINI_API_KEY "TU_CLAVE_AQUI"   # persistente (cierra y abre terminal)
# o solo para la sesión:
$env:GEMINI_API_KEY="TU_CLAVE_AQUI"
python .\scripts\run_agent.py -t "Abre tests, corrige fallas en targets/example.py y ejecuta pytest"
```

## Estructura
```
agent/
  agent.py         # loop ReAct + function calling
  tools.py         # funciones: read_file, write_file, run_tests
  router.py        # selección Pro/Flash por tarea
scripts/
  run_agent.py     # CLI
tests/
  test_example.py  # prueba simple
targets/
  example.py       # código con bug a corregir
requirements.txt
README.md
```

## Notas
- El agente usa Function Calling y un bucle acción-observación.
- `thinking` es opcional. Si tu SDK soporta `ThinkingConfig`, se usará.
- Ajusta `--budget` para latencia/calidad. Usa Flash para tareas triviales.
