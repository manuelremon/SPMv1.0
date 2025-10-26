#!/usr/bin/env python
"""
Crear solicitud 14 con usuario real y aprobador asignado.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "src/backend/core/data/spm.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

with sqlite3.connect(DB_PATH) as con:
    con.row_factory = dict_factory
    
    # Crear solicitud 14 con:
    # - id_usuario: "1" (Manuel, usuario real)
    # - centro: "Centro A"
    # - sector: "Operaciones"
    # - justificacion: "Solicitud de prueba para aprobación"
    # - centro_costos: "CC001"
    # - almacen_virtual: "AV001"
    # - status: "pendiente_de_aprobacion"
    # - aprobador_id: "2" (Juan - el superior)
    
    now = datetime.utcnow().isoformat()
    
    # Preparar data_json con 2 items
    data_json = {
        "items": [
            {"material": "Tubo acero 2.5\"", "cantidad": 50, "costo_unitario": 250, "total": 12500},
            {"material": "Válvula compuerta", "cantidad": 10, "costo_unitario": 1250, "total": 12500}
        ],
        "total": 25000
    }
    
    try:
        con.execute("""
            INSERT INTO solicitudes (
                id_usuario, centro, sector, justificacion, centro_costos, almacen_virtual,
                criticidad, fecha_necesidad, data_json, status, aprobador_id, planner_id,
                total_monto, notificado_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "1",  # id_usuario: Manuel
            "Centro A",  # centro
            "Operaciones",  # sector
            "Solicitud de prueba para aprobación",  # justificacion
            "CC001",  # centro_costos
            "AV001",  # almacen_virtual
            "Normal",  # criticidad
            None,  # fecha_necesidad
            json.dumps(data_json, ensure_ascii=False),  # data_json
            "pendiente_de_aprobacion",  # status
            "2",  # aprobador_id: Juan (usuario 2)
            None,  # planner_id
            25000,  # total_monto
            None,  # notificado_at
            now,  # created_at
            now  # updated_at
        ))
        con.commit()
        
        # Confirmar creación
        sol = con.execute(
            "SELECT id, id_usuario, aprobador_id, status, total_monto FROM solicitudes WHERE id=14"
        ).fetchone()
        
        print("✓ Solicitud 14 creada exitosamente")
        if sol:
            print(json.dumps(sol, indent=2, ensure_ascii=False, default=str))
        
        # Ver usuario 1 y usuario 2
        print("\n" + "=" * 60)
        print("USUARIO CREADOR (1 - Manuel)")
        print("=" * 60)
        u1 = con.execute("SELECT id_spm, nombre, rol FROM usuarios WHERE id_spm='1'").fetchone()
        print(json.dumps(u1, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 60)
        print("USUARIO APROBADOR (2 - Juan)")
        print("=" * 60)
        u2 = con.execute("SELECT id_spm, nombre, rol FROM usuarios WHERE id_spm='2'").fetchone()
        print(json.dumps(u2, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"✗ Error: {e}")
        con.rollback()
