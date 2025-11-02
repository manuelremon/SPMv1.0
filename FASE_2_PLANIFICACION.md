# FASE 2: Planificación de Validaciones Adicionales

## 📋 Objetivos de Fase 2

Después del éxito de Fase 1 (reducción ~75% de errores), Fase 2 se enfoca en:

1. **Validaciones de Presupuesto** - Límites por usuario y centro
2. **Auditoría y Historial** - Tracking de cambios
3. **Optimizaciones** - Performance y caching
4. **Automatización** - Flujos sin aprobación para casos simples

---

## 🔍 Análisis de Próximos Problemas

### Problema #5: Sin Límites de Presupuesto Global
**Síntoma:** Un usuario podría crear 100 solicitudes de USD 100,000 sin límite
**Impacto:** Sobregastos no controlados
**Solución propuesta:** `_validar_presupuesto_usuario()`

### Problema #6: Sin Historial de Cambios
**Síntoma:** No hay registro de quién modificó qué y cuándo
**Impacto:** Imposible auditar cambios
**Solución propuesta:** Agregar tabla `audit_log` y logging

### Problema #7: Sin Validación de Centros
**Síntoma:** Usuario podría solicitar para centro no autorizado
**Impacto:** Falta de control de acceso por ubicación
**Solución propuesta:** `_validar_centro_usuario()`

### Problema #8: Performance no Optimizada
**Síntoma:** Queries sin índices, sin caching
**Impacto:** Lentitud en BD con muchos datos
**Solución propuesta:** Agregar índices y cache de config

---

## 🗺️ Roadmap de Fase 2

### Iteración 2.1: Validaciones de Presupuesto (Semana 1)
```
├─ Crear tabla presupuesto_usuarios
├─ Implementar _validar_presupuesto_usuario()
├─ Integrar en _pre_validar_aprobacion()
├─ Agregar 8 tests unitarios
└─ Documentar cambios
```

### Iteración 2.2: Auditoría y Historial (Semana 2)
```
├─ Crear tabla audit_log
├─ Implementar _registrar_auditoria()
├─ Integrar en todas las operaciones
├─ Agregar 6 tests unitarios
└─ Crear queries de reporte
```

### Iteración 2.3: Validación de Centros (Semana 2-3)
```
├─ Analizar relación usuarios-centros
├─ Implementar _validar_centro_usuario()
├─ Integrar en validaciones
├─ Agregar 4 tests unitarios
└─ Actualizar documentación
```

### Iteración 2.4: Optimizaciones (Semana 3)
```
├─ Identificar queries lentas
├─ Agregar índices en BD
├─ Implementar caching de config
├─ Benchmarking antes/después
└─ Documentar mejoras
```

---

## 📊 Estimaciones

| Tarea | Complejidad | Horas | Tests | Impacto |
|-------|------------|-------|-------|---------|
| Presupuesto | Media | 6-8 | 8 | Alto |
| Auditoría | Alta | 8-10 | 6 | Crítico |
| Centros | Media | 4-6 | 4 | Medio |
| Optimización | Media | 4-6 | 2 | Alto |
| **Total Fase 2** | **--** | **22-30** | **20** | **--** |

---

## 🎯 Métricas de Éxito

**Fase 2 será exitosa cuando:**

- ✅ Todos los tests de Fase 1 siguen pasando (22/22)
- ✅ Nuevos tests de Fase 2 pasan (20/20)
- ✅ Cobertura de código > 95%
- ✅ Performance < 5ms por operación
- ✅ Auditoría completa de cambios
- ✅ Documentación actualizada

---

## 🔧 Cambios Técnicos Previstos

### Base de Datos

```sql
-- Nueva tabla de presupuestos
CREATE TABLE presupuesto_usuarios (
    id INTEGER PRIMARY KEY,
    usuario_id TEXT,
    mes_año DATE,
    presupuesto_asignado REAL,
    presupuesto_utilizado REAL,
    presupuesto_disponible REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Nueva tabla de auditoría
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    entidad_tipo TEXT,
    entidad_id INTEGER,
    accion TEXT,
    usuario_id TEXT,
    datos_anterior JSON,
    datos_nuevo JSON,
    timestamp TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);
```

### Funciones Nuevas

```python
# Presupuesto
def _validar_presupuesto_usuario(con, usuario_id, monto)
def _obtener_presupuesto_disponible(con, usuario_id)
def _actualizar_presupuesto_usado(con, usuario_id, monto)

# Auditoría
def _registrar_auditoria(con, entidad_tipo, entidad_id, accion, usuario, datos_anterior, datos_nuevo)
def _obtener_auditoria_entidad(con, entidad_tipo, entidad_id)

# Centros
def _validar_centro_usuario(con, usuario_id, centro_id)
def _obtener_centros_autorizados(con, usuario_id)

# Optimización
def _get_cached_approver_config(monto)
def _update_cache()
```

---

## 📝 Documentación Requerida

Para Fase 2, se necesitará:

1. **API Documentation** - Nuevos endpoints y cambios
2. **Database Schema** - Tablas nuevas y cambios
3. **Audit Trail Guide** - Cómo acceder a historial
4. **Performance Report** - Before/after benchmarks
5. **Migration Guide** - Cómo migrar datos existentes
6. **Training Materials** - Para usuarios finales

---

## ⚠️ Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| Cambios rompen Fase 1 | Media | Alto | Tests de regresión |
| Performance degrada | Baja | Medio | Benchmarking antes/después |
| Datos audit inconsistentes | Baja | Alto | Validación de integridad |
| Overflow de tabla audit | Baja | Medio | Rotación de logs |

---

## 🚀 Próximos Pasos Inmediatos

**Esta semana:**
1. ✅ Code review de Fase 1
2. ✅ Merge de cambios a main
3. ⏳ Iniciar Fase 2.1 (Presupuestos)
4. ⏳ Crear rama feature/presupuestos

**Próxima semana:**
1. ⏳ Tests de presupuesto (8)
2. ⏳ Implementar validaciones
3. ⏳ Integración con Fase 1
4. ⏳ Validación manual

---

## 📚 Referencias

- [FASE_1_VALIDACIONES_COMPLETADO.md](FASE_1_VALIDACIONES_COMPLETADO.md)
- [RESUMEN_FASE_1_FINAL.md](RESUMEN_FASE_1_FINAL.md)
- `src/backend/routes/solicitudes.py` (funciones base)
- `tests/test_solicitud_validations.py` (patrón de tests)

---

## 👥 Dependencias

**Para ejecutar Fase 2, necesitamos:**
- ✅ Código de Fase 1 mergeado
- ✅ Code review completado
- ✅ Equipo disponible (6-8 horas/día)
- ⏳ Datos de presupuesto (si existen)
- ⏳ Clarificación de centros autorizados

---

**Estado:** Planificación Completa  
**Fecha:** 2 de noviembre de 2025  
**Próximo milestone:** Inicio de Fase 2.1
