#!/usr/bin/env python
"""
Debug script: entender estructura real de usuarios y roles.
"""
import sqlite3
import json

DB_PATH = "src/backend/core/data/spm.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

with sqlite3.connect(DB_PATH) as con:
    con.row_factory = dict_factory
    
    # 1. Ver todas las tablas
    print("=" * 60)
    print("TODAS LAS TABLAS EN LA BD")
    print("=" * 60)
    tables = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for t in tables:
        print(f"  - {t.get('name')}")
    
    # 2. Ver estructura de tabla usuarios
    print("\n" + "=" * 60)
    print("ESTRUCTURA DE TABLA 'usuarios'")
    print("=" * 60)
    schema = con.execute("PRAGMA table_info(usuarios)").fetchall()
    for col in schema:
        print(f"  {col.get('name'):20} {col.get('type'):15} {col.get('notnull') and 'NOT NULL' or ''}")
    
    # 3. Todos los usuarios
    print("\n" + "=" * 60)
    print("TODOS LOS USUARIOS")
    print("=" * 60)
    users = con.execute("SELECT id_spm, nombre, mail FROM usuarios").fetchall()
    for u in users:
        print(f"  id_spm: {u.get('id_spm'):20} nombre: {u.get('nombre'):20} mail: {u.get('mail')}")
    
    # 4. Solicitud 13 - aprobador_id
    print("\n" + "=" * 60)
    print("SOLICITUD 13")
    print("=" * 60)
    sol = con.execute(
        "SELECT id, id_usuario, aprobador_id, planner_id, status FROM solicitudes WHERE id=13"
    ).fetchone()
    if sol:
        print(json.dumps(sol, indent=2, ensure_ascii=False))
    else:
        print("Solicitud 13 NO ENCONTRADA")

print("\n" + "=" * 60)
print("PROBLEMA IDENTIFICADO:")
print("=" * 60)
print("""
1. Usuario 'admin' NO EXISTE en tabla usuarios.
2. La BD no tiene tablas de roles.
3. _can_resolve() intenta llamar a has_role() que probablemente verificaría
   atributos en la tabla usuarios (ej: columna 'rol', 'roles', etc).
4. Solicitud 13 no tiene aprobador_id ni planner_id asignados.

SOLUCIONES:
  a) Asignar aprobador_id a solicitud 13 en BD
  b) Crear usuario 'admin' con los permisos necesarios
  c) Verificar cómo ha_role() funciona en auth.py
""")
