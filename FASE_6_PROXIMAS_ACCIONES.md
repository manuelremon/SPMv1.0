# 🚀 FASE 6: Próximas Acciones - Roadmap Inmediato

**Documento**: Quick Reference para continuar desarrollo  
**Última Actualización**: 15 de noviembre de 2025  
**Siguiente Sesión**: Sprint 2 - Componentes Principales

---

## 📍 Dónde Estamos Ahora

```
✅ Fase 1-5: 100% Completado
  - Backend v2 securizado (rate limiting, CSRF, JWT refresh, headers OWASP)
  - 4 commits de Phase 5
  
✅ Fase 6 Sprint 1: 100% Completado
  - Frontend v2 scaffold (Vite + React)
  - Auth flow completo (login, logout, protected routes)
  - API services (axios + interceptores)
  - 18 archivos nuevos, 1 commit

📊 Progreso Total: 60% del proyecto
```

---

## 🎯 Siguiente Paso Inmediato (AHORA)

### Opción A: Comenzar Sprint 2 Directamente
**Si quieres continuar con desarrollo:**

1. **Leer documentación**:
   - `FASE_6_SPRINT2_PLAN.md` - Plan detallado de Sprint 2
   - `FASE_6_COMPONENTES_ARQUITECTURA.md` - Arquitectura y código

2. **Comenzar Task 5.1** (Shared Components):
   - Crear `src/components/shared/Button.jsx` (20 líneas)
   - Crear `src/components/shared/Input.jsx` (30 líneas)
   - Crear `src/components/shared/Card.jsx` (25 líneas)
   - ... (otros 7 componentes base)
   - **Tiempo**: ~1 hora
   - **Crítico**: Hacerlo primero, otros dependen

3. **Validar setup**:
   ```bash
   cd frontend_v2
   npm run dev
   ```
   - Debe abrir en http://localhost:5173
   - No debe tener errores en consola

### Opción B: Validar Setup Actual Primero
**Si quieres asegurar que todo está bien:**

```bash
# Terminal 1: Backend
cd backend_v2
python app.py
# → Backend en http://localhost:5000

# Terminal 2: Frontend
cd frontend_v2
npm install  # (primero)
npm run dev
# → Frontend en http://localhost:5173

# Terminal 3: Testing manual
# - Ir a http://localhost:5173
# - Ver que redirige a /login
# - Login con admin/admin123
# - Ver Dashboard
# - Click Logout → back a /login
```

---

## 📋 Task Board - Sprint 2

### Fase 6 Sprint 2: Componentes Principales (7 horas)

#### Priority 1: Shared Components (1h) ⭐ HACER PRIMERO
**Status**: Not Started  
**Blocker**: Sí - Otros componentes dependen  
**Files**: 10 nuevos en `src/components/shared/`

```
□ Button.jsx (20 líneas)
□ Input.jsx (30 líneas)
□ TextArea.jsx (25 líneas)
□ Select.jsx (35 líneas)
□ Card.jsx (25 líneas)
□ Badge.jsx (20 líneas)
□ Table.jsx (50 líneas)
□ Modal.jsx (40 líneas)
□ Loading.jsx (25 líneas)
□ EmptyState.jsx (30 líneas)

Documento de referencia: FASE_6_COMPONENTES_ARQUITECTURA.md (sección "Tier 1")
```

#### Priority 2: Service Layer + Hooks (1h)
**Status**: Not Started  
**Dependencies**: Nada especial  
**Files**: 5 nuevos en `src/services/` + `src/hooks/`

```
□ services/solicitudes.js
□ services/planner.js
□ services/account.js
□ hooks/useAsync.js
□ hooks/useForm.js

Documento de referencia: FASE_6_COMPONENTES_ARQUITECTURA.md (sección "Task 5.2 & 5.3")
```

#### Priority 3: Solicitudes CRUD (2.5h)
**Status**: Not Started  
**Dependencies**: Priority 1 + Priority 2  
**Files**: 5 nuevos en `src/components/solicitudes/`

