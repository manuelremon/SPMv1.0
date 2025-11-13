"""
Configuración global de pytest para backend_v2
Agrega el directorio backend_v2 al PYTHONPATH
"""
import sys
from pathlib import Path

# Agregar directorio backend_v2 (padre de tests/) al PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
