#!/usr/bin/env python3
"""
Script para corregir todas las importaciones absolutas a relativas en src/backend
Convierte TODAS las importaciones de src.backend.* a importaciones relativas correctas
"""
import re
from pathlib import Path

def fix_file_imports(file_path):
    """Arregla todas las importaciones en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Calcular cuántos '..' necesita este archivo
    file_path_obj = Path(file_path)
    parts = file_path_obj.parts
    
    # Encontrar 'backend' en la ruta
    backend_idx = None
    for i, part in enumerate(parts):
        if part == 'backend':
            backend_idx = i
            break
    
    if backend_idx is None:
        return False
    
    # Calcular profundidad: cuántas carpetas debajo de backend está el archivo
    # backend/app.py -> depth 0 (usa . para ver hermanos en backend/)
    # backend/routes/auth.py -> depth 1 (usa .. para ver hermanos en backend/)
    # backend/services/auth/auth.py -> depth 2 (usa ... para ver hermanos en backend/)
    
    current_relative_path = file_path_obj.relative_to(Path(*parts[:backend_idx+1]))
    folder_depth = len(current_relative_path.parts) - 1  # -1 para excluir el archivo
    parent_prefix = '.' * (folder_depth + 1)
    
    # Ahora reemplazar todas las importaciones
    # from src.backend.XXX -> from <prefix>.XXX
    content = re.sub(
        r'from src\.backend\.',
        f'from {parent_prefix}',
        content
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Ejecutar
backend_dir = Path('src/backend')
py_files = sorted(backend_dir.rglob('*.py'))

print(f"📝 Escaneando {len(py_files)} archivos...\n")

fixed_count = 0
for py_file in py_files:
    if fix_file_imports(py_file):
        fixed_count += 1
        rel_path = py_file.relative_to('.')
        print(f"✅ {rel_path}")

print(f"\n✨ Corregidos {fixed_count} archivos")
