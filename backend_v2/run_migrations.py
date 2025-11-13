"""
Backend v2.0 - Migration Runner
Script para ejecutar migraciones SQL de la base de datos
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import List, Tuple

import bcrypt


class MigrationRunner:
    """Ejecuta migraciones SQL en orden secuencial"""
    
    def __init__(self, db_path: str, migrations_dir: str = None):
        """
        Args:
            db_path: Ruta a la base de datos SQLite
            migrations_dir: Directorio de migraciones (default: migrations/)
        """
        self.db_path = db_path
        
        if migrations_dir is None:
            # Directorio migrations/ relativo a este script
            script_dir = Path(__file__).parent
            migrations_dir = script_dir / "migrations"
        
        self.migrations_dir = Path(migrations_dir)
        
    def get_migration_files(self) -> List[Path]:
        """
        Obtiene lista ordenada de archivos .sql en migrations/
        
        Returns:
            Lista de paths ordenados por nombre (001_xxx.sql, 002_xxx.sql, etc.)
        """
        if not self.migrations_dir.exists():
            print(f"❌ Directorio de migraciones no encontrado: {self.migrations_dir}")
            return []
        
        sql_files = sorted(self.migrations_dir.glob("*.sql"))
        return sql_files
    
    def run_migration(self, sql_file: Path) -> Tuple[bool, str]:
        """
        Ejecuta un archivo SQL de migración.
        
        Args:
            sql_file: Path al archivo .sql
        
        Returns:
            Tupla (success: bool, message: str)
        """
        try:
            # Leer archivo SQL
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            # Conectar a DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ejecutar SQL (puede contener múltiples statements)
            cursor.executescript(sql_content)
            
            conn.commit()
            conn.close()
            
            return True, f"✅ Migración ejecutada: {sql_file.name}"
        
        except Exception as e:
            return False, f"❌ Error en {sql_file.name}: {e}"
    
    def run_all(self) -> None:
        """Ejecuta todas las migraciones en orden"""
        print("\n" + "="*60)
        print("🚀 EJECUTANDO MIGRACIONES DE BASE DE DATOS")
        print("="*60)
        print(f"DB: {self.db_path}")
        print(f"Migrations: {self.migrations_dir}")
        print()
        
        # Obtener migraciones
        migrations = self.get_migration_files()
        
        if not migrations:
            print("⚠️  No se encontraron migraciones para ejecutar.")
            return
        
        print(f"📁 Migraciones encontradas: {len(migrations)}")
        for mig in migrations:
            print(f"   - {mig.name}")
        print()
        
        # Ejecutar cada migración
        success_count = 0
        error_count = 0
        
        for migration_file in migrations:
            success, message = self.run_migration(migration_file)
            print(message)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        
        # Resumen
        print()
        print("="*60)
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores:   {error_count}")
        print("="*60)
        
        if error_count == 0:
            print("🎉 Todas las migraciones se ejecutaron correctamente!")
        else:
            print("⚠️  Algunas migraciones fallaron. Revisar errores arriba.")


def generate_bcrypt_hash(password: str) -> str:
    """
    Genera hash bcrypt para una contraseña.
    
    Útil para crear seeds de usuarios en migraciones.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash bcrypt como string
    
    Ejemplo:
        >>> generate_bcrypt_hash("admin123")
        '$2b$12$...'
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def main():
    """
    CLI para ejecutar migraciones.
    
    Uso:
        python run_migrations.py                    # Usa backend_v2.db
        python run_migrations.py /path/to/db.db     # Especifica DB
    """
    import sys
    
    # Path a DB (argumento o default)
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Default: backend_v2.db en directorio del proyecto
        project_root = Path(__file__).parent.parent
        db_path = project_root / "backend_v2.db"
    
    # Crear directorio si no existe
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Ejecutar migraciones
    runner = MigrationRunner(str(db_path))
    runner.run_all()
    
    print()
    print("💡 TIP: Puedes verificar la DB con:")
    print(f"   sqlite3 {db_path}")
    print("   sqlite> .schema users")
    print("   sqlite> SELECT * FROM users;")


if __name__ == "__main__":
    main()
