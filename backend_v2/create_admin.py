"""Script para crear usuario administrador"""
from datetime import datetime
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash
import sys
from pathlib import Path

# Usar la DB del proyecto (en la raíz)
db_path = Path(__file__).parent.parent / 'backend_v2.db'
engine = create_engine(f'sqlite:///{db_path}')

# Datos del admin
username = 'admin'
password_hash = generate_password_hash('admin123')
email = 'admin@spm.com'

# Insertar usuario
with engine.connect() as conn:
    # Verificar si ya existe
    result = conn.execute(
        text("SELECT id FROM users WHERE username = :username"),
        {"username": username}
    )
    
    if result.fetchone():
        print(f"⚠️  Usuario '{username}' ya existe")
    else:
        now = datetime.now().isoformat()
        conn.execute(
            text("""
                INSERT INTO users (
                    username, email, password_hash, nombre, apellido, role,
                    is_active, estado_registro, created_at, updated_at
                ) VALUES (
                    :username, :email, :password_hash, :nombre, :apellido, :role,
                    :is_active, :estado_registro, :created_at, :updated_at
                )
            """),
            {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "nombre": "Admin",
                "apellido": "Sistema",
                "role": "Administrador",
                "is_active": True,
                "estado_registro": "Activo",
                "created_at": now,
                "updated_at": now
            }
        )
        conn.commit()
        print(f"✅ Usuario '{username}' creado exitosamente")
        print(f"   Email: {email}")
        print(f"   Password: admin123")
