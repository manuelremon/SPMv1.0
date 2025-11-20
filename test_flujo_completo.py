#!/usr/bin/env python3
"""
Script para probar el flujo completo de una solicitud en SPM v1.0
Desde login hasta aprobación/rechazo
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

# Usuarios de prueba
USUARIO_SOLICITANTE = {
    "username": "usuario@spm.com",
    "password": "user123"
}

USUARIO_COORDINADOR = {
    "username": "coordinador@spm.com",
    "password": "coord123"
}

USUARIO_ADMIN = {
    "username": "admin@spm.com",
    "password": "admin123"
}

def print_section(title):
    """Imprime una sección visual"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_success(message):
    """Imprime mensaje de exito"""
    print(f"[OK] {message}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"[ERROR] {message}")

def print_info(message):
    """Imprime informacion"""
    print(f"[INFO] {message}")

# =============================================================================
# PASO 1: LOGIN COMO USUARIO SOLICITANTE
# =============================================================================

def test_login(credentials, nombre="Usuario"):
    """Prueba el login y retorna las cookies de sesión"""
    print_section(f"PASO: Login como {nombre}")

    response = requests.post(
        f"{API_BASE}/auth/login",
        json=credentials,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            user = data.get("user", {})
            print_success(f"Login exitoso como {user.get('nombre')} {user.get('apellido')}")
            print_info(f"  - Rol: {user.get('rol')}")
            print_info(f"  - Email: {user.get('mail')}")
            print_info(f"  - ID: {user.get('id_spm')}")
            return response.cookies
        else:
            print_error(f"Login fallido: {data}")
            return None
    else:
        print_error(f"Error HTTP {response.status_code}: {response.text}")
        return None

# =============================================================================
# PASO 2: OBTENER CATÁLOGOS
# =============================================================================

def test_get_catalogos(cookies):
    """Obtiene los catálogos disponibles"""
    print_section("PASO: Obtener Catálogos")

    response = requests.get(
        f"{API_BASE}/catalogos",
        cookies=cookies
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Catálogos obtenidos correctamente")

        centros = data.get("centros", [])
        sectores = data.get("sectores", [])
        almacenes = data.get("almacenes", [])

        print_info(f"  - Centros disponibles: {len(centros)}")
        if centros:
            print_info(f"    Ejemplos: {', '.join([c.get('codigo', '') for c in centros[:3]])}")

        print_info(f"  - Sectores disponibles: {len(sectores)}")
        if sectores:
            print_info(f"    Ejemplos: {', '.join([s.get('nombre', '') for s in sectores[:3]])}")

        print_info(f"  - Almacenes disponibles: {len(almacenes)}")
        if almacenes:
            print_info(f"    Ejemplos: {', '.join([a.get('codigo', '') for a in almacenes[:3]])}")

        return data
    else:
        print_error(f"Error al obtener catálogos: {response.status_code}")
        return None

# =============================================================================
# PASO 3: BUSCAR MATERIALES
# =============================================================================

def test_search_materiales(cookies, query="TUERCA"):
    """Busca materiales disponibles"""
    print_section(f"PASO: Buscar Materiales ('{query}')")

    response = requests.get(
        f"{API_BASE}/materiales",
        params={"q": query, "limit": 10},
        cookies=cookies
    )

    if response.status_code == 200:
        materiales = response.json()
        print_success(f"Se encontraron {len(materiales)} materiales")

        for i, mat in enumerate(materiales[:5], 1):
            print_info(f"  {i}. {mat.get('codigo')} - {mat.get('descripcion')} (${mat.get('precio_usd', 0):.2f})")

        return materiales
    else:
        print_error(f"Error al buscar materiales: {response.status_code}")
        return []

# =============================================================================
# PASO 4: CREAR SOLICITUD
# =============================================================================

def test_crear_solicitud(cookies, materiales):
    """Crea una solicitud de materiales"""
    print_section("PASO: Crear Solicitud")

    if not materiales or len(materiales) == 0:
        print_error("No hay materiales disponibles para crear la solicitud")
        return None

    # Tomar los primeros 2 materiales
    items = []
    for mat in materiales[:2]:
        items.append({
            "codigo": mat.get("codigo"),
            "descripcion": mat.get("descripcion"),
            "cantidad": 5,
            "precio_unitario": float(mat.get("precio_usd", 0)),
            "comentario": "Material para mantenimiento preventivo"
        })

    # Fecha de necesidad: 15 días en el futuro
    fecha_necesidad = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

    solicitud_data = {
        "centro": "1008",
        "sector": "Mantenimiento",
        "justificacion": "Solicitud de prueba automática - Materiales para mantenimiento preventivo de equipos",
        "centro_costos": "CC001",
        "almacen_virtual": "ALM0001",
        "criticidad": "Normal",
        "fecha_necesidad": fecha_necesidad,
        "items": items
    }

    print_info("Datos de la solicitud:")
    print_info(f"  - Centro: {solicitud_data['centro']}")
    print_info(f"  - Sector: {solicitud_data['sector']}")
    print_info(f"  - Criticidad: {solicitud_data['criticidad']}")
    print_info(f"  - Fecha necesidad: {solicitud_data['fecha_necesidad']}")
    print_info(f"  - Items: {len(items)}")

    response = requests.post(
        f"{API_BASE}/solicitudes",
        json=solicitud_data,
        cookies=cookies,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print_success("Solicitud creada exitosamente")
            print_info(f"  - ID: {data.get('id')}")
            print_info(f"  - Status: {data.get('status')}")
            print_info(f"  - Total: ${data.get('total_monto', 0):.2f}")
            return data.get('id')
        else:
            print_error(f"Error al crear solicitud: {data}")
            return None
    else:
        print_error(f"Error HTTP {response.status_code}: {response.text}")
        return None

# =============================================================================
# PASO 5: VER DETALLE DE SOLICITUD
# =============================================================================

def test_get_solicitud_detail(cookies, sol_id):
    """Obtiene el detalle de una solicitud"""
    print_section(f"PASO: Ver Detalle de Solicitud #{sol_id}")

    response = requests.get(
        f"{API_BASE}/solicitudes/{sol_id}",
        cookies=cookies
    )

    if response.status_code == 200:
        solicitud = response.json()
        print_success("Detalle de solicitud obtenido")
        print_info(f"  - ID: {solicitud.get('id')}")
        print_info(f"  - Usuario: {solicitud.get('id_usuario')}")
        print_info(f"  - Centro: {solicitud.get('centro')}")
        print_info(f"  - Sector: {solicitud.get('sector')}")
        print_info(f"  - Status: {solicitud.get('status')}")
        print_info(f"  - Total: ${solicitud.get('total_monto', 0):.2f}")
        print_info(f"  - Fecha creación: {solicitud.get('created_at')}")

        data_json = solicitud.get('data_json')
        if data_json:
            items = data_json.get('items', [])
            print_info(f"  - Items en solicitud: {len(items)}")
            for i, item in enumerate(items[:3], 1):
                print_info(f"    {i}. {item.get('descripcion')} x{item.get('cantidad')}")

        return solicitud
    else:
        print_error(f"Error al obtener solicitud: {response.status_code}")
        return None

# =============================================================================
# PASO 6: LISTAR SOLICITUDES PENDIENTES (COMO COORDINADOR/ADMIN)
# =============================================================================

def test_list_solicitudes_pendientes(cookies):
    """Lista solicitudes pendientes de aprobación"""
    print_section("PASO: Listar Solicitudes Pendientes")

    response = requests.get(
        f"{API_BASE}/solicitudes",
        params={"status": "pendiente_de_aprobacion"},
        cookies=cookies
    )

    if response.status_code == 200:
        data = response.json()
        # El endpoint puede retornar un dict con 'solicitudes' o directamente una lista
        if isinstance(data, dict):
            solicitudes = data.get('solicitudes', data.get('data', []))
        else:
            solicitudes = data

        print_success(f"Se encontraron {len(solicitudes)} solicitudes pendientes")

        for i, sol in enumerate(solicitudes[:5], 1):
            print_info(f"  {i}. ID: {sol.get('id')} - {sol.get('sector')} - ${sol.get('total_monto', 0):.2f} - {sol.get('created_at')}")

        return solicitudes
    else:
        print_error(f"Error al listar solicitudes: {response.status_code}")
        return []

# =============================================================================
# PASO 7: APROBAR/RECHAZAR SOLICITUD
# =============================================================================

def test_decidir_solicitud(cookies, sol_id, accion="aprobar", comentario=""):
    """Aprueba o rechaza una solicitud"""
    accion_texto = "Aprobar" if accion == "aprobar" else "Rechazar"
    print_section(f"PASO: {accion_texto} Solicitud #{sol_id}")

    decision_data = {
        "accion": accion,
        "comentario": comentario or f"Solicitud {accion}da mediante prueba automática"
    }

    print_info(f"Decisión: {accion.upper()}")
    print_info(f"Comentario: {decision_data['comentario']}")

    response = requests.post(
        f"{API_BASE}/solicitudes/{sol_id}/decidir",
        json=decision_data,
        cookies=cookies,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print_success(f"Solicitud {accion}da exitosamente")
            print_info(f"  - Nuevo status: {data.get('status')}")
            return True
        else:
            print_error(f"Error al decidir solicitud: {data}")
            return False
    else:
        print_error(f"Error HTTP {response.status_code}: {response.text}")
        return False

# =============================================================================
# SCRIPT PRINCIPAL
# =============================================================================

def main():
    """Ejecuta el flujo completo de prueba"""
    print("\n" + "="*80)
    print("  PRUEBA DE FLUJO COMPLETO - SPM v1.0")
    print("  Solicitud: Creacion > Aprobacion > Verificacion")
    print("="*80)

    # PASO 1: Login como usuario solicitante
    cookies_usuario = test_login(USUARIO_SOLICITANTE, "Usuario Solicitante")
    if not cookies_usuario:
        print_error("No se pudo hacer login como usuario solicitante")
        return

    # PASO 2: Obtener catálogos
    catalogos = test_get_catalogos(cookies_usuario)
    if not catalogos:
        print_error("No se pudieron obtener los catálogos")
        return

    # PASO 3: Buscar materiales
    materiales = test_search_materiales(cookies_usuario, "TUERCA")
    if not materiales:
        # Intentar con otro término
        materiales = test_search_materiales(cookies_usuario, "TORNILLO")

    if not materiales:
        print_error("No se encontraron materiales en el sistema")
        return

    # PASO 4: Crear solicitud
    solicitud_id = test_crear_solicitud(cookies_usuario, materiales)
    if not solicitud_id:
        print_error("No se pudo crear la solicitud")
        return

    # PASO 5: Ver detalle de la solicitud recién creada
    solicitud = test_get_solicitud_detail(cookies_usuario, solicitud_id)
    if not solicitud:
        print_error("No se pudo obtener el detalle de la solicitud")
        return

    # PASO 6: Login como coordinador/admin
    cookies_coordinador = test_login(USUARIO_COORDINADOR, "Coordinador")
    if not cookies_coordinador:
        print_error("No se pudo hacer login como coordinador")
        # Intentar con admin
        cookies_coordinador = test_login(USUARIO_ADMIN, "Administrador")
        if not cookies_coordinador:
            print_error("No se pudo hacer login como admin tampoco")
            return

    # PASO 7: Listar solicitudes pendientes
    solicitudes_pendientes = test_list_solicitudes_pendientes(cookies_coordinador)

    # PASO 8: Aprobar la solicitud
    aprobacion_exitosa = test_decidir_solicitud(
        cookies_coordinador,
        solicitud_id,
        accion="aprobar",
        comentario="Aprobada mediante prueba automática - OK"
    )

    if aprobacion_exitosa:
        # PASO 9: Verificar el nuevo estado
        solicitud_actualizada = test_get_solicitud_detail(cookies_coordinador, solicitud_id)
        if solicitud_actualizada:
            nuevo_status = solicitud_actualizada.get('status')
            if nuevo_status == 'aprobada':
                print_section("RESULTADO FINAL")
                print_success("FLUJO COMPLETO EXITOSO")
                print_info("La solicitud fue creada, listada y aprobada correctamente")
                print_info(f"ID de solicitud: {solicitud_id}")
                print_info(f"Status final: {nuevo_status}")
            else:
                print_error(f"El status no es el esperado: {nuevo_status}")
        else:
            print_error("No se pudo verificar el estado final")
    else:
        print_error("No se pudo aprobar la solicitud")

    print("\n" + "="*80)
    print("  FIN DE LA PRUEBA")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
