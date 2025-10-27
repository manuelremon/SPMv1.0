#!/usr/bin/env python3
"""
Script para corregir todas las importaciones absolutas a relativas en src/backend
Cambia: from src.backend.XXX -> importaciones relativas correctas
"""
import re
from pathlib import Path

def get_relative_import(file_path, target_module):
    """Calcula la importación relativa correcta basada en la posición del archivo."""
    # Ejemplo: routes/auth_routes.py queriendo acceder a services/auth/auth.py
    # Necesita: from ..services.auth.auth import ...
    
    file_path = Path(file_path)
    
    # Obtener nivel de profundidad (backend/ = 0, routes/ = 1, services/ = 1, etc)
    parts = file_path.parts
    backend_idx = None
    for i, part in enumerate(parts):
        if part == 'backend':
            backend_idx = i
            break
    
    if backend_idx is None:
        return None
    
    # Contar cuántos niveles estamos dentro de backend
    file_depth = len(parts) - backend_idx - 2  # -2: backend y el archivo actual
    
    # Construir punto prefijo
    prefix = '.' * (file_depth + 1)  # +1 porque siempre empezamos con un punto
    
    return prefix

def convert_imports(file_path):
    """Convierte importaciones absolutas a relativas en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if 'from src.backend.' in line or 'import src.backend.' in line:
            # Extraer el módulo target
            match = re.search(r'from src\.backend\.(\S+)|\simport src\.backend\.(\S+)', line)
            if match:
                module = match.group(1) or match.group(2)
                
                # Calcular profundidad del archivo actual
                file_parts = Path(file_path).parts
                backend_idx = None
                for i, part in enumerate(file_parts):
                    if part == 'backend':
                        backend_idx = i
                        break
                
                if backend_idx is not None:
                    file_depth = len(file_parts) - backend_idx - 2
                    prefix = '.' * (file_depth + 1)
                    
                    if 'from' in line:
                        line = re.sub(
                            r'from src\.backend\.',
                            f'from {prefix}',
                            line
                        )
                    else:
                        line = re.sub(
                            r'import src\.backend\.',
                            f'from {prefix} import ',
                            line
                        )
        
        new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Buscar todos los archivos .py en src/backend
backend_dir = Path('src/backend')
py_files = list(backend_dir.rglob('*.py'))

print(f"📝 Procesando {len(py_files)} archivos...\n")

fixed = 0
for py_file in py_files:
    if convert_imports(py_file):
        fixed += 1
        print(f"✅ Corregido: {py_file.relative_to('.')}")

print(f"\n🎉 Se corrigieron {fixed} archivos")
