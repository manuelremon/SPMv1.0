#!/usr/bin/env python
"""
Script mejorado para ejecutar el backend con mejor manejo de errores
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

logger.info(f"Root directory: {root_dir}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path[:3]}")

try:
    logger.info("Importando aplicación Flask...")
    from src.backend.app import app
    logger.info("✓ Aplicación Flask importada exitosamente")
    
except Exception as e:
    logger.error(f"✗ Error importando aplicación: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    try:
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "5000"))
        
        logger.info(f"Iniciando servidor en {host}:{port}...")
        logger.info("Debug mode: ON")
        logger.info("Reloader: OFF")
        
        app.run(
            host=host, 
            port=port, 
            debug=True, 
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"✗ Error iniciando servidor: {e}", exc_info=True)
        sys.exit(1)