```
□ SolicitudList.jsx (90 líneas)
□ SolicitudDetail.jsx (70 líneas)
□ SolicitudForm.jsx (100 líneas - shared)
□ CreateSolicitud.jsx (50 líneas)
□ EditSolicitud.jsx (60 líneas)

Documento de referencia: FASE_6_COMPONENTES_ARQUITECTURA.md (sección "Task 5.4")
Requisito: Endpoints en backend_v2:
  ✅ GET /api/solicitudes
  ✅ GET /api/solicitudes/:id
  ✅ POST /api/solicitudes
  ✅ PUT /api/solicitudes/:id
  ✅ DELETE /api/solicitudes/:id
```

#### Priority 4: Planner (0.5h)
**Status**: Not Started  
**Dependencies**: Priority 1 + Priority 2  
**Files**: 1 nuevo en `src/components/planner/`

```
□ PlannerView.jsx (80 líneas)

Documento de referencia: FASE_6_COMPONENTES_ARQUITECTURA.md (sección "Task 5.5")
```

#### Priority 5: Account (1h)
**Status**: Not Started  
**Dependencies**: Priority 1 + Priority 2  
**Files**: 3 nuevos en `src/components/account/`

```
□ AccountProfile.jsx (80 líneas)
□ AccountSecurity.jsx (100 líneas)
□ AccountPage.jsx (50 líneas)

Documento de referencia: FASE_6_COMPONENTES_ARQUITECTURA.md (sección "Task 5.6")
```

#### Priority 6: Testing + Bug Fixes (0.5h)
**Status**: Not Started  
**Dependencias**: Todo debe estar hecho primero

```
□ Manual testing CRUD flow
□ Verificar error handling
□ Validar responsive design
□ Fix bugs identificados
□ Commit final con mensaje "feat(fase-6): componentes principales"
```

---

## 🔗 Estructura de Rutas Esperadas Después de Sprint 2

```
/ → Redirect a /dashboard (si auth) o /login (si no)
├─ /login (Pública)
│  └─ Login.jsx (ya existe)
│
├─ /dashboard (Protegida)
│  └─ Dashboard.jsx (ya existe - puede mejorar)
│
├─ /solicitudes (Protegida)
│  ├─ SolicitudList.jsx (nueva)
│  ├─ /solicitudes/new → CreateSolicitud.jsx (nueva)
│  ├─ /solicitudes/:id → SolicitudDetail.jsx (nueva)
│  └─ /solicitudes/:id/edit → EditSolicitud.jsx (nueva)
│
├─ /planner (Protegida)
│  └─ PlannerView.jsx (nueva)
│
├─ /account (Protegida)
│  ├─ AccountProfile.jsx (nueva)
│  └─ AccountSecurity.jsx (nueva)
│
└─ 404 (Fallback)
```

**Actualización necesaria en App.jsx**:
```javascript
// Agregar rutas nuevas
<Route path="/solicitudes" element={<ProtectedRoute><SolicitudList /></ProtectedRoute>} />
<Route path="/solicitudes/new" element={<ProtectedRoute><CreateSolicitud /></ProtectedRoute>} />
<Route path="/solicitudes/:id" element={<ProtectedRoute><SolicitudDetail /></ProtectedRoute>} />
<Route path="/solicitudes/:id/edit" element={<ProtectedRoute><EditSolicitud /></ProtectedRoute>} />
<Route path="/planner" element={<ProtectedRoute><PlannerView /></ProtectedRoute>} />
<Route path="/account" element={<ProtectedRoute><AccountPage /></ProtectedRoute>} />
```

---

## 📚 Documentación Disponible

**Antes de comenzar, lee estas en orden**:

