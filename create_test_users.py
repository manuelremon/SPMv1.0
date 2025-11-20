#!/usr/bin/env python3
"""
Script para crear/actualizar usuarios de prueba en SPM v1.0
Contraseña por defecto: "test123" para todos los usuarios
"""

import sqlite3
import bcrypt
from pathlib import Path

DB_PATH = Path("src/backend/spm.db")
DEFAULT_PASSWORD = "test123"

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_test_users():
    """Crea/actualiza usuarios de prueba"""

    if not DB_PATH.exists():
        print(f"[ERROR] Base de datos no encontrada: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hash de la contraseña por defecto
    password_hash = hash_password(DEFAULT_PASSWORD)

    # Usuarios de prueba
    test_users = [
        {
            'id_spm': 'admin',
            'nombre': 'Administrador',
            'apellido': 'Sistema',
            'rol': 'admin',
            'mail': 'admin@spm.com',
            'telefono': '+54 299 467 3102',
            'posicion': 'Administrador del Sistema',
            'sector': 'TI',
            'centros': '["1008"]'
        },
        {
            'id_spm': 'coordinador',
            'nombre': 'Coordinador',
            'apellido': 'Prueba',
            'rol': 'coordinador',
            'mail': 'coordinador@spm.com',
            'telefono': '+54 299 467 3103',
            'posicion': 'Coordinador',
            'sector': 'Operaciones',
            'centros': '["1008", "1009"]'
        },
        {
            'id_spm': 'usuario',
            'nombre': 'Usuario',
            'apellido': 'Prueba',
            'rol': 'usuario',
            'mail': 'usuario@spm.com',
            'telefono': '+54 299 467 3104',
            'posicion': 'Usuario',
            'sector': 'Mantenimiento',
            'centros': '["1008"]'
        }
    ]

    print(">> Creando/actualizando usuarios de prueba...\n")

    for user in test_users:
        try:
            # Verificar si el usuario existe
            cursor.execute("SELECT id_spm FROM usuarios WHERE id_spm = ? OR mail = ?",
                         (user['id_spm'], user['mail']))
            exists = cursor.fetchone()

            if exists:
                # Actualizar usuario existente (solo contraseña)
                cursor.execute("""
                    UPDATE usuarios
                    SET contrasena = ?
                    WHERE id_spm = ? OR mail = ?
                """, (password_hash, user['id_spm'], user['mail']))
                print(f"[OK] Usuario actualizado: {user['id_spm']} ({user['mail']})")
            else:
                # Crear nuevo usuario
                cursor.execute("""
                    INSERT INTO usuarios
                    (id_spm, nombre, apellido, rol, mail, telefono, posicion, sector, centros, contrasena, estado_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo')
                """, (
                    user['id_spm'],
                    user['nombre'],
                    user['apellido'],
                    user['rol'],
                    user['mail'],
                    user['telefono'],
                    user['posicion'],
                    user['sector'],
                    user['centros'],
                    password_hash
                ))
                print(f"[OK] Usuario creado: {user['id_spm']} ({user['mail']})")

        except Exception as e:
            print(f"[ERROR] Error con usuario {user['id_spm']}: {e}")

    # También actualizar los usuarios existentes de la BD
    print("\n>> Actualizando contrasenias de usuarios existentes...\n")

    existing_users = [
        ('1', 'manuelremon@live.com.ar'),
        ('2', 'juanlevi@ypf.com'),
        ('3', 'pedromamani@ypf.com'),
        ('4', 'robertorosas@ypf.com'),
        ('5', 'carlosperez@ypf.com')
    ]

    for user_id, email in existing_users:
        try:
            cursor.execute("""
                UPDATE usuarios
                SET contrasena = ?
                WHERE id_spm = ?
            """, (password_hash, user_id))
            print(f"[OK] Contrasenia actualizada para ID: {user_id} ({email})")
        except Exception as e:
            print(f"[ERROR] Error actualizando {user_id}: {e}")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("[OK] Proceso completado!")
    print("="*60)
    print("\nCREDENCIALES DE PRUEBA:")
    print("-" * 60)
    print("Administrador:")
    print("   Email: admin@spm.com")
    print("   Usuario: admin")
    print(f"   Contrasenia: {DEFAULT_PASSWORD}")
    print("\nCoordinador:")
    print("   Email: coordinador@spm.com")
    print("   Usuario: coordinador")
    print(f"   Contrasenia: {DEFAULT_PASSWORD}")
    print("\nUsuario:")
    print("   Email: usuario@spm.com")
    print("   Usuario: usuario")
    print(f"   Contrasenia: {DEFAULT_PASSWORD}")
    print("\nUsuarios existentes:")
    print("   IDs: 1, 2, 3, 4, 5")
    print(f"   Contrasenia: {DEFAULT_PASSWORD}")
    print("-" * 60)

if __name__ == "__main__":
    create_test_users()
