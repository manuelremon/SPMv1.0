"""
Test del Filtro Técnico-Legal
Valida lógica de rechazo y aceptación
"""

from datetime import datetime, timedelta
from src.planner.models import (
    ItemMaster, SourcingOption, SourcingPath,
    InventoryLot, QCStatus, LotLocation
)
from src.planner.filters import TechnicalLegalFilter, FilterReason


def test_filter_expired_lot():
    """Test: Rechaza lote vencido"""
    filter_obj = TechnicalLegalFilter()
    
    # Crear lote vencido
    expired_lot = InventoryLot(
        lot_number="LOT-001-EXP",
        item_id="MAT-001",
        quantity_received=100,
        quantity_on_hand=100,
        receipt_date=datetime.utcnow() - timedelta(days=400),
        expiration_date=datetime.utcnow() - timedelta(days=30),  # Vencido hace 30 días
        supplier_id="SUP-001",
        purchase_order="PO-001",
        qc_status=QCStatus.APPROVED,
        locations=[
            LotLocation(warehouse_code="ALM-1", zone="STK", rack="A", level=1, position="01")
        ]
    )
    
    # Crear opción de stock
    option = SourcingOption(
        option_id="MAT-001:STOCK_LOCAL:NONE",
        item_id="MAT-001",
        sourcing_path="STOCK_LOCAL",
        quantity_available=100,
        unit_of_measure="EA",
        unit_cost_usd=0,
        lead_time_days_mean=0
    )
    
    # Crear item
    item = ItemMaster(
        item_id="MAT-001",
        sap_code="100001",
        description="Rodamiento",
        base_unit="EA"
    )
    
    # Aplicar filtro
    result = filter_obj.filter_option(option, item, inventory_lot=expired_lot)
    
    assert result.feasible == False, "Debe rechazar lote vencido"
    assert FilterReason.EXPIRED in result.reasons, "Debe incluir razón EXPIRED"
    print("✅ Test: Rechaza lote vencido - PASSED")


def test_filter_traceability_required():
    """Test: Rechaza opciones equivalentes si se requiere trazabilidad"""
    filter_obj = TechnicalLegalFilter()
    
    # Crear item que requiere trazabilidad
    item = ItemMaster(
        item_id="MAT-PHARMA",
        sap_code="200001",
        description="Medicamento controlado",
        base_unit="EA",
        requires_traceability=True
    )
    
    # Crear opción equivalente (sin trazabilidad garantizada)
    option = SourcingOption(
        option_id="MAT-PHARMA:EQUIVALENT:SUP-001",
        item_id="MAT-PHARMA",
        sourcing_path="EQUIVALENT",
        supplier_id="SUP-001",
        quantity_available=50,
        unit_of_measure="EA",
        unit_cost_usd=8.50,
        lead_time_days_mean=5
    )
    
    # Aplicar filtro
    result = filter_obj.filter_option(option, item)
    
    assert result.feasible == False, "Debe rechazar equivalente sin trazabilidad"
    assert FilterReason.TRACEABILITY_REQUIRED in result.reasons
    print("✅ Test: Rechaza opciones sin trazabilidad - PASSED")


def test_filter_compliance_violation():
    """Test: Rechaza si falta norma de cumplimiento"""
    filter_obj = TechnicalLegalFilter()
    
    # Establecer requisito normativo
    filter_obj.set_regulatory_requirements("MAT-FDA", ["ISO-13485", "FDA-21-CFR"])
    
    # Crear item sin certificaciones requeridas
    item = ItemMaster(
        item_id="MAT-FDA",
        sap_code="300001",
        description="Dispositivo médico",
        base_unit="EA",
        compliance_standards=["ISO-9001"]  # Solo tiene ISO-9001, le faltan ISO-13485 y FDA-21-CFR
    )
    
    # Crear opción de compra
    option = SourcingOption(
        option_id="MAT-FDA:PURCHASE:SUP-MED",
        item_id="MAT-FDA",
        sourcing_path="PURCHASE",
        supplier_id="SUP-MED",
        quantity_available=500,
        unit_of_measure="EA",
        unit_cost_usd=25.00,
        lead_time_days_mean=21
    )
    
    # Aplicar filtro
    result = filter_obj.filter_option(option, item)
    
    assert result.feasible == False, "Debe rechazar por falta de normas"
    assert FilterReason.COMPLIANCE_VIOLATION in result.reasons
    print("✅ Test: Rechaza incumplimiento normativo - PASSED")


