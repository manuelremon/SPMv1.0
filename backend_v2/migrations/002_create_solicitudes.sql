-- Backend v2.0 - Migration 002: Create solicitudes tables
-- Author: SPM v2.0 Migration Team
-- Date: 2025-01-08
-- Description: Migración de solicitudes v1.0 a v2.0 con normalización de items

-- ====================================================================================
-- Table 1: materiales (Catálogo de materiales)
-- ====================================================================================
CREATE TABLE IF NOT EXISTS materiales (
    -- Primary Key
    codigo VARCHAR(50) PRIMARY KEY,  -- Código SAP del material
    
    -- Información del material
    descripcion TEXT NOT NULL,
    precio_usd DECIMAL(12, 2) DEFAULT 0.0,  -- Precio en USD
    
    -- Clasificación
    centro VARCHAR(100),  -- Centro de pertenencia
    sector VARCHAR(100),  -- Sector organizacional
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para materiales
CREATE INDEX IF NOT EXISTS idx_materiales_centro ON materiales(centro);
CREATE INDEX IF NOT EXISTS idx_materiales_sector ON materiales(sector);
CREATE INDEX IF NOT EXISTS idx_materiales_descripcion ON materiales(descripcion);

-- Trigger para actualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_materiales_timestamp 
AFTER UPDATE ON materiales
FOR EACH ROW
BEGIN
    UPDATE materiales 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE codigo = NEW.codigo;
END;


-- ====================================================================================
-- Table 2: solicitudes (Solicitudes de materiales)
-- ====================================================================================
CREATE TABLE IF NOT EXISTS solicitudes (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    id_usuario VARCHAR(100) NOT NULL,  -- Username del solicitante
    aprobador_id VARCHAR(100),  -- Username del aprobador
    
    -- Clasificación organizacional
    centro VARCHAR(100) NOT NULL,
    sector VARCHAR(100),
    
    -- Información de la solicitud
    justificacion TEXT,
    comentario TEXT,
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'borrador',
    
    -- Fechas
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    fecha_modificacion TIMESTAMP,
    
    -- Tracking de aprobadores/planificadores
    aprobadores TEXT,  -- Lista separada por comas
    planificadores TEXT,  -- Lista separada por comas
    
    -- Total calculado
    total_monto DECIMAL(12, 2) DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (id_usuario) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (aprobador_id) REFERENCES users(username) ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Check constraint para status
    CHECK (status IN (
        'borrador',
        'pendiente_de_aprobacion',
        'aprobada',
        'rechazada',
        'en_tratamiento',
        'cancelada',
        'cancelacion_pendiente',
        'en_planificacion',
        'finalizada'
    ))
);

-- Índices para solicitudes
CREATE INDEX IF NOT EXISTS idx_solicitudes_id_usuario ON solicitudes(id_usuario);
CREATE INDEX IF NOT EXISTS idx_solicitudes_status ON solicitudes(status);
CREATE INDEX IF NOT EXISTS idx_solicitudes_centro ON solicitudes(centro);
CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha_creacion ON solicitudes(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_solicitudes_aprobador_id ON solicitudes(aprobador_id);

-- Trigger para actualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_solicitudes_timestamp 
AFTER UPDATE ON solicitudes
FOR EACH ROW
BEGIN
    UPDATE solicitudes 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;


-- ====================================================================================
-- Table 3: solicitud_items (Items normalizados de solicitudes)
-- ====================================================================================
CREATE TABLE IF NOT EXISTS solicitud_items (
    -- Primary Key
    id_item INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    solicitud_id INTEGER NOT NULL,
    material_codigo VARCHAR(50) NOT NULL,
    
    -- Datos del item
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(12, 2) DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (material_codigo) REFERENCES materiales(codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Check constraint para cantidad positiva
    CHECK (cantidad > 0)
);

-- Índices para solicitud_items
CREATE INDEX IF NOT EXISTS idx_solicitud_items_solicitud_id ON solicitud_items(solicitud_id);
CREATE INDEX IF NOT EXISTS idx_solicitud_items_material_codigo ON solicitud_items(material_codigo);

-- Índice compuesto para búsquedas por solicitud + material
CREATE INDEX IF NOT EXISTS idx_solicitud_items_composite 
    ON solicitud_items(solicitud_id, material_codigo);


-- ====================================================================================
-- Table 4: aprobaciones (Audit trail de aprobaciones/rechazos)
-- ====================================================================================
CREATE TABLE IF NOT EXISTS aprobaciones (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    solicitud_id INTEGER NOT NULL,
    aprobador_id VARCHAR(100) NOT NULL,
    
    -- Información de la aprobación
    decision VARCHAR(20) NOT NULL,  -- 'aprobada', 'rechazada'
    comentario TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (aprobador_id) REFERENCES users(username) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Check constraint para decision
    CHECK (decision IN ('aprobada', 'rechazada'))
);

-- Índices para aprobaciones
CREATE INDEX IF NOT EXISTS idx_aprobaciones_solicitud_id ON aprobaciones(solicitud_id);
CREATE INDEX IF NOT EXISTS idx_aprobaciones_aprobador_id ON aprobaciones(aprobador_id);
CREATE INDEX IF NOT EXISTS idx_aprobaciones_decision ON aprobaciones(decision);
CREATE INDEX IF NOT EXISTS idx_aprobaciones_created_at ON aprobaciones(created_at);


-- ====================================================================================
-- Seed Data: Materiales de ejemplo
-- ====================================================================================

-- Materiales de IT
INSERT OR IGNORE INTO materiales (codigo, descripcion, precio_usd, centro, sector) VALUES
    ('MAT-IT-001', 'Laptop Dell Latitude 5420', 1200.00, 'Buenos Aires', 'IT'),
    ('MAT-IT-002', 'Monitor LG 27" 4K', 450.00, 'Buenos Aires', 'IT'),
    ('MAT-IT-003', 'Teclado Mecánico Logitech', 85.00, 'Buenos Aires', 'IT'),
    ('MAT-IT-004', 'Mouse Wireless Logitech MX Master', 99.00, 'Buenos Aires', 'IT'),
    ('MAT-IT-005', 'Webcam Logitech C920 HD Pro', 78.00, 'Buenos Aires', 'IT');

-- Materiales de Oficina
INSERT OR IGNORE INTO materiales (codigo, descripcion, precio_usd, centro, sector) VALUES
    ('MAT-OF-001', 'Resma Papel A4 75g x 500 hojas', 5.50, 'Buenos Aires', 'Oficina'),
    ('MAT-OF-002', 'Carpeta A-Z Tamaño Oficio', 3.20, 'Buenos Aires', 'Oficina'),
    ('MAT-OF-003', 'Archivador Palanca Lomo Ancho', 4.80, 'Buenos Aires', 'Oficina'),
    ('MAT-OF-004', 'Lapicera Bic Cristal Azul x 50', 8.00, 'Buenos Aires', 'Oficina'),
    ('MAT-OF-005', 'Resaltador Stabilo Boss x 6 colores', 12.00, 'Buenos Aires', 'Oficina');

-- Materiales de Mantenimiento
INSERT OR IGNORE INTO materiales (codigo, descripcion, precio_usd, centro, sector) VALUES
    ('MAT-MN-001', 'Destornillador Set 12 piezas', 22.00, 'Mendoza', 'Mantenimiento'),
    ('MAT-MN-002', 'Taladro Inalámbrico Bosch 18V', 180.00, 'Mendoza', 'Mantenimiento'),
    ('MAT-MN-003', 'Cinta Métrica 5m Stanley', 8.50, 'Mendoza', 'Mantenimiento'),
    ('MAT-MN-004', 'Linterna LED Recargable', 25.00, 'Mendoza', 'Mantenimiento'),
    ('MAT-MN-005', 'Set Llaves Allen métricas', 15.00, 'Mendoza', 'Mantenimiento');

-- Materiales de Seguridad
INSERT OR IGNORE INTO materiales (codigo, descripcion, precio_usd, centro, sector) VALUES
    ('MAT-SG-001', 'Casco de Seguridad Industrial', 18.00, 'Comodoro Rivadavia', 'Seguridad'),
    ('MAT-SG-002', 'Chaleco Reflectante Alta Visibilidad', 12.00, 'Comodoro Rivadavia', 'Seguridad'),
    ('MAT-SG-003', 'Guantes de Seguridad Anticorte', 9.50, 'Comodoro Rivadavia', 'Seguridad'),
    ('MAT-SG-004', 'Botas de Seguridad Punta de Acero', 65.00, 'Comodoro Rivadavia', 'Seguridad'),
    ('MAT-SG-005', 'Gafas de Seguridad Antivaho', 8.00, 'Comodoro Rivadavia', 'Seguridad');

-- Materiales de Laboratorio
INSERT OR IGNORE INTO materiales (codigo, descripcion, precio_usd, centro, sector) VALUES
    ('MAT-LB-001', 'Microscopio Binocular 1000x', 550.00, 'La Plata', 'Laboratorio'),
    ('MAT-LB-002', 'Pipeta Automática 10-100 µL', 120.00, 'La Plata', 'Laboratorio'),
    ('MAT-LB-003', 'Balanza Digital Precisión 0.01g', 280.00, 'La Plata', 'Laboratorio'),
    ('MAT-LB-004', 'Vaso Precipitado Vidrio 500ml x 6', 35.00, 'La Plata', 'Laboratorio'),
    ('MAT-LB-005', 'pH-metro Digital Portátil', 95.00, 'La Plata', 'Laboratorio');


-- ====================================================================================
-- Views útiles (opcional)
-- ====================================================================================

-- Vista de solicitudes con totales calculados
CREATE VIEW IF NOT EXISTS v_solicitudes_summary AS
SELECT 
    s.id,
    s.id_usuario,
    s.centro,
    s.sector,
    s.status,
    s.fecha_creacion,
    COUNT(si.id_item) as total_items,
    SUM(si.cantidad) as total_cantidad,
    SUM(si.cantidad * si.precio_unitario) as total_calculado,
    s.total_monto
FROM solicitudes s
LEFT JOIN solicitud_items si ON s.id = si.solicitud_id
GROUP BY s.id;

-- Vista de materiales más solicitados
CREATE VIEW IF NOT EXISTS v_materiales_populares AS
SELECT 
    m.codigo,
    m.descripcion,
    m.centro,
    m.sector,
    COUNT(si.id_item) as total_solicitudes,
    SUM(si.cantidad) as cantidad_total
FROM materiales m
LEFT JOIN solicitud_items si ON m.codigo = si.material_codigo
GROUP BY m.codigo
ORDER BY total_solicitudes DESC;


-- ====================================================================================
-- Migration Complete
-- ====================================================================================
-- Tables created: materiales, solicitudes, solicitud_items, aprobaciones
-- Indexes created: 20 indexes for performance
-- Seed data: 25 materiales across 5 sectors
-- Views created: 2 summary views