1. ✅ `FASE_6_SPRINT1_COMPLETADO.md` - Lo que ya se hizo
2. ✅ `FASE_6_SPRINT2_PLAN.md` - Plan detallado con pseudocódigo
3. ✅ `FASE_6_COMPONENTES_ARQUITECTURA.md` - Architecture + código actual
4. 📍 `PROYECTO_STATUS_ACTUAL.md` - Estado general del proyecto
5. `FASE_5_SEGURIDAD_REFORZADA.md` - Detalles de seguridad (si necesitas)

---

## 🛠️ Herramientas & Dependencias

### Frontend v2 - Dependencias Actuales
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.6.2",
  "zustand": "^4.4.1",
  "tailwindcss": "^3.3.6",
  "lucide-react": "^latest"
}
```

### Backend v2 - Endpoints Seguros
```
✅ GET /api/csrf - Obtener CSRF token
✅ POST /api/auth/register - Registro
✅ POST /api/auth/login - Login
✅ GET /api/auth/me - Usuario actual
✅ POST /api/auth/refresh - Refresh token
✅ POST /api/auth/logout - Logout
✅ GET /api/auth/change-password - Cambiar pwd
✅ GET /api/solicitudes - Listar (con paginación)
✅ GET /api/solicitudes/:id - Detalles
✅ POST /api/solicitudes - Crear
✅ PUT /api/solicitudes/:id - Editar
✅ DELETE /api/solicitudes/:id - Eliminar
⏳ GET /api/planner - Timeline
⏳ GET /api/auth/profile - Perfil usuario
⏳ PUT /api/auth/profile - Editar perfil
```

**Verificar que backend expone todos estos endpoints**:
```bash
cd backend_v2
python -m pytest tests/ -v  # (si existen tests)
# O verificar manualmente con curl
```

---

## ✅ Validation Checklist

Antes de marcar Sprint 2 como "done":

### Funcionalidad CRUD
- [ ] SolicitudList carga datos del backend
- [ ] SolicitudDetail muestra datos correctos
- [ ] CreateSolicitud crea nueva solicitud (POST exitoso)
- [ ] EditSolicitud actualiza datos (PUT exitoso)
- [ ] Delete solicitud funciona
- [ ] Paginación funciona (si tiene >10 registros)

### Error Handling
- [ ] Backend retorna error → se muestra en UI
- [ ] Token inválido → redirect a /login
- [ ] CSRF token missing → error visible
- [ ] Network error → error message visible
- [ ] Validación client-side → previene submit

### Seguridad
- [ ] CSRF token en localStorage (check DevTools)
- [ ] X-CSRF-Token en headers (check Network tab)
- [ ] Cookies HttpOnly presentes (check DevTools Cookies)
- [ ] Rutas protegidas redirigen a /login
- [ ] Logout limpia cookies + localStorage

### UI/UX
- [ ] Responsive en mobile (375px)
- [ ] Responsive en desktop (1920px)
- [ ] Loading states visibles
- [ ] Error messages claros
- [ ] Navigation funciona
- [ ] Sidebar colapsable

### Performance
- [ ] No hay warnings en console
- [ ] Lighthouse score > 80
- [ ] Images optimizadas
- [ ] Code splitting funciona (si aplica)

---

## 🚨 Problemas Conocidos & Soluciones

### Problema: "Cannot find module 'lucide-react'"
**Solución**:
```bash
cd frontend_v2
npm install lucide-react
```

### Problema: Backend retorna CORS error
**Solución**:
```python
# En backend_v2/app.py, verificar:
from flask_cors import CORS
CORS(app, origins=["http://localhost:5173"], allow_credentials=True)
```

### Problema: "401 Unauthorized" en refresh
**Solución**:
- Verificar que refresh_token cookie está presente
- Verificar que backend expone POST /api/auth/refresh
- Verificar que token refresh no está expirado (7 días)

### Problema: Form no submite
**Solución**:
- Verificar validación (error messages en console)
- Verificar que onSubmit handler está asignado
- Verificar que Button type="submit" en form

---

## 📊 Commits Esperados en Sprint 2

Después de completar Sprint 2, esperar ~2-3 commits:

```
Commit 1: "feat(fase-6): shared components - button, input, card, etc."
- 10 nuevos archivos en src/components/shared/
- ~400 líneas de código