def test_filter_supplier_suspended():
    """Test: Rechaza proveedor suspendido"""
    filter_obj = TechnicalLegalFilter()
    filter_obj.register_supplier_as_suspended("SUP-BAD")
    
    item = ItemMaster(
        item_id="MAT-001",
        sap_code="100001",
        description="Material",
        base_unit="EA"
    )
    
    option = SourcingOption(
        option_id="MAT-001:PURCHASE:SUP-BAD",
        item_id="MAT-001",
        sourcing_path="PURCHASE",
        supplier_id="SUP-BAD",
        quantity_available=100,
        unit_of_measure="EA",
        unit_cost_usd=10.00,
        lead_time_days_mean=14
    )
    
    result = filter_obj.filter_option(option, item)
    
    assert result.feasible == False, "Debe rechazar proveedor suspendido"
    assert FilterReason.SUPPLIER_SUSPENDED in result.reasons
    print("✅ Test: Rechaza proveedor suspendido - PASSED")


def test_filter_lead_time_violation():
    """Test: Rechaza si lead time excede fecha requerida"""
    filter_obj = TechnicalLegalFilter()
    
    item = ItemMaster(
        item_id="MAT-001",
        sap_code="100001",
        description="Material",
        base_unit="EA"
    )
    
    # Requerido en 5 días
    required_date = datetime.utcnow() + timedelta(days=5)
    
    # Opción con lead time de 14 días (no cabe)
    option = SourcingOption(
        option_id="MAT-001:PURCHASE:SUP-001",
        item_id="MAT-001",
        sourcing_path="PURCHASE",
        supplier_id="SUP-001",
        quantity_available=100,
        unit_of_measure="EA",
        unit_cost_usd=10.00,
        lead_time_days_mean=14.0
    )
    
    result = filter_obj.filter_option(option, item, required_date=required_date)
    
    assert result.feasible == False, "Debe rechazar por incumplimiento de lead time"
    assert FilterReason.LEAD_TIME_VIOLATION in result.reasons
    print("✅ Test: Rechaza incumplimiento de lead time - PASSED")


def test_filter_path_multiple_options():
    """Test: Filtrar ruta con múltiples opciones"""
    filter_obj = TechnicalLegalFilter()
    filter_obj.register_supplier_as_suspended("SUP-BAD")
    
    item = ItemMaster(
        item_id="MAT-001",
        sap_code="100001",
        description="Material",
        base_unit="EA"
    )
    
    # Crear ruta con 3 opciones
    path = SourcingPath(
        path_id="SOL-001:MAT-001",
        solicitud_id="SOL-001",
        material_id="MAT-001",
        required_quantity=100,
        required_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Opción 1: Stock local (viable)
    opt1 = SourcingOption(
        option_id="MAT-001:STOCK_LOCAL:NONE",
        item_id="MAT-001",
        sourcing_path="STOCK_LOCAL",
        quantity_available=50,
        unit_of_measure="EA",
        unit_cost_usd=0,
        lead_time_days_mean=0
    )
    
    # Opción 2: Proveedor suspendido (rechazada)
    opt2 = SourcingOption(
        option_id="MAT-001:PURCHASE:SUP-BAD",
        item_id="MAT-001",
        sourcing_path="PURCHASE",
        supplier_id="SUP-BAD",
        quantity_available=100,
        unit_of_measure="EA",
        unit_cost_usd=10.00,
        lead_time_days_mean=14
    )
    
    # Opción 3: Proveedor bueno (viable)
    opt3 = SourcingOption(
        option_id="MAT-001:PURCHASE:SUP-GOOD",
        item_id="MAT-001",
        sourcing_path="PURCHASE",
        supplier_id="SUP-GOOD",
        quantity_available=100,
        unit_of_measure="EA",
        unit_cost_usd=11.00,
        lead_time_days_mean=14
    )
    
    path.add_option(opt1)
    path.add_option(opt2)
    path.add_option(opt3)
    
    # Filtrar ruta
    filtered_path = filter_obj.filter_path(path, item)
    
    # Verificar resultados
    feasible = filter_obj.get_feasible_options(filtered_path)
    assert len(feasible) == 2, "Debe tener 2 opciones viables"
    assert feasible[0].option_id == "MAT-001:STOCK_LOCAL:NONE"
    assert feasible[1].option_id == "MAT-001:PURCHASE:SUP-GOOD"
    
    # Verificar reporte
    report = filter_obj.generate_filter_report(filtered_path)
    assert report["feasible_count"] == 2
    assert report["infeasible_count"] == 1
    assert report["feasibility_rate"] == 2/3
    
    print("✅ Test: Filtrar ruta con múltiples opciones - PASSED")
    print(f"   Reporte: {report['feasible_count']}/{report['total_options']} opciones viables")


if __name__ == "__main__":
    test_filter_expired_lot()
    test_filter_traceability_required()
    test_filter_compliance_violation()
    test_filter_supplier_suspended()
    test_filter_lead_time_violation()
    test_filter_path_multiple_options()
    print("\n✅ Todos los tests pasaron")
