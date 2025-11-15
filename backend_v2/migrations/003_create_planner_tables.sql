-- Migration: 003_create_planner_tables.sql
-- Description: Create planner domain tables (items, inventory, suppliers, warehouses)
-- Date: 2025-11-13

-- =====================================================
-- 1. ITEM MASTER TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_item_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id VARCHAR(50) UNIQUE NOT NULL,
    sap_code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    long_description TEXT,
    
    -- Clasificación
    abc_class VARCHAR(10) DEFAULT 'C' CHECK (abc_class IN ('A', 'B', 'C')),
    criticality VARCHAR(20) DEFAULT 'LOW' CHECK (criticality IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    procurement_type VARCHAR(20) DEFAULT 'PURCHASE' CHECK (procurement_type IN ('PURCHASE', 'MAKE', 'TRANSFER', 'IMPORT', 'VMI')),
    
    -- Unidades
    base_unit VARCHAR(10) NOT NULL,
    alternative_units TEXT,  -- JSON: {"BOX": 10, "PALLET": 500}
    
    -- Especificaciones técnicas (JSON)
    specifications TEXT,  -- JSON: {"voltage": "220V", "rpm": 1500}
    
    -- Cumplimiento normativo
    requires_traceability INTEGER DEFAULT 0,
    compliance_standards TEXT,  -- JSON: ["ISO9001", "FDA"]
    shelf_life_days INTEGER,
    requires_cold_chain INTEGER DEFAULT 0,
    
    -- Estructura
    is_assembly INTEGER DEFAULT 0,
    
    -- Costos
    standard_cost_usd REAL DEFAULT 0.0,
    list_price_usd REAL DEFAULT 0.0,
    annual_consumption_units REAL DEFAULT 0.0,
    
    -- Parámetros de control
    minimum_order_quantity REAL DEFAULT 1.0,
    order_multiple REAL DEFAULT 1.0,
    safety_stock_days INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_item_master_item_id ON planner_item_master(item_id);
CREATE INDEX idx_item_master_sap_code ON planner_item_master(sap_code);
CREATE INDEX idx_item_master_abc ON planner_item_master(abc_class);
CREATE INDEX idx_item_master_criticality ON planner_item_master(criticality);

-- =====================================================
-- 2. BOM (BILL OF MATERIALS) TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_bom_component (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_item_id INTEGER NOT NULL,
    component_id VARCHAR(50) NOT NULL,
    component_code VARCHAR(50) NOT NULL,
    quantity REAL NOT NULL,
    unit_of_measure VARCHAR(10) NOT NULL,
    scrap_factor REAL DEFAULT 1.0,
    is_phantom INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_item_id) REFERENCES planner_item_master(id) ON DELETE CASCADE,
    UNIQUE (parent_item_id, component_id)
);

CREATE INDEX idx_bom_parent ON planner_bom_component(parent_item_id);
CREATE INDEX idx_bom_component ON planner_bom_component(component_id);

-- =====================================================
-- 3. EQUIVALENT ITEMS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_equivalent_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    equivalent_id VARCHAR(50) NOT NULL,
    equivalent_code VARCHAR(50) NOT NULL,
    
    -- Conversión técnica
    conversion_factor REAL DEFAULT 1.0,
    technical_specs_match REAL DEFAULT 0.9,
    
    -- Diferencias operativas
    cost_differential REAL DEFAULT 0.0,
    lead_time_delta_days INTEGER DEFAULT 0,
    supplier_reliability REAL DEFAULT 0.95,
    
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (item_id) REFERENCES planner_item_master(id) ON DELETE CASCADE
);

CREATE INDEX idx_equiv_item ON planner_equivalent_item(item_id);
CREATE INDEX idx_equiv_id ON planner_equivalent_item(equivalent_id);

-- =====================================================
-- 4. INVENTORY LOT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_inventory_lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_number VARCHAR(50) UNIQUE NOT NULL,
    serial_number VARCHAR(50),
    item_id INTEGER NOT NULL,
    
    -- Cantidades
    quantity_received REAL NOT NULL,
    quantity_on_hand REAL NOT NULL,
    quantity_reserved_hard REAL DEFAULT 0.0,
    quantity_reserved_soft REAL DEFAULT 0.0,
    quantity_allocated REAL DEFAULT 0.0,
    
    -- Fechas
    receipt_date DATETIME NOT NULL,
    expiration_date DATETIME,
    shelf_life_days INTEGER,
    
    -- Control de Calidad
    qc_status VARCHAR(20) DEFAULT 'INSPECTING' CHECK (qc_status IN ('INSPECTING', 'APPROVED', 'CONDITIONAL', 'REJECTED', 'QUARANTINE')),
    qc_approver VARCHAR(100),
    qc_date DATETIME,
    qc_notes TEXT,
    
    -- Trazabilidad
    supplier_id VARCHAR(50),
    purchase_order VARCHAR(50),
    invoice_number VARCHAR(50),
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (item_id) REFERENCES planner_item_master(id) ON DELETE RESTRICT,
    CHECK (quantity_on_hand >= 0),
    CHECK (quantity_reserved_hard >= 0),
    CHECK (quantity_reserved_soft >= 0),
    CHECK (quantity_allocated >= 0)
);

