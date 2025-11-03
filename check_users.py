import sqlite3

db_path = "src/backend/core/data/spm.db"
con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=== USUARIOS EN LA BASE DE DATOS ===\n")
usuarios = cur.execute("SELECT id, id_spm, nombre FROM usuarios LIMIT 10").fetchall()
for u in usuarios:
    print(f"id={u['id']}, id_spm={u['id_spm']}, nombre={u['nombre']}")

con.close()
