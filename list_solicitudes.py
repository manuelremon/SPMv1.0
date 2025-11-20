#!/usr/bin/env python3
"""Listar todas las solicitudes en la BD"""

import sqlite3

con = sqlite3.connect('src/backend/core/data/spm.db')
con.row_factory = sqlite3.Row

print("=== Todas las Solicitudes en la BD ===\n")

rows = con.execute(
    """SELECT id, centro, sector, criticidad, almacen_virtual,
              total_monto, justificacion, created_at
       FROM solicitudes
       ORDER BY id DESC
       LIMIT 10"""
).fetchall()

if rows:
    for row in rows:
        print(f"ID #{row['id']}:")
        print(f"  Centro: {row['centro']}")
        print(f"  Sector: {row['sector']}")
        print(f"  Criticidad: {row['criticidad']}")
        print(f"  Almacen: {row['almacen_virtual']}")
        print(f"  Total: ${row['total_monto']}")
        print(f"  Just: {row['justificacion'][:50]}")
        print(f"  Creada: {row['created_at']}")
        print()
else:
    print("No hay solicitudes en la BD")

con.close()