CREATE INDEX idx_lot_item ON planner_inventory_lot(item_id);
CREATE INDEX idx_lot_number ON planner_inventory_lot(lot_number);
CREATE INDEX idx_lot_status ON planner_inventory_lot(qc_status);
CREATE INDEX idx_lot_supplier ON planner_inventory_lot(supplier_id);
CREATE INDEX idx_lot_expiration ON planner_inventory_lot(expiration_date);

-- =====================================================
-- 5. LOT LOCATION TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_lot_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    
    -- Ubicación jerárquica
    warehouse_code VARCHAR(20) NOT NULL,
    zone VARCHAR(20),
    rack VARCHAR(20),
    level VARCHAR(10),
    position VARCHAR(10),
    
    quantity REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lot_id) REFERENCES planner_inventory_lot(id) ON DELETE CASCADE
);

CREATE INDEX idx_location_lot ON planner_lot_location(lot_id);
CREATE INDEX idx_location_warehouse ON planner_lot_location(warehouse_code);

-- =====================================================
-- 6. SUPPLIER TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id VARCHAR(50) UNIQUE NOT NULL,
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Contacto
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    
    -- Rating
    rating VARCHAR(20) DEFAULT 'APPROVED' CHECK (rating IN ('PREFERRED', 'APPROVED', 'CONDITIONAL', 'PROBATION', 'BLOCKED')),
    reliability_score REAL DEFAULT 0.9,
    quality_score REAL DEFAULT 0.9,
    on_time_delivery_rate REAL DEFAULT 0.95,
    
    -- Plazos y condiciones
    average_lead_time_days INTEGER DEFAULT 15,
    minimum_order_value_usd REAL DEFAULT 0.0,
    payment_terms_days INTEGER DEFAULT 30,
    
    -- Capacidades (JSON)
    categories_supplied TEXT,  -- JSON: ["RAW_MATERIALS", "COMPONENTS"]
    certifications TEXT,  -- JSON: ["ISO9001", "ISO14001"]
    geographical_coverage TEXT,  -- JSON: ["ARGENTINA", "BRAZIL"]
    
    -- Estado
    is_active INTEGER DEFAULT 1,
    blocked_reason TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_supplier_id ON planner_supplier(supplier_id);
CREATE INDEX idx_supplier_code ON planner_supplier(supplier_code);
CREATE INDEX idx_supplier_rating ON planner_supplier(rating);
CREATE INDEX idx_supplier_active ON planner_supplier(is_active);

-- =====================================================
-- 7. SUPPLIER PRICE AGREEMENT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_supplier_price_agreement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    item_id VARCHAR(50) NOT NULL,
    
    -- Pricing
    unit_price_usd REAL NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    moq REAL DEFAULT 1.0,
    order_multiple REAL DEFAULT 1.0,
    
    -- Lead time específico
    lead_time_days INTEGER,
    
    -- Vigencia
    valid_from DATETIME NOT NULL,
    valid_to DATETIME,
    
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supplier_id) REFERENCES planner_supplier(id) ON DELETE CASCADE
);

CREATE INDEX idx_price_agreement_supplier ON planner_supplier_price_agreement(supplier_id);
CREATE INDEX idx_price_agreement_item ON planner_supplier_price_agreement(item_id);
CREATE INDEX idx_price_agreement_validity ON planner_supplier_price_agreement(valid_from, valid_to);

-- =====================================================
-- 8. WAREHOUSE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS planner_warehouse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_id VARCHAR(50) UNIQUE NOT NULL,
    warehouse_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    warehouse_type VARCHAR(20) DEFAULT 'REGIONAL' CHECK (warehouse_type IN ('CENTRAL', 'REGIONAL', 'FIELD', 'CONSIGNMENT', 'VMI')),
    
    -- Ubicación geográfica
    location VARCHAR(255),
    latitude REAL,
    longitude REAL,
    timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires',
    
    -- Capacidades
    total_capacity_cubic_meters REAL,
    total_capacity_pallets INTEGER,
    utilization_rate REAL DEFAULT 0.0,
    
    -- Costos operativos (por hora)
    picking_cost_per_hour REAL DEFAULT 25.0,
    packing_cost_per_hour REAL DEFAULT 20.0,
    shipping_cost_per_hour REAL DEFAULT 35.0,
    coordination_cost_per_hour REAL DEFAULT 40.0,
    
    -- Parámetros operativos
    operates_24_7 INTEGER DEFAULT 0,
    working_hours_per_day INTEGER DEFAULT 8,
    average_picking_time_hours REAL DEFAULT 0.5,
    average_packing_time_hours REAL DEFAULT 0.25,
    
    -- Conectividad (JSON)
    connections TEXT,  -- JSON: {"WH-02": {"distance_km": 350, "transit_days": 2}}
    
    -- Confiabilidad
    reliability_score REAL DEFAULT 0.95,
    on_time_shipping_rate REAL DEFAULT 0.9,
    
    -- Estado
    is_active INTEGER DEFAULT 1,
    manager_name VARCHAR(255),
    manager_email VARCHAR(255),
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_warehouse_id ON planner_warehouse(warehouse_id);
CREATE INDEX idx_warehouse_code ON planner_warehouse(warehouse_code);
CREATE INDEX idx_warehouse_type ON planner_warehouse(warehouse_type);
CREATE INDEX idx_warehouse_active ON planner_warehouse(is_active);
CREATE INDEX idx_warehouse_location ON planner_warehouse(location);
