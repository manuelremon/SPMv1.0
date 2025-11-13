-- Backend v2.0 - Migration 001: Create users table
-- Author: SPM v2.0 Migration Team
-- Date: 2025-11-13
-- Description: Migración de tabla usuarios v1.0 a users v2.0 con nuevos campos

-- Crear tabla users
CREATE TABLE IF NOT EXISTS users (
    -- Primary Key (nuevo en v2)
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Campos de identidad
    username VARCHAR(100) NOT NULL UNIQUE,  -- era id_spm en v1.0
    email VARCHAR(255) UNIQUE,              -- era mail en v1.0
    password_hash VARCHAR(255) NOT NULL,    -- era contrasena en v1.0
    
    -- Información personal
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    
    -- Organización
    role VARCHAR(50) NOT NULL DEFAULT 'Solicitante',  -- era rol en v1.0
    sector VARCHAR(100),
    posicion VARCHAR(100),
    centros TEXT,  -- Lista separada por comas/punto y coma
    
    -- Legacy YPF
    id_ypf VARCHAR(100),  -- ID de Red YPF (legacy)
    
    -- Jerarquía organizacional
    jefe VARCHAR(100),
    gerente1 VARCHAR(100),
    gerente2 VARCHAR(100),
    
    -- Estado
    is_active BOOLEAN NOT NULL DEFAULT 1,  -- nuevo en v2
    estado_registro VARCHAR(50) DEFAULT 'Pendiente',
    
    -- Timestamps (nuevos en v2)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_estado_registro ON users(estado_registro);

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Seed de usuario admin
-- Password: admin123 (hash bcrypt)
INSERT OR IGNORE INTO users (
    username,
    email,
    password_hash,
    nombre,
    apellido,
    role,
    is_active,
    estado_registro,
    sector,
    posicion
) VALUES (
    'admin',
    'admin@spm.com',
    '$2b$12$19rk6IUBQkijnlGPqbrRMuxRbxMOU.3FH6P8kceiba3JOW4y/1i.C',
    'Administrador',
    'Sistema',
    'Administrador',
    1,
    'Activo',
    'IT',
    'System Administrator'
);

-- Seed de usuario planificador
-- Password: plan123
INSERT OR IGNORE INTO users (
    username,
    email,
    password_hash,
    nombre,
    apellido,
    role,
    is_active,
    estado_registro,
    sector,
    posicion
) VALUES (
    'planificador',
    'planificador@spm.com',
    '$2b$12$EAL6j2mDIokuJP6GFsHlP.madjcpcsScbWJsFcKS5CIzWKJoqt91W',
    'Plan',
    'SPM',
    'Planificador',
    1,
    'Activo',
    'Planificación',
    'Planner'
);

-- Seed de usuario solicitante
-- Password: user123
INSERT OR IGNORE INTO users (
    username,
    email,
    password_hash,
    nombre,
    apellido,
    role,
    is_active,
    estado_registro,
    sector,
    posicion
) VALUES (
    'usuario',
    'usuario@spm.com',
    '$2b$12$TRNVmCo/yBh3REXhJsiVhuYaDh4SfLrXQrfWTU.1vAPPz3pxvagfa',
    'Usuario',
    'Prueba',
    'Solicitante',
    1,
    'Activo',
    'Operaciones',
    'Operator'
);
