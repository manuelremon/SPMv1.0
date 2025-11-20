#!/usr/bin/env python3
"""
Cleanup script for SPMv1.0 - Remove legacy, backup, and unnecessary files
"""
import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path("/home/user/SPMv1.0")

# Files to delete completely
FILES_TO_DELETE = [
    # Legacy files
    "tests/test_material_consumption_analyzer_v1_legacy.py",
    "src/frontend/login-legacy.html",

    # Debug files (move to archive instead of delete)
    # "src/frontend/debug-materiales.html",
    # "src/frontend/debug-materials.js",
    # "src/frontend/test_login_smoke.js",

    # Duplicate utility script
    "fix_duplicates.py",  # Already used, can delete
]

# Directories to delete completely
DIRS_TO_DELETE = [
    # Cache directories
    "src/__pycache__",
    "src/backend/__pycache__",
    "src/backend/routes/__pycache__",
    "src/backend/core/__pycache__",
    "src/backend/services/__pycache__",
    "src/backend/services/auth/__pycache__",
    "src/backend/services/db/__pycache__",
    "src/backend/services/dashboard/__pycache__",
    "src/backend/models/__pycache__",
    "src/backend/middleware/__pycache__",
    "src/planner/__pycache__",
    "src/agent/__pycache__",

    # Build/test cache
    ".pytest_cache",
]

# Scripts to move to archive (old/deprecated utilities)
SCRIPTS_TO_ARCHIVE = [
    "scripts/fix_ui_step2.py",  # Specific fix, probably done
    "scripts/fix_user_access.py",  # Specific fix
    "scripts/repair/fix_all_imports.py",  # Import fixes done
    "scripts/repair/fix_imports.py",  # Import fixes done
    "scripts/repair/fix_relative_imports.py",  # Import fixes done
    "scripts/utilities/check_users.py",  # Duplicate of manual/check_users2.py
    "scripts/utilities/debug_approve_issue.py",  # Specific debug
    "scripts/utilities/debug_token.py",  # Specific debug
    "scripts/utilities/create_solicitud_14.py",  # Test data
    "scripts/utilities/create_solicitud_15.py",  # Test data
    "scripts/utils/repair_imports.py",  # Duplicate
]

# Files to find and delete by pattern
PATTERNS_TO_DELETE = [
    "**/*.pyc",
    "**/*.pyo",
    "**/.DS_Store",
    "**/*~",
]

def cleanup():
    """Run cleanup operations"""
    deleted_files = 0
    deleted_dirs = 0
    archived_files = 0
    errors = []

    print("🧹 Starting cleanup of SPMv1.0...\n")

    # 1. Delete specific files
    print("📄 Deleting specific files...")
    for file_path in FILES_TO_DELETE:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                errors.append(f"  ❌ Error deleting {file_path}: {e}")
        else:
            print(f"  ℹ️  Not found: {file_path}")

    # 2. Delete directories
    print("\n📁 Deleting cache directories...")
    for dir_path in DIRS_TO_DELETE:
        full_path = BASE_DIR / dir_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"  ✅ Deleted: {dir_path}")
                deleted_dirs += 1
            except Exception as e:
                errors.append(f"  ❌ Error deleting {dir_path}: {e}")
        else:
            print(f"  ℹ️  Not found: {dir_path}")

    # 3. Archive old scripts
    print("\n📦 Archiving deprecated scripts...")
    archive_dir = BASE_DIR / "scripts" / "archive"
    archive_dir.mkdir(exist_ok=True)

    for script_path in SCRIPTS_TO_ARCHIVE:
        full_path = BASE_DIR / script_path
        if full_path.exists():
            try:
                # Preserve directory structure in archive
                relative = full_path.relative_to(BASE_DIR / "scripts")
                archive_dest = archive_dir / relative
                archive_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(archive_dest))
                print(f"  ✅ Archived: {script_path}")
                archived_files += 1
            except Exception as e:
                errors.append(f"  ❌ Error archiving {script_path}: {e}")
        else:
            print(f"  ℹ️  Not found: {script_path}")

    # 4. Delete files by pattern
    print("\n🔍 Deleting files by pattern...")
    for pattern in PATTERNS_TO_DELETE:
        for file_path in BASE_DIR.rglob(pattern.split('/')[-1]):
            # Skip if in node_modules or .git
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            try:
                file_path.unlink()
                print(f"  ✅ Deleted: {file_path.relative_to(BASE_DIR)}")
                deleted_files += 1
            except Exception as e:
                errors.append(f"  ❌ Error deleting {file_path}: {e}")

    # Summary
    print("\n" + "="*60)
    print("📊 CLEANUP SUMMARY")
    print("="*60)
    print(f"✅ Files deleted: {deleted_files}")
    print(f"✅ Directories deleted: {deleted_dirs}")
    print(f"✅ Files archived: {archived_files}")

    if errors:
        print(f"\n⚠️  Errors encountered: {len(errors)}")
        for error in errors:
            print(error)
    else:
        print("\n🎉 Cleanup completed successfully!")

    return deleted_files + deleted_dirs + archived_files

if __name__ == "__main__":
    cleanup()
