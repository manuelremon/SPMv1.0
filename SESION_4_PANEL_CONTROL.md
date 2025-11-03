# 🎯 SESIÓN 4 - PANEL DE CONTROL

## ⚡ ESTADO ACTUAL

```
🖥️  BACKEND:        ❌ INACTIVO (debe iniciarse)
📊 DATABASE:       ✅ ACTIVO (44,461 materiales)
🎨 UI STEP 2:      ⚠️  FUNCIONAL pero FEO (requiere rediseño)
🔎 BÚSQUEDA:       ✅ FUNCIONAL (SAP + Descripción)
📋 MODAL:          ❌ NO EXISTE (debe crear)
📈 PROGRESO:       65% → 85% (meta de esta sesión)
```

---

## 🚀 PASO 1: INICIAR SERVIDOR

**Comando único:**
```powershell
cd D:\GitHub\SPMv1.0 ; python -c "from src.backend.app import app; app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)"
```

**Espera este mensaje:**
```
Running on http://127.0.0.1:5000
```

**Verifica en navegador:**
```
http://127.0.0.1:5000/home.html
```

---

## 📋 TAREAS DE HOY

### ✅ TAREA 1: Rediseñar UI de Step 2 (1.5 - 2 horas)
- **Ubicación:** `home.html` líneas 1424-1530
- **Requisito:** Diseño limpio, profesional, sin gradientes feos
- **Resultado esperado:** Usuario dice "Se ve bien"

### ✅ TAREA 2: Implementar Modal (45 min - 1 hora)
- **Ubicación:** `home.html` función `showMaterialDescription()` línea ~4420
- **Requisito:** Popup muestra descripción ampliada + botón "Agregar"
- **Resultado esperado:** Click en "Ver Descripción" abre modal bonito

### ✅ TAREA 3: Testing completo (30 min)
- Búsqueda por SAP
- Búsqueda por descripción
- Filtrado en tiempo real
- Modal abriendo y cerrando
- Agregar material a tabla
- Sin errores en consola

### ✅ TAREA 4: Documentación (15 min)
- Crear `SESION_4_COMPLETADA.md`
- Resumen de cambios
- Capturas de pantalla
- Estado final

---

## 🎨 GUÍA DE DISEÑO RECOMENDADA

### Colores
```css
Primario (botones principal):    #2563eb (azul profesional)
Primario hover:                  #1d4ed8 (azul oscuro)
Secundario (cancelar):           #6b7280 (gris)
Éxito (agregar):                 #10b981 (verde)
Fondo:                           #ffffff (blanco)
Fondo secciones:                 #f9fafb (gris muy claro)
Texto principal:                 #1f2937 (gris oscuro)
Texto secundario:                #6b7280 (gris medio)
Borde:                           #e5e7eb (gris claro)
```

### Layout (3 secciones)
```
┌────────────────────────────────────────────┐
│ 🔎 BUSCAR MATERIAL                         │
├────────────────────────────────────────────┤
│ [SAP input........] [Descripción input..]  │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ ✅ SELECCIONAR Y AGREGAR                   │
├────────────────────────────────────────────┤
│ Material: [dropdown..................]     │
│ Cantidad: [input]  Precio: [input]        │
│ [Ver Descripción] [Agregar Material]      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ 📋 MATERIALES AGREGADOS                    │
├────────────────────────────────────────────┤
│ Tabla con materiales                       │
│ [borrar] [editar]                          │
└────────────────────────────────────────────┘
```

---

## 🔄 FLUJO ESPERADO (después de cambios)

```
1. Usuario ingresa en Step 2
   ↓
2. Ve UI limpia con tres secciones
   ↓
3. Escribe "TORNILLO" en descripción
   ↓
4. Se filtran automáticamente 50 resultados
   ↓
5. Selecciona uno del dropdown
   ↓
6. Click en "Ver Descripción" 
   ↓
7. Se abre MODAL bonito mostrando:
   - Código SAP
   - Descripción corta
   - ✨ DESCRIPCIÓN AMPLIADA ✨ (new!)
   - Precio
   - Unidad
   ↓
8. Opcionalmente clickea "Agregar desde aquí"
   ↓
9. Modal cierra, material agregado a tabla
   ↓
10. Continúa añadiendo más materiales
```

