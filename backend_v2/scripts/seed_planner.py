"""
Script de seeding para tablas de Planner.

Crea datos de prueba para:
- 15 items (3 CRITICAL, 5 HIGH, 7 MEDIUM/LOW)
- 5 suppliers con acuerdos de precio
- 3 warehouses con conectividad
- 20 lotes de inventario
- 5 BOMs con componentes
- 10 ítems equivalentes
"""

import sys
from pathlib import Path

# Agregar backend_v2 al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from core.db import engine, Base
from models.planner import (
    ItemMaster, BOMComponent, EquivalentItem,
    InventoryLot, LotLocation,
    Supplier, SupplierPriceAgreement,
    Warehouse,
    ABCClassification, ItemCriticality, ProcurementType,
    QCStatus, SupplierRating, WarehouseType
)


def seed_items(session: Session):
    """Crea 15 items de ejemplo"""
    items = [
        # CRITICAL items (3)
        ItemMaster(
            item_id="ITEM-001", sap_code="MAT-001", 
            description="Válvula de presión crítica",
            abc_class=ABCClassification.A, criticality=ItemCriticality.CRITICAL,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=450.0, list_price_usd=600.0,
            minimum_order_quantity=1.0, safety_stock_days=30
        ),
        ItemMaster(
            item_id="ITEM-002", sap_code="MAT-002",
            description="Sensor de temperatura industrial",
            abc_class=ABCClassification.A, criticality=ItemCriticality.CRITICAL,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=280.0, list_price_usd=380.0,
            minimum_order_quantity=2.0, safety_stock_days=20
        ),
        ItemMaster(
            item_id="ITEM-003", sap_code="MAT-003",
            description="Motor eléctrico 15HP",
            abc_class=ABCClassification.A, criticality=ItemCriticality.CRITICAL,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=1200.0, list_price_usd=1650.0,
            minimum_order_quantity=1.0, safety_stock_days=45,
            is_assembly=True
        ),
        
        # HIGH priority items (5)
        ItemMaster(
            item_id="ITEM-004", sap_code="MAT-004",
            description="Rodamiento industrial SKF",
            abc_class=ABCClassification.A, criticality=ItemCriticality.HIGH,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=85.0, list_price_usd=120.0,
            minimum_order_quantity=5.0, safety_stock_days=15
        ),
        ItemMaster(
            item_id="ITEM-005", sap_code="MAT-005",
            description="Cable eléctrico 3x2.5mm",
            abc_class=ABCClassification.B, criticality=ItemCriticality.HIGH,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="M", standard_cost_usd=3.5, list_price_usd=5.2,
            minimum_order_quantity=100.0, order_multiple=100.0
        ),
        ItemMaster(
            item_id="ITEM-006", sap_code="MAT-006",
            description="Filtro de aceite hidráulico",
            abc_class=ABCClassification.B, criticality=ItemCriticality.HIGH,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=45.0, list_price_usd=68.0,
            minimum_order_quantity=10.0, safety_stock_days=10
        ),
        ItemMaster(
            item_id="ITEM-007", sap_code="MAT-007",
            description="Empaque de junta tórica NBR",
            abc_class=ABCClassification.C, criticality=ItemCriticality.HIGH,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=2.5, list_price_usd=4.5,
            minimum_order_quantity=50.0, order_multiple=50.0
        ),
        ItemMaster(
            item_id="ITEM-008", sap_code="MAT-008",
            description="Aceite lubricante sintético 5L",
            abc_class=ABCClassification.B, criticality=ItemCriticality.HIGH,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="LT", standard_cost_usd=25.0, list_price_usd=38.0,
            minimum_order_quantity=20.0, shelf_life_days=365
        ),
        
        # MEDIUM/LOW priority items (7)
        ItemMaster(
            item_id="ITEM-009", sap_code="MAT-009",
            description="Tornillo hexagonal M12x40",
            abc_class=ABCClassification.C, criticality=ItemCriticality.MEDIUM,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=0.45, list_price_usd=0.85,
            minimum_order_quantity=100.0, order_multiple=100.0
        ),
        ItemMaster(
            item_id="ITEM-010", sap_code="MAT-010",
            description="Tuerca hexagonal M12",
            abc_class=ABCClassification.C, criticality=ItemCriticality.MEDIUM,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=0.25, list_price_usd=0.55,
            minimum_order_quantity=200.0, order_multiple=100.0
        ),
        ItemMaster(
            item_id="ITEM-011", sap_code="MAT-011",
            description="Arandela plana M12",
            abc_class=ABCClassification.C, criticality=ItemCriticality.LOW,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=0.15, list_price_usd=0.35,
            minimum_order_quantity=500.0, order_multiple=100.0
        ),
        ItemMaster(
            item_id="ITEM-012", sap_code="MAT-012",
            description="Grasa multiuso 500g",
            abc_class=ABCClassification.C, criticality=ItemCriticality.LOW,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="KG", standard_cost_usd=8.5, list_price_usd=14.0,
            minimum_order_quantity=10.0
        ),
        ItemMaster(
            item_id="ITEM-013", sap_code="MAT-013",
            description="Cinta aislante 19mm x 20m",
            abc_class=ABCClassification.C, criticality=ItemCriticality.LOW,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="EA", standard_cost_usd=2.2, list_price_usd=4.0,
            minimum_order_quantity=20.0
        ),
        ItemMaster(
            item_id="ITEM-014", sap_code="MAT-014",
            description="Guante de seguridad nitrilo",
            abc_class=ABCClassification.C, criticality=ItemCriticality.LOW,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="PAR", standard_cost_usd=3.8, list_price_usd=6.5,
            minimum_order_quantity=50.0, order_multiple=10.0
        ),
        ItemMaster(
            item_id="ITEM-015", sap_code="MAT-015",
            description="Pintura anticorrosiva 1L",
            abc_class=ABCClassification.C, criticality=ItemCriticality.LOW,
            procurement_type=ProcurementType.PURCHASE,
            base_unit="LT", standard_cost_usd=15.0, list_price_usd=24.0,
            minimum_order_quantity=12.0, shelf_life_days=180
        ),
    ]
    
    session.add_all(items)
    session.commit()
    print(f"✅ Created {len(items)} items")
    return items


