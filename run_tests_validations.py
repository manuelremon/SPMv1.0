#!/usr/bin/env python
"""Script para ejecutar tests de validaciones Fase 1"""

import subprocess
import sys

if __name__ == "__main__":
    # Ejecutar pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", 
         "tests/test_solicitud_validations.py", 
         "-v", "--tb=short"],
        capture_output=False
    )
    sys.exit(result.returncode)
