#!/usr/bin/env python
"""Backend debug launcher - diagnóstico completo"""
import sys
import os
import socket
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.info("=" * 60)
logger.info("INICIANDO BACKEND SPM - MODO DEBUG")
logger.info("=" * 60)

# Test 1: Check port availability
logger.info("\n[1] Verificando disponibilidad del puerto 5000...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5000))
if result == 0:
    logger.error("❌ Puerto 5000 ya está en uso")
    sock.close()
    sys.exit(1)
else:
    logger.info("✅ Puerto 5000 disponible")
sock.close()

# Test 2: Import Flask app
logger.info("\n[2] Importando aplicación Flask...")
try:
    from src.backend.app import app
    logger.info("✅ App importada exitosamente")
except Exception as e:
    logger.error(f"❌ Error importando app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check app configuration
logger.info("\n[3] Verificando configuración de la app...")
logger.info(f"  - Debug mode: {app.debug}")
logger.info(f"  - Número de rutas: {len(list(app.url_map.iter_rules()))}")

# Test 4: List first 10 routes
logger.info("\n[4] Primeras 10 rutas registradas:")
routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        routes.append(f"  - {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
        if len(routes) >= 10:
            break
for route in routes:
    logger.info(route)

# Test 5: Try to bind to port directly
logger.info("\n[5] Intentando bindear a 0.0.0.0:5000...")
try:
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    test_sock.bind(('0.0.0.0', 5000))
    test_sock.close()
    logger.info("✅ Bind a puerto 5000 exitoso")
except Exception as e:
    logger.error(f"❌ Error en bind: {e}")
    sys.exit(1)

# Test 6: Start Flask server
logger.info("\n[6] Iniciando servidor Flask...")
logger.info("=" * 60)
logger.info("🚀 SERVIDOR INICIADO - ESCUCHANDO EN http://127.0.0.1:5000")
logger.info("   Presiona CTRL+C para detener")
logger.info("=" * 60)

try:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    
    # Use werkzeug directly for better control
    from werkzeug.serving import make_server
    server = make_server(host, port, app, threaded=True)
    logger.info(f"\n✅ Servidor creado: {host}:{port}")
    logger.info("✅ Escuchando en todas las interfaces...")
    
    server.serve_forever()
except KeyboardInterrupt:
    logger.info("\n\n⏹️  Servidor detenido por usuario")
except Exception as e:
    logger.error(f"\n❌ Error iniciando servidor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