def seed_suppliers(session: Session, items: list):
    """Crea 5 suppliers con acuerdos de precio"""
    suppliers = [
        Supplier(
            supplier_id="SUP-001", supplier_code="PROV-001",
            name="Válvulas Industriales SA",
            contact_name="Juan Pérez", contact_email="jperez@valvulas.com",
            rating=SupplierRating.PREFERRED,
            reliability_score=0.95, quality_score=0.98, on_time_delivery_rate=0.97,
            average_lead_time_days=10, payment_terms_days=30
        ),
        Supplier(
            supplier_id="SUP-002", supplier_code="PROV-002",
            name="Electromecánica del Sur",
            contact_name="María López", contact_email="mlopez@electrosur.com",
            rating=SupplierRating.APPROVED,
            reliability_score=0.90, quality_score=0.92, on_time_delivery_rate=0.88,
            average_lead_time_days=15, payment_terms_days=45
        ),
        Supplier(
            supplier_id="SUP-003", supplier_code="PROV-003",
            name="Distribuidora SKF Argentina",
            contact_name="Carlos Rodríguez", contact_email="crodriguez@skfar.com",
            rating=SupplierRating.PREFERRED,
            reliability_score=0.98, quality_score=0.99, on_time_delivery_rate=0.96,
            average_lead_time_days=7, payment_terms_days=30
        ),
        Supplier(
            supplier_id="SUP-004", supplier_code="PROV-004",
            name="Bulonería y Ferretería Industrial",
            contact_name="Ana Martínez", contact_email="amartinez@buloneria.com",
            rating=SupplierRating.APPROVED,
            reliability_score=0.85, quality_score=0.88, on_time_delivery_rate=0.92,
            average_lead_time_days=20, payment_terms_days=60
        ),
        Supplier(
            supplier_id="SUP-005", supplier_code="PROV-005",
            name="Lubricantes y Químicos SA",
            contact_name="Roberto Gómez", contact_email="rgomez@lubquim.com",
            rating=SupplierRating.APPROVED,
            reliability_score=0.87, quality_score=0.90, on_time_delivery_rate=0.85,
            average_lead_time_days=12, payment_terms_days=45
        ),
    ]
    
    session.add_all(suppliers)
    session.commit()
    print(f"✅ Created {len(suppliers)} suppliers")
    
    # Crear price agreements
    today = datetime.now(UTC)
    agreements = [
        # SUP-001: Items críticos
        SupplierPriceAgreement(supplier_id=1, item_id="ITEM-001", unit_price_usd=420.0, moq=1.0, lead_time_days=10, valid_from=today, valid_to=today + timedelta(days=365)),
        SupplierPriceAgreement(supplier_id=1, item_id="ITEM-002", unit_price_usd=260.0, moq=2.0, lead_time_days=12, valid_from=today, valid_to=today + timedelta(days=365)),
        
        # SUP-002: Motor
        SupplierPriceAgreement(supplier_id=2, item_id="ITEM-003", unit_price_usd=1150.0, moq=1.0, lead_time_days=15, valid_from=today, valid_to=today + timedelta(days=180)),
        SupplierPriceAgreement(supplier_id=2, item_id="ITEM-005", unit_price_usd=3.2, moq=100.0, lead_time_days=7, valid_from=today),
        
        # SUP-003: Rodamientos
        SupplierPriceAgreement(supplier_id=3, item_id="ITEM-004", unit_price_usd=78.0, moq=5.0, lead_time_days=5, valid_from=today, valid_to=today + timedelta(days=365)),
        
        # SUP-004: Ferretería
        SupplierPriceAgreement(supplier_id=4, item_id="ITEM-009", unit_price_usd=0.40, moq=100.0, lead_time_days=20, valid_from=today),
        SupplierPriceAgreement(supplier_id=4, item_id="ITEM-010", unit_price_usd=0.22, moq=200.0, lead_time_days=20, valid_from=today),
        SupplierPriceAgreement(supplier_id=4, item_id="ITEM-011", unit_price_usd=0.12, moq=500.0, lead_time_days=15, valid_from=today),
        
        # SUP-005: Lubricantes
        SupplierPriceAgreement(supplier_id=5, item_id="ITEM-006", unit_price_usd=42.0, moq=10.0, lead_time_days=10, valid_from=today),
        SupplierPriceAgreement(supplier_id=5, item_id="ITEM-008", unit_price_usd=23.0, moq=20.0, lead_time_days=8, valid_from=today),
        SupplierPriceAgreement(supplier_id=5, item_id="ITEM-012", unit_price_usd=7.8, moq=10.0, lead_time_days=12, valid_from=today),
    ]
    
    session.add_all(agreements)
    session.commit()
    print(f"✅ Created {len(agreements)} price agreements")
    
    return suppliers


