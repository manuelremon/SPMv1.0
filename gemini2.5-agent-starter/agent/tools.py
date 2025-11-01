from __future__ import annotations
from pathlib import Path
import subprocess
import json
import os

ROOT = Path.cwd()

def _safe(path: str) -> Path:
    p = (ROOT / path).resolve()
    if ROOT not in p.parents and p != ROOT:
        raise ValueError("path fuera de raíz")
    return p

def read_file(path: str) -> dict:
    p = _safe(path)
    if not p.exists():
        return {"ok": False, "error": "no existe", "path": path}
    return {"ok": True, "text": p.read_text(encoding="utf-8"), "path": path}

def write_file(path: str, text: str) -> dict:
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return {"ok": True, "bytes": len(text), "path": path}

def run_tests(cmd: str = "pytest -q") -> dict:
    try:
        out = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=180)
        return {
            "ok": out.returncode == 0,
            "returncode": out.returncode,
            "stdout": out.stdout[-10000:],
            "stderr": out.stderr[-10000:],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def tool_declarations():
    # JSON Schema compatible con Google GenAI function calling
    return [
        {
            "name": "read_file",
            "description": "Lee un archivo de texto relativo a la raíz del repo",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": "Escribe un archivo de texto relativo a la raíz del repo",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "text": {"type": "string"}},
                "required": ["path", "text"],
            },
        },
        {
            "name": "run_tests",
            "description": "Ejecuta tests en shell y devuelve salida",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}},
            },
        },
    ]

def handle_tool_call(function_call) -> dict:
    name = function_call.name
    args = dict(function_call.args or {})
    if name == "read_file":
        res = read_file(**args)
    elif name == "write_file":
        res = write_file(**args)
    elif name == "run_tests":
        res = run_tests(**args)
    else:
        res = {"ok": False, "error": f"función no soportada: {name}"}
    return {"name": name, "response": res}
