#!/usr/bin/env python3
"""
Generar datos de prueba inteligentes en tablas vacías
"""

import sqlite3
from datetime import datetime, timedelta
import random
import json

DB_PATH = "src/backend/core/data/spm.db"

print("=" * 80)
print("GENERANDO DATOS DE PRUEBA EN TABLAS VACÍAS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

# =====================================================================
# 1. PLANIFICADORES
# =====================================================================
print("\n📅 Insertando PLANIFICADORES...")
cursor.execute("""
    INSERT INTO planificadores (usuario_id, centro_id, sector_id, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", ('1', 1, 1, 'activo', datetime.now().isoformat(), datetime.now().isoformat()))
cursor.execute("""
    INSERT INTO planificadores (usuario_id, centro_id, sector_id, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", ('5', 2, 3, 'activo', datetime.now().isoformat(), datetime.now().isoformat()))
print("  ✓ 2 planificadores insertados")
conn.commit()

# =====================================================================
# 2. PLANIFICADOR_ASIGNACIONES
# =====================================================================
print("\n📋 Insertando PLANIFICADOR_ASIGNACIONES...")
cursor.execute("""
    INSERT INTO planificador_asignaciones (solicitud_id, planificador_id, estado, comentarios, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", (1, 1, 'asignado', 'Asignado para análisis de monto', datetime.now().isoformat(), datetime.now().isoformat()))
cursor.execute("""
    INSERT INTO planificador_asignaciones (solicitud_id, planificador_id, estado, comentarios, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", (3, 2, 'asignado', 'Asignado para verificación presupuesto', datetime.now().isoformat(), datetime.now().isoformat()))
print("  ✓ 2 asignaciones insertadas")
conn.commit()

# =====================================================================
# 3. SOLPEDS - Pedidos de Solicitud
# =====================================================================
print("\n📦 Insertando SOLPEDS (Pedidos de Solicitud)...")
# Para solicitud 1
cursor.execute("""
    INSERT INTO solpeds (solicitud_id, numero_pedido, material_codigo, cantidad, precio_unitario, 
                         total, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (1, 'PED-001-001', '1000000006', 4, 19567.38, 78269.52, 'pendiente', 
      datetime.now().isoformat(), datetime.now().isoformat()))

# Para solicitud 3
cursor.execute("""
    INSERT INTO solpeds (solicitud_id, numero_pedido, material_codigo, cantidad, precio_unitario, 
                         total, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (3, 'PED-003-001', '1000028839', 1, 16011.26, 16011.26, 'pendiente', 
      datetime.now().isoformat(), datetime.now().isoformat()))

# Para solicitud 4
cursor.execute("""
    INSERT INTO solpeds (solicitud_id, numero_pedido, material_codigo, cantidad, precio_unitario, 
                         total, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (4, 'PED-004-001', '1000557208', 1, 6229.56, 6229.56, 'pendiente', 
      datetime.now().isoformat(), datetime.now().isoformat()))

# Para solicitud 5
cursor.execute("""
    INSERT INTO solpeds (solicitud_id, numero_pedido, material_codigo, cantidad, precio_unitario, 
                         total, estado, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (5, 'PED-005-001', '1000556055', 1, 28996.26, 28996.26, 'pendiente', 
      datetime.now().isoformat(), datetime.now().isoformat()))

print("  ✓ 4 pedidos (solpeds) insertados")
conn.commit()

# =====================================================================
# 4. NOTIFICACIONES
# =====================================================================
print("\n🔔 Insertando NOTIFICACIONES...")
notificaciones = [
    (2, 'Solicitud #1 creada', 'Una nueva solicitud de material ha sido creada', 'solicitud_nueva', 1, 'no_leida'),
    (6, 'Solicitud #1 requiere aprobación', 'La solicitud #1 está pendiente de su aprobación', 'solicitud_pendiente', 1, 'no_leida'),
    (5, 'Solicitud #3 requiere aprobación', 'La solicitud #3 está pendiente de su aprobación', 'solicitud_pendiente', 3, 'no_leida'),
    (7, 'Nueva solicitud asignada', 'Se ha asignado una nueva solicitud para evaluar', 'solicitud_asignada', 5, 'leida'),
    (3, 'Presupuesto disponible', 'Presupuesto disponible en Mantenimiento: $100,090', 'presupuesto_info', None, 'leida'),
]

for usuario_id, titulo, mensaje, tipo, referencia_id, estado in notificaciones:
    cursor.execute("""
        INSERT INTO notificaciones (usuario_id, titulo, mensaje, tipo, referencia_id, estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (usuario_id, titulo, mensaje, tipo, referencia_id, estado, 
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(notificaciones)} notificaciones insertadas")
conn.commit()

# =====================================================================
# 5. OUTBOX_EMAILS
# =====================================================================
print("\n📧 Insertando OUTBOX_EMAILS...")
emails = [
    (2, 'juanlevi@ypf.com', 'Solicitud #1 creada', 'Su solicitud ha sido registrada en el sistema', 'pendiente'),
    (6, 'andresgarcia@ypf.com', 'Aprobación requerida', 'La solicitud #1 requiere su aprobación', 'pendiente'),
    (5, 'carlosperez@ypf.com', 'Aprobación requerida', 'La solicitud #3 requiere su aprobación', 'pendiente'),
]

for usuario_id, destinatario, asunto, cuerpo, estado in emails:
    cursor.execute("""
        INSERT INTO outbox_emails (usuario_id, destinatario, asunto, cuerpo, estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usuario_id, destinatario, asunto, cuerpo, estado, 
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(emails)} emails insertados")
conn.commit()

# =====================================================================
# 6. ARCHIVOS_ADJUNTOS
# =====================================================================
print("\n📎 Insertando ARCHIVOS_ADJUNTOS...")
archivos = [
    (1, 'Justificacion_Solicitud_1.pdf', 'application/pdf', 245600, 'justificacion'),
    (1, 'Presupuesto_Proveedor.xlsx', 'application/vnd.ms-excel', 125400, 'presupuesto'),
    (3, 'Especificaciones_Tecnicas.pdf', 'application/pdf', 89300, 'especificacion'),
]

for solicitud_id, nombre_archivo, tipo_archivo, tamaño, tipo in archivos:
    cursor.execute("""
        INSERT INTO archivos_adjuntos (solicitud_id, nombre_archivo, tipo_archivo, tamaño, tipo, 
                                      ruta_archivo, estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (solicitud_id, nombre_archivo, tipo_archivo, tamaño, tipo, 
          f'/uploads/solicitud_{solicitud_id}/{nombre_archivo}', 'activo',
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(archivos)} archivos insertados")
conn.commit()

# =====================================================================
# 7. PRESUPUESTO_INCORPORACIONES
# =====================================================================
print("\n💵 Insertando PRESUPUESTO_INCORPORACIONES...")
incorporaciones = [
    (1, 1, 50000, 'Ampliación de presupuesto solicitud 1', 'aprobado'),
    (2, 3, 30000, 'Ampliación para mantenimiento preventivo', 'pendiente'),
]

for presupuesto_id, solicitud_id, monto, descripcion, estado in incorporaciones:
    cursor.execute("""
        INSERT INTO presupuesto_incorporaciones (presupuesto_id, solicitud_id, monto, descripcion, 
                                                estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (presupuesto_id, solicitud_id, monto, descripcion, estado,
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(incorporaciones)} incorporaciones de presupuesto insertadas")
conn.commit()

# =====================================================================
# 8. PURCHASE_ORDERS (Órdenes de Compra)
# =====================================================================
print("\n🛒 Insertando PURCHASE_ORDERS...")
pos = [
    (1, 'OP-2025-001', 'PED-001-001', 1, 78269.52, 'abierta'),
    (3, 'OP-2025-002', 'PED-003-001', 1, 16011.26, 'abierta'),
    (4, 'OP-2025-003', 'PED-004-001', 1, 6229.56, 'abierta'),
    (5, 'OP-2025-004', 'PED-005-001', 1, 28996.26, 'abierta'),
]

for solicitud_id, numero_po, numero_pedido, centro_id, monto, estado in pos:
    cursor.execute("""
        INSERT INTO purchase_orders (solicitud_id, numero_po, numero_pedido, centro_id, monto, 
                                    estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (solicitud_id, numero_po, numero_pedido, centro_id, monto, estado,
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(pos)} órdenes de compra insertadas")
conn.commit()

# =====================================================================
# 9. TRASLADOS
# =====================================================================
print("\n🚚 Insertando TRASLADOS...")
traslados = [
    (1, 'TAL-2025-001', 'centro_origen_1', 'centro_destino_2', 78269.52, 'en_transito', 
     datetime.now().isoformat(), (datetime.now() + timedelta(days=3)).isoformat()),
    (3, 'TAL-2025-002', 'centro_origen_1', 'centro_destino_3', 16011.26, 'pendiente',
     datetime.now().isoformat(), (datetime.now() + timedelta(days=5)).isoformat()),
]

for solicitud_id, numero_traslado, origen, destino, monto, estado, fecha_inicio, fecha_estimada in traslados:
    cursor.execute("""
        INSERT INTO traslados (solicitud_id, numero_traslado, centro_origen, centro_destino, monto, 
                              estado, fecha_inicio, fecha_estimada, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (solicitud_id, numero_traslado, origen, destino, monto, estado, fecha_inicio, fecha_estimada,
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(traslados)} traslados insertados")
conn.commit()

# =====================================================================
# 10. USER_PROFILE_REQUESTS
# =====================================================================
print("\n👤 Insertando USER_PROFILE_REQUESTS...")
profile_reqs = [
    (2, 'actualizar_departamento', 'Solicitar cambio a Compras', 'pendiente'),
    (3, 'cambiar_centro', 'Solicitar cambio a centro 1500', 'aprobado'),
    (4, 'elevar_permisos', 'Solicitar permisos de aprobador', 'pendiente'),
]

for usuario_id, tipo, descripcion, estado in profile_reqs:
    cursor.execute("""
        INSERT INTO user_profile_requests (usuario_id, tipo, descripcion, estado, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (usuario_id, tipo, descripcion, estado,
          datetime.now().isoformat(), datetime.now().isoformat()))

print(f"  ✓ {len(profile_reqs)} solicitudes de perfil insertadas")
conn.commit()

# =====================================================================
# 11. SOLICITUD_ITEMS_TRATAMIENTO
# =====================================================================
print("\n📌 Insertando SOLICITUD_ITEMS_TRATAMIENTO...")
items_tratamiento = [
    (1, 1, 'Revisión de monto', 'En revisión', datetime.now().isoformat()),
    (1, 2, 'Validación de disponibilidad', 'En revisión', (datetime.now() + timedelta(hours=1)).isoformat()),
    (3, 1, 'Revisión de justificación', 'En revisión', datetime.now().isoformat()),
]

for solicitud_id, orden, descripcion, estado, created_at in items_tratamiento:
    cursor.execute("""
        INSERT INTO solicitud_items_tratamiento (solicitud_id, orden, descripcion, estado, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (solicitud_id, orden, descripcion, estado, created_at))

print(f"  ✓ {len(items_tratamiento)} items de tratamiento insertados")
conn.commit()

# =====================================================================
# 12. SOLICITUD_TRATAMIENTO_LOG
# =====================================================================
print("\n📊 Insertando SOLICITUD_TRATAMIENTO_LOG...")
logs = [
    (1, 'creacion', 'Solicitud creada por usuario 2', datetime.now().isoformat()),
    (1, 'envio_aprobador', 'Enviada a aprobador Andres Garcia', (datetime.now() + timedelta(minutes=5)).isoformat()),
    (3, 'creacion', 'Solicitud creada por usuario 2', (datetime.now() - timedelta(hours=2)).isoformat()),
]

for solicitud_id, tipo_evento, descripcion, timestamp in logs:
    cursor.execute("""
        INSERT INTO solicitud_tratamiento_log (solicitud_id, tipo_evento, descripcion, timestamp)
        VALUES (?, ?, ?, ?)
    """, (solicitud_id, tipo_evento, descripcion, timestamp))

print(f"  ✓ {len(logs)} logs de tratamiento insertados")
conn.commit()

# =====================================================================
# 13. SOLICITUD_TRATAMIENTO_EVENTOS
# =====================================================================
print("\n⚡ Insertando SOLICITUD_TRATAMIENTO_EVENTOS...")
eventos = [
    (1, 'aprobacion_requerida', 'Solicitud enviada para aprobación', '6', 
     datetime.now().isoformat(), 'pendiente'),
    (3, 'revision_presupuesto', 'En revisión de disponibilidad presupuestaria', '5',
     (datetime.now() + timedelta(hours=1)).isoformat(), 'en_progreso'),
]

for solicitud_id, tipo_evento, descripcion, usuario_id, fecha_evento, estado in eventos:
    cursor.execute("""
        INSERT INTO solicitud_tratamiento_eventos (solicitud_id, tipo_evento, descripcion, 
                                                  usuario_id, fecha_evento, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (solicitud_id, tipo_evento, descripcion, usuario_id, fecha_evento, estado))

print(f"  ✓ {len(eventos)} eventos de tratamiento insertados")
conn.commit()

# =====================================================================
# ESTADÍSTICAS FINALES
# =====================================================================
print("\n" + "=" * 80)
print("✅ GENERACIÓN DE DATOS DE PRUEBA COMPLETADA")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM planificadores")
print(f"\n📅 Planificadores: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM planificador_asignaciones")
print(f"📋 Planificador asignaciones: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM solpeds")
print(f"📦 Pedidos (solpeds): {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM notificaciones")
print(f"🔔 Notificaciones: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM outbox_emails")
print(f"📧 Emails: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM archivos_adjuntos")
print(f"📎 Archivos: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM presupuesto_incorporaciones")
print(f"💵 Incorporaciones de presupuesto: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM purchase_orders")
print(f"🛒 Órdenes de compra: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM traslados")
print(f"🚚 Traslados: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM user_profile_requests")
print(f"👤 Solicitudes de perfil: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM solicitud_items_tratamiento")
print(f"📌 Items de tratamiento: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM solicitud_tratamiento_log")
print(f"📊 Logs: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM solicitud_tratamiento_eventos")
print(f"⚡ Eventos: {cursor.fetchone()[0]}")

print("\n✨ Todas las tablas vacías han sido pobladas con datos de prueba coherentes.\n")

conn.close()