def seed_warehouses(session: Session):
    """Crea 3 warehouses con conectividad"""
    warehouses = [
        Warehouse(
            warehouse_id="WH-001", warehouse_code="ALM-CENTRAL",
            name="Almacén Central Buenos Aires",
            warehouse_type=WarehouseType.CENTRAL,
            location="Buenos Aires", latitude=-34.6037, longitude=-58.3816,
            total_capacity_pallets=500, utilization_rate=0.75,
            picking_cost_per_hour=30.0, packing_cost_per_hour=25.0,
            shipping_cost_per_hour=40.0, coordination_cost_per_hour=45.0,
            operates_24_7=True, working_hours_per_day=24,
            reliability_score=0.98, on_time_shipping_rate=0.96,
            connections={
                "WH-002": {"distance_km": 350, "transit_days": 2},
                "WH-003": {"distance_km": 800, "transit_days": 3}
            }
        ),
        Warehouse(
            warehouse_id="WH-002", warehouse_code="ALM-SUR",
            name="Almacén Regional Sur",
            warehouse_type=WarehouseType.REGIONAL,
            location="Comodoro Rivadavia", latitude=-45.8644, longitude=-67.4806,
            total_capacity_pallets=200, utilization_rate=0.60,
            picking_cost_per_hour=25.0, packing_cost_per_hour=20.0,
            shipping_cost_per_hour=35.0, coordination_cost_per_hour=40.0,
            operates_24_7=False, working_hours_per_day=8,
            reliability_score=0.92, on_time_shipping_rate=0.88,
            connections={
                "WH-001": {"distance_km": 350, "transit_days": 2},
                "WH-003": {"distance_km": 1200, "transit_days": 4}
            }
        ),
        Warehouse(
            warehouse_id="WH-003", warehouse_code="ALM-NORTE",
            name="Almacén Regional Norte",
            warehouse_type=WarehouseType.REGIONAL,
            location="Mendoza", latitude=-32.8895, longitude=-68.8458,
            total_capacity_pallets=150, utilization_rate=0.50,
            picking_cost_per_hour=25.0, packing_cost_per_hour=20.0,
            shipping_cost_per_hour=35.0, coordination_cost_per_hour=40.0,
            operates_24_7=False, working_hours_per_day=8,
            reliability_score=0.90, on_time_shipping_rate=0.85,
            connections={
                "WH-001": {"distance_km": 800, "transit_days": 3},
                "WH-002": {"distance_km": 1200, "transit_days": 4}
            }
        ),
    ]
    
    session.add_all(warehouses)
    session.commit()
    print(f"✅ Created {len(warehouses)} warehouses")
    return warehouses