Commit 2: "feat(fase-6): services y hooks - solicitudes, planner, useAsync"
- 5 nuevos archivos en src/services/ + src/hooks/
- ~200 líneas de código

Commit 3: "feat(fase-6): componentes principales - CRUD solicitudes, planner, account"
- 8 nuevos archivos en src/components/
- ~600 líneas de código
- Update App.jsx con nuevas rutas
- Update layout navigation

Commit 4 (opcional): "fix(fase-6): bug fixes y ajustes de styling"
```

---

## 🎯 Objetivo Final de Sprint 2

```
┌────────────────────────────────────────────┐
│  Después de completar Sprint 2:            │
│                                            │
│  ✅ 15+ componentes reutilizables        │
│  ✅ CRUD completo para Solicitudes       │
│  ✅ Planner básico funcional             │
│  ✅ Account/Perfil del usuario           │
│  ✅ Integración completa con backend     │
│  ✅ Error handling y validación          │
│  ✅ Responsive design en todas partes    │
│  ✅ Seguridad (CSRF, JWT, cookies)      │
│                                            │
│  Progreso: 50% → 70% del proyecto        │
│                                            │
│  Próxima: Sprint 3 (Testing & Polish)    │
└────────────────────────────────────────────┘
```

---

## 🚀 Cómo Empezar Ahora Mismo

### Step 1: Preparar el Entorno
```bash
# En una terminal:
cd c:\Users\MANUE\Documents\GitHub\SPMv1.0\frontend_v2
npm run dev
# → Frontend en http://localhost:5173

# En otra terminal:
cd c:\Users\MANUE\Documents\GitHub\SPMv1.0\backend_v2
python app.py
# → Backend en http://localhost:5000
```

### Step 2: Crear Componentes Base
```bash
# Crear carpeta shared si no existe
mkdir -p src/components/shared

# Crear Button.jsx
# Crear Input.jsx
# Crear Card.jsx
# ... (ver detalles en FASE_6_COMPONENTES_ARQUITECTURA.md)
```

### Step 3: Testear
```javascript
// En navegador, abrir DevTools Console:
console.log(localStorage.getItem('csrf_token'))  // Debe tener valor
console.log(document.cookie)  // Debe tener spm_token y spm_token_refresh
```

### Step 4: Commit
```bash
git add .
git commit -m "feat(fase-6): shared components - button, input, card, etc."
git push
```

---

## 📞 Quick Links

- **Frontend**: `c:\Users\MANUE\Documents\GitHub\SPMv1.0\frontend_v2`
- **Backend**: `c:\Users\MANUE\Documents\GitHub\SPMv1.0\backend_v2`
- **Documentación Sprint 2**: `FASE_6_SPRINT2_PLAN.md`
- **Arquitectura**: `FASE_6_COMPONENTES_ARQUITECTURA.md`
- **Estado Proyecto**: `PROYECTO_STATUS_ACTUAL.md`

---

## ⏱️ Timeboxing Sugerido

```
Sesión 1 (2h):
- 10min: Lectura documentación
- 50min: Shared Components (Priority 1)
- 60min: Services + Hooks (Priority 2)

Sesión 2 (3h):
- 2h 30min: Solicitudes CRUD (Priority 3)
- 30min: Testing + fixes

Sesión 3 (2h):
- 1h: Planner + Account (Priority 4 + 5)
- 30min: Final testing
- 30min: Commits y documentación
```

---

**Estado Actual**: ✅ Listo para Sprint 2  
**Próxima Acción**: Comenzar con Shared Components (Button, Input, Card)  
**Duración Estimada**: 7 horas  
**Fecha Recomendada**: Esta semana

¡A comenzar! 🚀

