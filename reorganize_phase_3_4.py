#!/usr/bin/env python3
"""
SCRIPT DE REORGANIZACIÓN - FASE 3 y 4
Mueve documentación a docs/ y scripts a scripts/
"""
import os
import shutil
from pathlib import Path

REPO_ROOT = Path('d:/GitHub/SPMv1.0')

print("=" * 80)
print("REORGANIZACIÓN DEL REPOSITORIO - FASE 3 y 4")
print("=" * 80)

# FASE 3: MOVER DOCUMENTACIÓN A docs/
print("\n3️⃣  FASE 3: DOCUMENTACIÓN → docs/")
print("-" * 80)

doc_moves = {
    'FINAL_STATUS_PLANIFICACION.txt': 'docs/planning/',
    'ITERACION_COMPLETADA_NAVEGACION.md': 'docs/history/',
    'ITERACION_COMPLETADA_RESUMEN.txt': 'docs/history/',
    'MENU_NAVIGATION_COMPLETE.md': 'docs/guides/',
    'PLANIFICACION_FLUJO_VISUAL.md': 'docs/planning/',
    'PLANIFICACION_INTEGRATION_COMPLETE.md': 'docs/planning/',
    'PLANNER_DEMO_CREDENTIALS.txt': 'docs/planning/',
    'PRUEBA_MANUAL_MENU.md': 'docs/testing/',
    'QUICK_REFERENCE_PLANIFICACION.txt': 'docs/planning/',
    'QUICK_START.txt': 'docs/',
    'RESUMEN_FINAL_PLANIFICACION.md': 'docs/planning/',
    'SYSTEM_REPAIRED.txt': 'docs/system/',
    'TESTING_MANUAL_PLANIFICACION.md': 'docs/testing/',
}

moved_docs = 0

for file, dest_dir in doc_moves.items():
    src = REPO_ROOT / file
    dest_path = REPO_ROOT / dest_dir
    
    if src.exists():
        # Crear directorio destino
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Mover archivo
        dest_file = dest_path / file
        try:
            shutil.move(str(src), str(dest_file))
            print(f"  ✓ {file} → {dest_dir}")
            moved_docs += 1
        except Exception as e:
            print(f"  ✗ Error moviendo {file}: {e}")
    else:
        print(f"  ⚠ No existe: {file}")

print(f"\n✓ Documentos movidos: {moved_docs}")

# FASE 4: MOVER SCRIPTS A scripts/
print("\n4️⃣  FASE 4: SCRIPTS → scripts/")
print("-" * 80)

script_moves = {
    'analyze_repo.py': 'scripts/utilities/',
    'check_db.py': 'scripts/utilities/',
    'create_test_data.py': 'scripts/db/',
    'create_planner_demo.py': 'scripts/utilities/',
    'init_db.py': 'scripts/db/',
    'list_tables.py': 'scripts/db/',
    'validate_imports.py': 'scripts/utilities/',
    'fix_all_imports.py': 'scripts/repair/',
    'fix_imports.py': 'scripts/repair/',
    'fix_relative_imports.py': 'scripts/repair/',
    'validate_planificacion.sh': 'scripts/dev/',
}

ps1_scripts = {
    'CHECK_FINAL.ps1': 'scripts/dev/',
    'VERIFY_MENU_NAVIGATION.ps1': 'scripts/dev/',
}

moved_scripts = 0

# Mover scripts Python
for file, dest_dir in script_moves.items():
    src = REPO_ROOT / file
    dest_path = REPO_ROOT / dest_dir
    
    if src.exists():
        dest_path.mkdir(parents=True, exist_ok=True)
        dest_file = dest_path / file
        try:
            shutil.move(str(src), str(dest_file))
            print(f"  ✓ {file} → {dest_dir}")
            moved_scripts += 1
        except Exception as e:
            print(f"  ✗ Error moviendo {file}: {e}")
    else:
        print(f"  ⚠ No existe: {file}")

# Mover scripts PowerShell
for file, dest_dir in ps1_scripts.items():
    src = REPO_ROOT / file
    dest_path = REPO_ROOT / dest_dir
    
    if src.exists():
        dest_path.mkdir(parents=True, exist_ok=True)
        dest_file = dest_path / file
        try:
            shutil.move(str(src), str(dest_file))
            print(f"  ✓ {file} → {dest_dir}")
            moved_scripts += 1
        except Exception as e:
            print(f"  ✗ Error moviendo {file}: {e}")
    else:
        print(f"  ⚠ No existe: {file}")

print(f"\n✓ Scripts movidos: {moved_scripts}")

# RESUMEN
print("\n" + "=" * 80)
print("📊 RESUMEN FASE 3 y 4")
print("=" * 80)
print(f"\n✓ Documentos movidos: {moved_docs}")
print(f"✓ Scripts movidos: {moved_scripts}")
print(f"✓ Total movimientos: {moved_docs + moved_scripts}")

print("\n✅ FASE 3 y 4 COMPLETADAS")
print("\n📝 PRÓXIMOS PASOS:")
print("  1. Verificar: git status")
print("  2. Validar: python -m flask run (verificar que funciona)")
print("  3. Tests: pytest tests/ (ejecutar suite de pruebas)")
print("  4. Commit: git add . && git commit -m 'chore: reorganize repo structure'")

print("\n" + "=" * 80)