def seed_inventory(session: Session, items: list):
    """Crea 20 lotes de inventario"""
    today = datetime.now(UTC)
    
    lots = [
        # Items críticos con stock
        InventoryLot(
            lot_number="LOT-001-2025-01", item_id=1,
            quantity_received=10.0, quantity_on_hand=8.0, quantity_reserved_hard=2.0,
            receipt_date=today - timedelta(days=30), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-001", purchase_order="PO-2024-1001"
        ),
        InventoryLot(
            lot_number="LOT-002-2025-01", item_id=2,
            quantity_received=15.0, quantity_on_hand=12.0, quantity_reserved_soft=3.0,
            receipt_date=today - timedelta(days=20), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-001", purchase_order="PO-2024-1002"
        ),
        InventoryLot(
            lot_number="LOT-003-2025-01", item_id=3,
            quantity_received=5.0, quantity_on_hand=3.0, quantity_allocated=2.0,
            receipt_date=today - timedelta(days=45), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-002", purchase_order="PO-2024-1003"
        ),
        
        # Rodamientos
        InventoryLot(
            lot_number="LOT-004-2025-01", item_id=4,
            quantity_received=50.0, quantity_on_hand=38.0, quantity_reserved_hard=10.0,
            receipt_date=today - timedelta(days=15), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-003", purchase_order="PO-2024-1004"
        ),
        InventoryLot(
            lot_number="LOT-004-2024-12", item_id=4,
            quantity_received=50.0, quantity_on_hand=5.0, quantity_allocated=45.0,
            receipt_date=today - timedelta(days=60), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-003", purchase_order="PO-2024-0980"
        ),
        
        # Cable eléctrico
        InventoryLot(
            lot_number="LOT-005-2025-01", item_id=5,
            quantity_received=500.0, quantity_on_hand=320.0, quantity_reserved_hard=100.0,
            receipt_date=today - timedelta(days=25), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-002", purchase_order="PO-2024-1005"
        ),
        
        # Filtros
        InventoryLot(
            lot_number="LOT-006-2025-01", item_id=6,
            quantity_received=100.0, quantity_on_hand=75.0, quantity_reserved_soft=15.0,
            receipt_date=today - timedelta(days=10), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-005", purchase_order="PO-2024-1006"
        ),
        
        # Empaques
        InventoryLot(
            lot_number="LOT-007-2025-01", item_id=7,
            quantity_received=200.0, quantity_on_hand=150.0, quantity_reserved_hard=30.0,
            receipt_date=today - timedelta(days=5), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-001", purchase_order="PO-2025-0001"
        ),
        
        # Aceite (con vencimiento)
        InventoryLot(
            lot_number="LOT-008-2024-11", item_id=8,
            quantity_received=100.0, quantity_on_hand=45.0, quantity_allocated=55.0,
            receipt_date=today - timedelta(days=90), 
            expiration_date=today + timedelta(days=275),
            shelf_life_days=365,
            qc_status=QCStatus.APPROVED,
            supplier_id="SUP-005", purchase_order="PO-2024-0850"
        ),
        InventoryLot(
            lot_number="LOT-008-2025-01", item_id=8,
            quantity_received=100.0, quantity_on_hand=95.0, quantity_reserved_soft=5.0,
            receipt_date=today - timedelta(days=15),
            expiration_date=today + timedelta(days=350),
            shelf_life_days=365,
            qc_status=QCStatus.APPROVED,
            supplier_id="SUP-005", purchase_order="PO-2025-0005"
        ),
        
        # Tornillería
        InventoryLot(
            lot_number="LOT-009-2024-12", item_id=9,
            quantity_received=1000.0, quantity_on_hand=580.0, quantity_allocated=420.0,
            receipt_date=today - timedelta(days=50), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-004", purchase_order="PO-2024-0900"
        ),
        InventoryLot(
            lot_number="LOT-010-2024-12", item_id=10,
            quantity_received=1000.0, quantity_on_hand=650.0, quantity_allocated=350.0,
            receipt_date=today - timedelta(days=50), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-004", purchase_order="PO-2024-0901"
        ),
        InventoryLot(
            lot_number="LOT-011-2025-01", item_id=11,
            quantity_received=1000.0, quantity_on_hand=920.0, quantity_reserved_hard=80.0,
            receipt_date=today - timedelta(days=10), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-004", purchase_order="PO-2025-0010"
        ),
        
        # Grasa
        InventoryLot(
            lot_number="LOT-012-2024-11", item_id=12,
            quantity_received=50.0, quantity_on_hand=28.0, quantity_allocated=22.0,
            receipt_date=today - timedelta(days=70), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-005", purchase_order="PO-2024-0870"
        ),
        
        # Cinta aislante
        InventoryLot(
            lot_number="LOT-013-2024-12", item_id=13,
            quantity_received=100.0, quantity_on_hand=55.0, quantity_reserved_soft=10.0,
            receipt_date=today - timedelta(days=40), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-002", purchase_order="PO-2024-0920"
        ),
        
        # Guantes
        InventoryLot(
            lot_number="LOT-014-2025-01", item_id=14,
            quantity_received=200.0, quantity_on_hand=185.0, quantity_allocated=15.0,
            receipt_date=today - timedelta(days=8), qc_status=QCStatus.APPROVED,
            supplier_id="SUP-004", purchase_order="PO-2025-0008"
        ),
        
        # Pintura (con vencimiento)
        InventoryLot(
            lot_number="LOT-015-2024-10", item_id=15,
            quantity_received=24.0, quantity_on_hand=8.0, quantity_allocated=16.0,
            receipt_date=today - timedelta(days=120),
            expiration_date=today + timedelta(days=60),
            shelf_life_days=180,
            qc_status=QCStatus.CONDITIONAL,  # Cerca de vencer
            supplier_id="SUP-002", purchase_order="PO-2024-0750"
        ),
        InventoryLot(
            lot_number="LOT-015-2025-01", item_id=15,
            quantity_received=24.0, quantity_on_hand=22.0, quantity_reserved_soft=2.0,
            receipt_date=today - timedelta(days=5),
            expiration_date=today + timedelta(days=175),
            shelf_life_days=180,
            qc_status=QCStatus.APPROVED,
            supplier_id="SUP-002", purchase_order="PO-2025-0003"
        ),
        
        # Items en inspección (no disponibles aún)
        InventoryLot(
            lot_number="LOT-001-2025-02", item_id=1,
            quantity_received=5.0, quantity_on_hand=5.0, quantity_reserved_soft=0.0,
            receipt_date=today - timedelta(days=2), qc_status=QCStatus.INSPECTING,
            supplier_id="SUP-001", purchase_order="PO-2025-0015"
        ),
        InventoryLot(
            lot_number="LOT-006-2025-02", item_id=6,
            quantity_received=50.0, quantity_on_hand=50.0, quantity_reserved_soft=0.0,
            receipt_date=today - timedelta(days=1), qc_status=QCStatus.INSPECTING,
            supplier_id="SUP-005", purchase_order="PO-2025-0016"
        ),
        
        # Lote en cuarentena
        InventoryLot(
            lot_number="LOT-004-QUAR-01", item_id=4,
            quantity_received=20.0, quantity_on_hand=20.0, quantity_reserved_soft=0.0,
            receipt_date=today - timedelta(days=12), qc_status=QCStatus.QUARANTINE,
            qc_notes="Posible defecto en acabado superficial - verificar con ingeniería",
            supplier_id="SUP-003", purchase_order="PO-2025-0012"
        ),
    ]
    
    session.add_all(lots)
    session.commit()
    print(f"✅ Created {len(lots)} inventory lots")
    
    # Crear ubicaciones para los primeros 10 lotes
    locations = [
        LotLocation(lot_id=1, warehouse_code="WH-001", zone="STO", rack="R01", level="A", position="01", quantity=8.0),
        LotLocation(lot_id=2, warehouse_code="WH-001", zone="STO", rack="R01", level="A", position="02", quantity=12.0),
        LotLocation(lot_id=3, warehouse_code="WH-001", zone="STO", rack="R02", level="B", position="01", quantity=3.0),
        LotLocation(lot_id=4, warehouse_code="WH-001", zone="STO", rack="R03", level="A", position="05", quantity=38.0),
        LotLocation(lot_id=5, warehouse_code="WH-002", zone="STO", rack="R01", level="C", position="10", quantity=5.0),
        LotLocation(lot_id=6, warehouse_code="WH-001", zone="STO", rack="R05", level="A", position="01", quantity=320.0),
        LotLocation(lot_id=7, warehouse_code="WH-001", zone="STO", rack="R06", level="B", position="03", quantity=75.0),
        LotLocation(lot_id=8, warehouse_code="WH-002", zone="STO", rack="R02", level="A", position="08", quantity=150.0),
        LotLocation(lot_id=9, warehouse_code="WH-001", zone="STO", rack="R07", level="C", position="02", quantity=30.0),
        LotLocation(lot_id=9, warehouse_code="WH-003", zone="STO", rack="R01", level="A", position="05", quantity=15.0),
    ]
    
    session.add_all(locations)
    session.commit()
    print(f"✅ Created {len(locations)} lot locations")
    
    return lots


