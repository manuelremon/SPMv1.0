#!/usr/bin/env python3
"""Script para probar directamente la función get_user_stats sin HTTP"""
import sys
sys.path.insert(0, '/src')

from src.backend.services.dashboard.stats import get_user_stats, get_dashboard_activity, get_chart_data

print("=" * 70)
print("PROBANDO FUNCIONES DE ESTADÍSTICAS DIRECTAMENTE")
print("=" * 70)

print("\n1. Llamando a get_user_stats(1)")
print("-" * 70)
try:
    stats = get_user_stats(1)
    print("✓ get_user_stats(1) retornó:")
    print(f"  - pending: {stats.get('pending')}")
    print(f"  - approved: {stats.get('approved')}")
    print(f"  - in_process: {stats.get('in_process')}")
    print(f"  - rejected: {stats.get('rejected')}")
    print(f"  - total_materials: {stats.get('total_materials')}")
    print(f"  - approval_rate: {stats.get('approval_rate')}")
    print(f"  - recent_requests: {len(stats.get('recent_requests', []))} items")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Llamando a get_dashboard_activity()")
print("-" * 70)
try:
    activity = get_dashboard_activity()
    print(f"✓ get_dashboard_activity() retornó {len(activity)} items")
    for item in activity[:3]:
        print(f"  - ID {item.get('id')}: {item.get('title', 'N/A')[:40]}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Llamando a get_chart_data()")
print("-" * 70)
try:
    chart = get_chart_data()
    print(f"✓ get_chart_data() retornó:")
    print(f"  - states: {len(chart.get('states', []))} estados")
    for state in chart.get('states', []):
        print(f"    - {state.get('name')}: {state.get('count')}")
    print(f"  - trend: {len(chart.get('trend', []))} días")
    print(f"  - centers: {len(chart.get('centers', []))} centros")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)
