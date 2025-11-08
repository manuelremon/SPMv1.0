"""
Fix migration: Update usuario_centros and usuario_almacenes to use correct usuario_id
"""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
db_path = PROJECT_ROOT / "src" / "backend" / "core" / "data" / "spm.db"
con = sqlite3.connect(str(db_path))
cur = con.cursor()

print("=== FIXING USER ACCESS DATA ===\n")

# Delete old data with wrong ID
print("1️⃣ Borrando datos antiguos con ID incorrecto...")
cur.execute("DELETE FROM usuario_centros WHERE usuario_id = 'ID2'")
cur.execute("DELETE FROM usuario_almacenes WHERE usuario_id = 'ID2'")
print("✅ Datos antiguos borrados")

# Insert correct data with correct ID (numeric string '2')
print("\n2️⃣ Insertando datos con ID correcto ('2')...")
centros = [1008, 1050]
for centro_id in centros:
    cur.execute(
        "INSERT OR IGNORE INTO usuario_centros (usuario_id, centro_id) VALUES (?, ?)",
        ('2', centro_id)
    )
    print(f"✅ Added access: '2' -> Centro {centro_id}")

# For almacenes, give access to common ones
almacenes = cur.execute("SELECT id FROM catalog_almacenes LIMIT 5").fetchall()
almacen_ids = [a[0] for a in almacenes]

for almacen_id in almacen_ids:
    cur.execute(
        "INSERT OR IGNORE INTO usuario_almacenes (usuario_id, almacen_id) VALUES (?, ?)",
        ('2', almacen_id)
    )
    print(f"✅ Added access: '2' -> Almacen {almacen_id}")

con.commit()

print("\n=== VERIFICATION ===")

# Verify data
centros_access = cur.execute(
    "SELECT centro_id FROM usuario_centros WHERE usuario_id = ?",
    ('2',)
).fetchall()
print(f"Usuario '2' authorized centros: {[c[0] for c in centros_access]}")

almacenes_access = cur.execute(
    "SELECT almacen_id FROM usuario_almacenes WHERE usuario_id = ?",
    ('2',)
).fetchall()
print(f"Usuario '2' authorized almacenes: {[a[0] for a in almacenes_access]}")

con.close()
print("\n✅ Migration completed!")