def seed_boms(session: Session, items: list):
    """Crea 5 BOMs con componentes"""
    # Motor eléctrico (ITEM-003) es assembly
    motor_bom = [
        BOMComponent(parent_item_id=3, component_id="COMP-301", component_code="ROTOR-15HP", quantity=1.0, unit_of_measure="EA", scrap_factor=1.0),
        BOMComponent(parent_item_id=3, component_id="COMP-302", component_code="STATOR-15HP", quantity=1.0, unit_of_measure="EA", scrap_factor=1.0),
        BOMComponent(parent_item_id=3, component_id="COMP-303", component_code="CASING-15HP", quantity=1.0, unit_of_measure="EA", scrap_factor=1.0),
        BOMComponent(parent_item_id=3, component_id="ITEM-004", component_code="MAT-004", quantity=2.0, unit_of_measure="EA", scrap_factor=1.0, notes="Rodamientos SKF"),
        BOMComponent(parent_item_id=3, component_id="ITEM-009", component_code="MAT-009", quantity=8.0, unit_of_measure="EA", scrap_factor=1.05, notes="Tornillos de sujeción"),
        BOMComponent(parent_item_id=3, component_id="ITEM-010", component_code="MAT-010", quantity=8.0, unit_of_measure="EA", scrap_factor=1.05),
        BOMComponent(parent_item_id=3, component_id="ITEM-011", component_code="MAT-011", quantity=16.0, unit_of_measure="EA", scrap_factor=1.10, notes="Arandelas de presión"),
    ]
    
    session.add_all(motor_bom)
    session.commit()
    print(f"✅ Created BOM for Motor (7 components)")
    
    return motor_bom


