#!/usr/bin/env python3
"""
Test para verificar que el backend acepta tanto JSON como FormData
"""

import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

# Login
print("=== Test FormData vs JSON ===\n")
print("1. Login con JSON...")
response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "usuario@spm.com", "password": "user123"},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    cookies = response.cookies
    print("[OK] Login exitoso\n")
else:
    print(f"[ERROR] Login fallido: {response.status_code}")
    exit(1)

# Test 1: Crear solicitud con JSON (como antes)
print("2. Crear solicitud con JSON (Content-Type: application/json)...")
json_payload = {
    "centro": "1008",
    "sector": "Mantenimiento",
    "justificacion": "Test con JSON",
    "almacen_virtual": "ALM0001",
    "centro_costos": "CC001",
    "criticidad": "Normal",
    "fecha_necesidad": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
    "items": [
        {
            "codigo": "1000000001",
            "descripcion": "TUERCA M8",
            "cantidad": 5,
            "precio_unitario": 12.50
        }
    ]
}

response_json = requests.post(
    f"{API_BASE}/solicitudes",
    json=json_payload,
    cookies=cookies,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response_json.status_code}")
print(f"Response: {response_json.json()}")

if response_json.status_code == 200:
    print("[OK] Solicitud JSON creada exitosamente\n")
else:
    print(f"[ERROR] Fallo creacion con JSON\n")

# Test 2: Crear solicitud con FormData
print("3. Crear solicitud con FormData (como lo hace el frontend)...")
import json

formdata_payload = {
    "centro": "1008",
    "sector": "Mantenimiento",
    "justificacion": "Test con FormData",
    "almacen": "ALM0001",  # <- Nombre de campo diferente!
    "centroCostos": "CC001",  # <- Nombre de campo diferente!
    "criticidad": "Alta",  # <- Valor diferente!
    "fechaNecesaria": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),  # <- Nombre diferente!
    "items": json.dumps([  # <- FormData envia items como string JSON
        {
            "codigo": "1000000002",
            "descripcion": "TUERCA M10",
            "cantidad": 3,
            "precio_unitario": 15.00
        }
    ])
}

response_formdata = requests.post(
    f"{API_BASE}/solicitudes",
    data=formdata_payload,  # <- Nota: 'data' en lugar de 'json'
    cookies=cookies,
    # Sin Content-Type, requests envia como multipart/form-data automaticamente
)

print(f"Status: {response_formdata.status_code}")
print(f"Response: {response_formdata.json()}")

if response_formdata.status_code == 200:
    print("[OK] Solicitud FormData creada exitosamente\n")
else:
    print(f"[ERROR] Fallo creacion con FormData\n")

print("=== Resumen ===")
print(f"JSON:     {'OK' if response_json.status_code == 200 else 'FAIL'}")
print(f"FormData: {'OK' if response_formdata.status_code == 200 else 'FAIL'}")
