#!/usr/bin/env python
"""
Crear solicitud 15 con centros, sectores y almacenes que coincidan con configuración real.
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
    
    now = datetime.utcnow().isoformat()
    
    # Crear solicitud 15 con:
    # - id_usuario: "1" (Manuel)
    # - centro: "1008" (configurado en planificador_asignaciones)
    # - sector: "Mantenimiento" (configurado)
    # - almacen_virtual: "ALM0001" (configurado)
    # - aprobador_id: "2" (Juan - el superior)
    
    data_json = {
        "items": [
            {"material": "Repuesto hidráulico", "cantidad": 20, "costo_unitario": 500, "total": 10000},
            {"material": "Aceite sintético 5L", "cantidad": 30, "costo_unitario": 300, "total": 9000},
        ],
        "total": 19000
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
            "1008",  # centro: configurado
            "Mantenimiento",  # sector: configurado
            "Solicitud de repuestos de mantenimiento",  # justificacion
            "CC001",  # centro_costos
            "ALM0001",  # almacen_virtual: configurado
            "Normal",  # criticidad
            None,  # fecha_necesidad
            json.dumps(data_json, ensure_ascii=False),  # data_json
            "pendiente_de_aprobacion",  # status
            "2",  # aprobador_id: Juan
            None,  # planner_id
            19000,  # total_monto
            None,  # notificado_at
            now,  # created_at
            now  # updated_at
        ))
        con.commit()
        
        # Confirmar creación
        sol = con.execute(
            "SELECT id, id_usuario, centro, sector, almacen_virtual, aprobador_id, status, total_monto FROM solicitudes WHERE id=15"
        ).fetchone()
        
        print("=" * 60)
        print("✓ SOLICITUD 15 CREADA EXITOSAMENTE")
        print("=" * 60)
        print(json.dumps(sol, indent=2, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"✗ Error: {e}")
        con.rollback()