def seed_equivalents(session: Session, items: list):
    """Crea 10 ítems equivalentes"""
    equivalents = [
        # Válvula ITEM-001 tiene 2 equivalentes
        EquivalentItem(item_id=1, equivalent_id="ITEM-001-ALT1", equivalent_code="MAT-001-A", conversion_factor=1.0, technical_specs_match=0.95, cost_differential=0.08, supplier_reliability=0.92),
        EquivalentItem(item_id=1, equivalent_id="ITEM-001-ALT2", equivalent_code="MAT-001-B", conversion_factor=1.0, technical_specs_match=0.88, cost_differential=-0.05, lead_time_delta_days=5, supplier_reliability=0.85),
        
        # Sensor ITEM-002 tiene 1 equivalente
        EquivalentItem(item_id=2, equivalent_id="ITEM-002-ALT1", equivalent_code="MAT-002-A", conversion_factor=1.0, technical_specs_match=0.92, cost_differential=0.12, supplier_reliability=0.90),
        
        # Rodamiento ITEM-004 tiene 2 equivalentes
        EquivalentItem(item_id=4, equivalent_id="ITEM-004-FAG", equivalent_code="FAG-6208", conversion_factor=1.0, technical_specs_match=0.98, cost_differential=0.15, supplier_reliability=0.96),
        EquivalentItem(item_id=4, equivalent_id="ITEM-004-NTN", equivalent_code="NTN-6208", conversion_factor=1.0, technical_specs_match=0.95, cost_differential=0.05, supplier_reliability=0.93),
        
        # Cable ITEM-005 tiene 1 equivalente
        EquivalentItem(item_id=5, equivalent_id="ITEM-005-ALT", equivalent_code="CABLE-3X2.5-FLEX", conversion_factor=1.0, technical_specs_match=0.90, cost_differential=-0.10, supplier_reliability=0.88),
        
        # Filtro ITEM-006 tiene 2 equivalentes
        EquivalentItem(item_id=6, equivalent_id="ITEM-006-MANN", equivalent_code="MANN-H932", conversion_factor=1.0, technical_specs_match=0.97, cost_differential=0.20, supplier_reliability=0.95),
        EquivalentItem(item_id=6, equivalent_id="ITEM-006-DONALDSON", equivalent_code="DONALDSON-P550588", conversion_factor=1.0, technical_specs_match=0.94, cost_differential=0.10, supplier_reliability=0.92),
        
        # Aceite ITEM-008 tiene 1 equivalente
        EquivalentItem(item_id=8, equivalent_id="ITEM-008-SHELL", equivalent_code="SHELL-RIMULA-R6", conversion_factor=1.0, technical_specs_match=0.96, cost_differential=0.18, supplier_reliability=0.97),
        
        # Grasa ITEM-012 tiene 1 equivalente
        EquivalentItem(item_id=12, equivalent_id="ITEM-012-MOBIL", equivalent_code="MOBIL-POLYREX-EM", conversion_factor=1.0, technical_specs_match=0.93, cost_differential=0.25, supplier_reliability=0.94),
    ]
    
    session.add_all(equivalents)
    session.commit()
    print(f"✅ Created {len(equivalents)} equivalent items")
    
    return equivalents


def main():
    """Ejecuta el seeding completo"""
    print("\n" + "="*60)
    print("🌱 SEEDING PLANNER DATABASE")
    print("="*60 + "\n")
    
    # Crear tablas
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created\n")
    
    # Crear sesión
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Seed en orden de dependencias
        items = seed_items(session)
        suppliers = seed_suppliers(session, items)
        warehouses = seed_warehouses(session)
        lots = seed_inventory(session, items)
        boms = seed_boms(session, items)
        equivalents = seed_equivalents(session, items)
        
        print("\n" + "="*60)
        print("✅ SEEDING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nSummary:")
        print(f"  • Items: {len(items)}")
        print(f"  • Suppliers: {len(suppliers)}")
        print(f"  • Warehouses: {len(warehouses)}")
        print(f"  • Inventory Lots: {len(lots)}")
        print(f"  • BOM Components: {len(boms)}")
        print(f"  • Equivalent Items: {len(equivalents)}")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
