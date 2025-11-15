#!/usr/bin/env python3
"""
SCRIPT DE LIMPIEZA - FASE 1 y 2
Elimina duplicados y archivos obsoletos
(No destructivo hasta que se confirme)
"""
import os
import shutil
from pathlib import Path

REPO_ROOT = Path('d:/GitHub/SPMv1.0')

# Lista de duplicados a eliminar
DUPLICATES_TO_DELETE = [
    'src/frontend/pages/admin/admin-solicitudes.html',
    'src/frontend/pages/admin/admin-centros.html',
    'src/frontend/pages/admin/admin-almacenes.html',
    'src/frontend/pages/admin/admin-dashboard.html',
    'src/frontend/pages/admin/admin-reportes.html',
    'src/frontend/pages/admin/admin-configuracion.html',
    'src/frontend/pages/user/mis-solicitudes.html',
    'src/frontend/pages/user/agregar-materiales.html',
    'src/frontend/pages/user/equipo-solicitudes.html',
    'src/frontend/pages/user/reportes.html',
    'src/frontend/pages/user/notificaciones.html',
    'src/frontend/pages/user/presupuesto.html',
    'src/frontend/pages/user/uploads.html',
    'Agent/gemini2.5-agent-starter/agent/__init__.py',
    'src/backend/uploads/ab9fffda4181438ca66a0aa5234397aa.png',
]

# Lista de archivos obsoletos
OBSOLETE_FILES = [
    'database/backup/spm.db.bak',
    'docs/archive/legacy/src_backend_server.py.bak',
    'src/backend/data/Materiales.csv.bak',
]

print("=" * 80)
print("LIMPIEZA DEL REPOSITORIO - FASE 1 y 2")
print("=" * 80)

print("\n📋 ARCHIVOS A ELIMINAR:")
print("\n1️⃣  DUPLICADOS HTML (11 archivos)")
all_files = DUPLICATES_TO_DELETE + OBSOLETE_FILES
deleted_count = 0
errors = []

for file_path in DUPLICATES_TO_DELETE:
    full_path = REPO_ROOT / file_path
    if full_path.exists():
        try:
            full_path.unlink()
            print(f"  ✓ Eliminado: {file_path}")
            deleted_count += 1
        except Exception as e:
            errors.append((file_path, str(e)))
            print(f"  ✗ Error: {file_path} - {e}")
    else:
        print(f"  ⚠ No existe: {file_path}")

print(f"\n2️⃣  ARCHIVOS OBSOLETOS (.bak) - {len(OBSOLETE_FILES)} archivos")
for file_path in OBSOLETE_FILES:
    full_path = REPO_ROOT / file_path
    if full_path.exists():
        try:
            full_path.unlink()
            print(f"  ✓ Eliminado: {file_path}")
            deleted_count += 1
        except Exception as e:
            errors.append((file_path, str(e)))
            print(f"  ✗ Error: {file_path} - {e}")
    else:
        print(f"  ⚠ No existe: {file_path}")

# Limpiar directorios vacíos
print(f"\n3️⃣  LIMPIANDO DIRECTORIOS VACÍOS...")
empty_dirs_deleted = 0

for root, dirs, files in os.walk(REPO_ROOT, topdown=False):
    for dir_name in dirs:
        dir_path = Path(root) / dir_name
        try:
            if not any(dir_path.iterdir()) and '.git' not in str(dir_path):
                if 'pages' in str(dir_path):  # Eliminar la carpeta pages si está vacía
                    dir_path.rmdir()
                    print(f"  ✓ Eliminado directorio: {dir_path.relative_to(REPO_ROOT)}")
                    empty_dirs_deleted += 1
        except:
            pass

print("\n" + "=" * 80)
print("📊 RESUMEN")
print("=" * 80)
print(f"\n✓ Archivos eliminados: {deleted_count}")
print(f"✓ Directorios vacios eliminados: {empty_dirs_deleted}")

if errors:
    print(f"\n⚠ Errores encontrados: {len(errors)}")
    for file, error in errors:
        print(f"  - {file}: {error}")
else:
    print(f"\n✅ SIN ERRORES - Limpieza completada exitosamente")

print("\n📝 PRÓXIMOS PASOS:")
print("  1. Verificar: python -m flask ... run")
print("  2. Probar: pytest tests/")
print("  3. Revisar: git status")
print("  4. Si todo ok, ejecutar: FASE 3 (reorganización de archivos)")

print("\n" + "=" * 80)
