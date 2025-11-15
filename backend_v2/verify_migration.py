import sqlite3

conn = sqlite3.connect('backend_v2.db')
cursor = conn.cursor()

# Listar tablas
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("✅ Tablas creadas:")
for table in tables:
    print(f"   - {table[0]}")

print()

# Contar materiales
count_materiales = cursor.execute("SELECT COUNT(*) FROM materiales").fetchone()[0]
print(f"📦 Materiales en catálogo: {count_materiales}")

# Contar usuarios
count_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"👥 Usuarios creados: {count_users}")

print()
print("🎉 Migración FASE 4.2 completada exitosamente!")

conn.close()