---

## 📊 DATOS DISPONIBLES

**Materiales en `window.allMateriales`:**
```javascript
{
  codigo: "1000000006",
  descripcion: "TORNILLO ACERO 3/8",
  descripcion_larga: "Tornillo de acero inoxidable de 3/8 pulgada, "
                     + "rosca completa, acabado pulido. Uso general "
                     + "en mantenimiento industrial. Especificación "
                     + "ASTM A307 Grado B.",
  centro: null,
  sector: null,
  unidad: "UNI",
  precio_usd: 15.50
}
```

**Total:** 44,461 materiales disponibles

---

## 📁 ARCHIVOS A MODIFICAR

| # | Archivo | Líneas | Qué | Tiempo |
|---|---------|--------|-----|--------|
| 1 | home.html | 1424-1530 | Rediseño HTML Step 2 | 1.5h |
| 2 | home.html | ~4420 | Crear modal función | 45m |
| 3 | home.html | 4350-4391 | Revisar filterMaterials() | 15m |
| 4 | home.html | 4500-4586 | Revisar addMaterialToList() | 15m |

**Total:** ~3 horas

---

## ✨ MEJORAS ESPERADAS (Sesión 4)

```
ANTES (Sesión 3):
- ✅ Búsqueda funciona
- ❌ UI se ve fea
- ❌ Sin modal
- ❌ Experiencia confusa

DESPUÉS (Sesión 4):
- ✅ Búsqueda funciona
- ✅ UI limpia y profesional ← NUEVO
- ✅ Modal bonito con descripción ampliada ← NUEVO
- ✅ Experiencia intuitiva ← MEJORADO
```

---

## 🧪 CHECKLIST DE TESTING

### Search & Filter
- [ ] Escribir "TORNILLO" filtra resultados
- [ ] Escribir "12345" (SAP) filtra resultados
- [ ] Filtrado es tiempo real
- [ ] Datalist actualiza correctamente

### Material Selection
- [ ] Puedo seleccionar material del dropdown
- [ ] Se llena el campo de cantidad
- [ ] Se llena el campo de precio
- [ ] Valores son correctos

### Modal Description
- [ ] Botón "Ver Descripción" visible
- [ ] Click abre modal
- [ ] Modal muestra Código SAP
- [ ] Modal muestra Descripción corta
- [ ] Modal muestra Descripción ampliada ✨
- [ ] Modal muestra Precio USD
- [ ] Modal muestra Unidad
- [ ] Botón Cerrar funciona
- [ ] Botón "Agregar desde modal" funciona

### Material Addition
- [ ] Material se agrega a tabla
- [ ] Tabla muestra: Código, Descripción, Cantidad, Precio
- [ ] Botón eliminar funciona
- [ ] Puedo agregar múltiples materiales

### UI/UX
- [ ] Sin errores en consola
- [ ] Diseño responsive (mobile ok)
- [ ] Colores profesionales
- [ ] Espaciado adecuado
- [ ] Tipografía clara

---

## 🎯 META FINAL

```
Sesión 4 completa cuando:
✅ UI redesigned y aprobada
✅ Modal funcionando y bonito
✅ Testing completado
✅ Sin errores en consola
✅ Documentación actualizada
✅ Ready para Step 3 (validaciones)
```

---

## 📞 USUARIO DEMO

- **Usuario:** 2 (Juan Levi)
- **Acceso:** Centros [1008, 1050], Almacenes [1, 12, 101, 9002, 9003]
- **Test:** Agregar "TORNILLO" desde búsqueda

---

**Hora de inicio:** 2 de Noviembre 2025
**Tiempo estimado:** 2.5 - 3 horas
**Progreso esperado:** 65% → 85%

¡Vamos! 🚀
