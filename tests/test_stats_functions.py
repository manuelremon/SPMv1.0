#!/usr/bin/env python3
"""Test script para verificar que las funciones de stats.py funcionan correctamente"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.backend.services.dashboard.stats import (
    get_user_stats,
    get_dashboard_activity,
    get_chart_data
)

print("=" * 70)
print("PROBANDO FUNCIONES DE DASHBOARD")
print("=" * 70)

print("\n1. PROBANDO get_user_stats() para usuario '1'")
print("-" * 70)
try:
    stats = get_user_stats('1')
    print(f"✓ Solicitudes pendientes: {stats['pending']}")
    print(f"✓ Solicitudes aprobadas: {stats['approved']}")
    print(f"✓ Solicitudes en proceso: {stats['in_process']}")
    print(f"✓ Solicitudes rechazadas: {stats['rejected']}")
    print(f"✓ Total de materiales en catálogo: {stats['total_materials']}")
    print(f"✓ Tasa de aprobación: {stats['approval_rate']}%")
    print(f"✓ Solicitudes recientes: {len(stats['recent_requests'])}")
    for req in stats['recent_requests'][:2]:
        print(f"  - ID: {req['id']}, Status: {req['status']}, Título: {req['title'][:30]}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n2. PROBANDO get_dashboard_activity()")
print("-" * 70)
try:
    activity = get_dashboard_activity()
    print(f"✓ Actividades encontradas: {len(activity)}")
    for act in activity[:3]:
        print(f"  - ID: {act['id']}, Status: {act['status_text']}, Fecha: {act['date'][:10]}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n3. PROBANDO get_chart_data()")
print("-" * 70)
try:
    charts = get_chart_data()
    print(f"✓ Estados encontrados: {len(charts['states'])}")
    for state in charts['states']:
        print(f"  - {state['name']}: {state['count']} solicitudes")
    print(f"✓ Días en tendencia: {len(charts['trend'])}")
    print(f"  Día más activo: {max(charts['trend'], key=lambda x: x['count'])}")
    print(f"✓ Centros encontrados: {len(charts['centers'])}")
    for center in charts['centers'][:3]:
        print(f"  - {center['name']}: {center['count']}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("PRUEBAS COMPLETADAS")
print("=" * 70)
