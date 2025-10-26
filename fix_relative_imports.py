#!/usr/bin/env python3
"""
Script definitivo para reparar TODAS las importaciones
Analiza qué está siendo importado y calcula la ruta relativa correcta
"""
import re
from pathlib import Path

def calculate_relative_import_path(source_file, target_module_path):
    """
    Calcula la ruta relativa correcta.
    
    source_file: ruta del archivo que hace la importación (ej: services/auth/auth.py)
    target_module_path: ruta del módulo a importar (ej: middleware/csrf o core/config)
    """
    source = Path(source_file).resolve()
    
    # Encontrar backend_dir
    backend_parent = None
    for parent in source.parents:
        if parent.name == 'backend':
            backend_parent = parent
            break
    
    if not backend_parent:
        return None
    
    # Calcular ruta del target dentro de backend
    # Primero necesitamos saber qué tan profundo estamos
    source_relative = source.relative_to(backend_parent)
    source_depth = len(source_relative.parts) - 1  # -1 para excluir el archivo
    
    # Número de .. necesarios para volver a backend_parent
    ups = source_depth
    
    # Ahora bajar al target
    target_parts = target_module_path.split('.')
    down_path = '/'.join(target_parts)
    
    if ups == 0:
        # Estamos en backend/, podemos ir directo
        return '.' + ('.' + down_path.replace('/', '.') if down_path else '')
    else:
        # Necesitamos subir antes
        dots = '.' * (ups + 1)
        return dots + ('.'+down_path.replace('/', '.') if down_path else '')

def fix_imports_in_file(file_path):
    """Arregla importaciones en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original = ''.join(lines)
    modified = False
    
    for i, line in enumerate(lines):
        # Buscar: from .XXX import / from .XXX.YYY import
        # Cuando debería ser from ..XXX import / from ...XXX import, etc
        
        if re.match(r'^\s*from \.[^.]', line):  # from .algo pero no .. (incorrecto en subdirectorio)
            # Archivo está en subdirectorio pero import es como si estuviera en raíz
            file_path_obj = Path(file_path)
            backend_parent = None
            for parent in file_path_obj.parents:
                if parent.name == 'backend':
                    backend_parent = parent
                    break
            
            if backend_parent:
                relative_path = file_path_obj.relative_to(backend_parent)
                depth = len(relative_path.parts) - 1
                
                if depth > 0:  # Estamos en subdirectorio
                    # Cambiar .algo a ..algo o ...algo
                    match = re.match(r'^(\s*from )(\.+)(\w.*)', line)
                    if match:
                        indent = match.group(1)
                        old_dots = match.group(2)
                        rest = match.group(3)
                        
                        # Calcular nuevos dots
                        current_dots = len(old_dots)
                        needed_dots = depth + 1
                        
                        if needed_dots != current_dots:
                            new_line = indent + ('.' * needed_dots) + rest + '\n' if not line.endswith('\n') else ''
                            new_line = indent + ('.' * needed_dots) + rest
                            if line.endswith('\n'):
                                new_line += '\n'
                            lines[i] = new_line
                            modified = True

    new_content = ''.join(lines)
    if new_content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

# Aplicar a todos los archivos
backend_dir = Path('src/backend')
py_files = sorted(backend_dir.rglob('*.py'))

print("🔧 Reparando imports...\n")

fixed = 0
for py_file in py_files:
    if fix_imports_in_file(py_file):
        fixed += 1
        print(f"✅ {py_file.relative_to('.')}")

print(f"\n✨ Reparados {fixed} archivos")
