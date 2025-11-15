"""
Modelos de dominio para el módulo Planner.

Adaptados de src/planner/models/ a SQLAlchemy con soporte para:
- Maestro de ítems (ItemMaster)
- Estructura de producto (BOM)
- Inventarios con trazabilidad
- Ítems equivalentes y sustitutos
"""

from .items import (
    ABCClassification,
    ItemCriticality,
    ProcurementType,
    ItemMaster,
    BOMComponent,
    EquivalentItem
)

from .inventory import (
    QCStatus,
    InventoryLot,
    LotLocation
)

from .suppliers import (
    SupplierRating,
    Supplier,
    SupplierPriceAgreement
)

from .warehouses import (
    WarehouseType,
    Warehouse
)

__all__ = [
    # Enums
    "ABCClassification",
    "ItemCriticality",
    "ProcurementType",
    "QCStatus",
    "SupplierRating",
    "WarehouseType",
    
    # Items
    "ItemMaster",
    "BOMComponent",
    "EquivalentItem",
    
    # Inventory
    "InventoryLot",
    "LotLocation",
    
    # Suppliers
    "Supplier",
    "SupplierPriceAgreement",
    
    # Warehouses
    "Warehouse",
]
