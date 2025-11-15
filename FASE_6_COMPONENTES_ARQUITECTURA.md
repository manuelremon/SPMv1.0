# FASE 6 - Sprint 2: Component Architecture & Visual Guide

**Objetivo**: Construir 15+ componentes reutilizables + integración CRUD completa  
**Estimado**: 7 horas de desarrollo  
**Status**: Ready to Start

---

## 📐 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                        App.jsx                              │
│  (Router + Auth Check + CSRF Token Fetch)                   │
└────┬──────────────────────────────────────────────┬─────────┘
     │                                              │
     ├─────────────────┬─────────────────┐         │
     │                 │                 │         │
  ProtectedRoute    ProtectedRoute   ProtectedRoute │
  /dashboard        /solicitudes      /account      │
     │                 │                 │         │
  Dashboard         Solicitudes       Account       │
  - Bienvenida      - List             - Profile    │
  - Stats           - Detail           - Security   │
  - Quick Links     - Create           - Settings   │
                    - Edit                         │
                                                   │
                     (Pública)                      │
                        │                           │
                      Login────────────────────────┘
                      - Form
                      - Validation
                      - Error Display

Components Compartidos: Layout, Button, Input, Card, Badge, Modal, etc.
Services Compartidos: api.js, auth.js, csrf.js
Store Compartido: authStore.js
```

---

## 🏗️ Estructura de Directorios Final

```
frontend_v2/src/
├── components/
│   ├── auth/
│   │   ├── Login.jsx ✅ (ya existe)
│   │   └── ProtectedRoute.jsx ✅ (ya existe)
│   │
│   ├── layout/
│   │   └── Layout.jsx ✅ (ya existe)
│   │
│   ├── solicitudes/
│   │   ├── Dashboard.jsx ✅ (ya existe - mejorado)
│   │   ├── SolicitudList.jsx 🆕
│   │   ├── SolicitudDetail.jsx 🆕
│   │   ├── CreateSolicitud.jsx 🆕
│   │   ├── EditSolicitud.jsx 🆕
│   │   └── SolicitudForm.jsx 🆕 (compartido)
│   │
│   ├── planner/
│   │   └── PlannerView.jsx 🆕
│   │
│   ├── account/
│   │   ├── AccountPage.jsx 🆕
│   │   ├── AccountProfile.jsx 🆕
│   │   └── AccountSecurity.jsx 🆕
│   │
│   └── shared/
│       ├── Button.jsx 🆕
│       ├── Input.jsx 🆕
│       ├── TextArea.jsx 🆕
│       ├── Select.jsx 🆕
│       ├── Card.jsx 🆕
│       ├── Badge.jsx 🆕
│       ├── Table.jsx 🆕
│       ├── Modal.jsx 🆕
│       ├── Loading.jsx 🆕
│       ├── EmptyState.jsx 🆕
│       ├── ErrorAlert.jsx 🆕
│       └── Pagination.jsx 🆕
│
├── hooks/
│   ├── useAsync.js 🆕 (para data fetching)
│   └── useForm.js 🆕 (para form handling)
│
├── store/
│   └── authStore.js ✅ (ya existe)
│
├── services/
│   ├── api.js ✅ (ya existe)
│   ├── auth.js ✅ (ya existe)
│   ├── csrf.js ✅ (ya existe)
│   ├── solicitudes.js 🆕
│   ├── planner.js 🆕
│   └── account.js 🆕
│
└── App.jsx ✅ (ya existe)
```

---

## 📋 Componentes por Prioridad

### Tier 1: Componentes Base (Shared) - 1h
**Sin estos, el resto no funciona**

```javascript
// Button.jsx
<Button 
  variant="primary|secondary|danger" 
  size="sm|md|lg" 
  loading={false}
  disabled={false}
  onClick={handler}
>
  Click me
</Button>

// Input.jsx
<Input 
  label="Nombre" 
  type="text|password|email" 
  value={value} 
  onChange={handler}
  error={error}
  required={true}
/>

// Card.jsx
<Card title="Título" footer={actions}>
  Contenido
</Card>

// Loading.jsx
<Loading message="Cargando datos..." />

// EmptyState.jsx
<EmptyState 
  icon={IconComponent} 
  title="Sin resultados"
  description="No hay solicitudes"
  action={<Button>Crear Nueva</Button>}
/>

// Badge.jsx
<Badge variant="success|warning|danger|info">Estado</Badge>
```

### Tier 2: Auth & Layout (ya existen) ✅

```javascript
// ProtectedRoute.jsx ✅
// Layout.jsx ✅
// Login.jsx ✅
```

### Tier 3: Formularios & Tables - 2.5h

```javascript
// SolicitudForm.jsx (compartido)
<SolicitudForm 
  initial={data}
  onSubmit={handler}
  loading={false}
/>

// Table.jsx
<Table 
  columns={[
    { key: 'id', label: 'ID', width: '80px' },
    { key: 'asunto', label: 'Asunto', width: '300px' },
    { key: 'estado', label: 'Estado', render: (val) => <Badge>{val}</Badge> },
    { key: 'acciones', label: 'Acciones', render: (row) => <Actions /> }
  ]}
  data={rows}
  onRow={(row) => navigate(`/solicitudes/${row.id}`)}
/>

// Pagination.jsx
<Pagination 
  page={1} 
  pageSize={10} 
  total={100}
  onChange={(page) => setPage(page)}
/>
```

### Tier 4: Páginas Solicitudes - 2h

```javascript
// SolicitudList.jsx
- GET /api/solicitudes (con paginación)
- Filters: estado, search, fecha
- Actions: Create, Edit, Delete
- Responsive table

// SolicitudDetail.jsx
- GET /api/solicitudes/:id
- Timeline de cambios
- Materiales relacionados
- Actions: Edit, Delete, Back

// CreateSolicitud.jsx
- Form: asunto, descripción, prioridad
- POST /api/solicitudes
- Validación
- Success message + redirect

// EditSolicitud.jsx
- GET /api/solicitudes/:id (pre-llenar)
- PUT /api/solicitudes/:id
- Validación
```

### Tier 5: Planner - 0.5h

```javascript
// PlannerView.jsx
- GET /api/planner
- Timeline simple (tabla)
- Mostrar fechas, responsables
- Filtro por mes
```

### Tier 6: Account - 1h

```javascript
// AccountProfile.jsx
- GET /api/auth/profile
- PUT /api/auth/profile
- Campos: nombre, email, teléfono, etc.

// AccountSecurity.jsx
- POST /api/auth/change-password
- Validación contraseña
- Confirmación
```

---

## 🔄 Dependency Graph

```
App.jsx
├── ProtectedRoute.jsx
│   └── Layout.jsx
│       ├── Dashboard.jsx (uses shared components)
│       ├── SolicitudList.jsx
│       │   ├── Table.jsx
│       │   ├── Pagination.jsx
│       │   ├── Button.jsx
│       │   └── Badge.jsx
│       ├── SolicitudDetail.jsx
│       │   ├── Card.jsx
│       │   └── Button.jsx
│       ├── SolicitudCreate.jsx
│       │   ├── SolicitudForm.jsx
│       │   │   ├── Input.jsx
│       │   │   ├── TextArea.jsx
│       │   │   ├── Select.jsx
│       │   │   └── Button.jsx
│       │   └── ErrorAlert.jsx
│       ├── PlannerView.jsx
│       │   └── Table.jsx
│       └── AccountPage.jsx
│           ├── AccountProfile.jsx
│           │   └── SolicitudForm.jsx (reutilizado)
│           └── AccountSecurity.jsx
│               └── Input.jsx
│
└── Login.jsx (no protegido)
    ├── Input.jsx
    ├── Button.jsx
    └── ErrorAlert.jsx
```

---

## 📊 Sprint 2 Task Breakdown

### Task 5.1: Shared Components (1 hora) ⭐ START HERE

**Crear 10 componentes base** en `src/components/shared/`:

1. **Button.jsx** (20 líneas)
   ```jsx
   function Button({ variant = 'primary', size = 'md', loading, ...props }) {
     const variants = {
       primary: 'bg-blue-600 hover:bg-blue-700 text-white',
       secondary: 'bg-gray-300 hover:bg-gray-400 text-black',
       danger: 'bg-red-600 hover:bg-red-700 text-white'
     }
     return <button className={`${variants[variant]} px-4 py-2 rounded`} {...props} />
   }
   ```

2. **Input.jsx** (30 líneas)
   ```jsx
   function Input({ label, error, ...props }) {
     return (
       <div className="space-y-1">
         {label && <label className="block text-sm font-medium">{label}</label>}
         <input className={`w-full px-3 py-2 border rounded ${error ? 'border-red-500' : 'border-gray-300'}`} {...props} />
         {error && <span className="text-red-600 text-sm">{error}</span>}
       </div>
     )
   }
   ```

3. **Card.jsx** (25 líneas)
4. **Badge.jsx** (20 líneas)
5. **Loading.jsx** (25 líneas)
6. **EmptyState.jsx** (30 líneas)
7. **Table.jsx** (50 líneas)
8. **Pagination.jsx** (40 líneas)
9. **Modal.jsx** (40 líneas)
10. **ErrorAlert.jsx** (20 líneas)

**Prioridad**: CRITICAL - Los demás componentes dependen de estos

---

### Task 5.2: Service Layer (0.5 horas)

**Crear 3 services** en `src/services/`:

1. **solicitudes.js** - Endpoints de solicitudes
   ```javascript
   export const solicitudesService = {
     list: (params) => api.get('/solicitudes', { params }),
     get: (id) => api.get(`/solicitudes/${id}`),
     create: (data) => api.post('/solicitudes', data),
     update: (id, data) => api.put(`/solicitudes/${id}`, data),
     delete: (id) => api.delete(`/solicitudes/${id}`)
   }
   ```

2. **planner.js** - Endpoints del planner
3. **account.js** - Endpoints de cuenta

---

### Task 5.3: Custom Hooks (0.5 horas)

**Crear 2 hooks** en `src/hooks/`:

1. **useAsync.js** - Para data fetching con loading/error
   ```javascript
   export function useAsync(asyncFunction, immediate = true) {
     const [state, setState] = useState({ status: 'idle', data: null, error: null })
     
     const execute = useCallback(async () => {
       setState({ status: 'pending', data: null, error: null })
       try {
         const response = await asyncFunction()
         setState({ status: 'success', data: response, error: null })
         return response
       } catch (error) {
         setState({ status: 'error', data: null, error })
       }
     }, [asyncFunction])
     
     useEffect(() => {
       if (immediate) execute()
     }, [execute, immediate])
     
     return { ...state, execute }
   }
   ```

2. **useForm.js** - Para manejo de formularios

---

### Task 5.4: Páginas Solicitudes (2.5 horas)

#### 5.4.1 SolicitudList.jsx (90 líneas)
```jsx
function SolicitudList() {
  const [solicitudes, setSolicitudes] = useState([])
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ estado: 'todos' })
  const [loading, setLoading] = useState(false)
  
  const { status, data, error, execute } = useAsync(() => 
    solicitudesService.list({ page, ...filters })
  )
  
  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'asunto', label: 'Asunto' },
    { key: 'estado', label: 'Estado', render: (val) => <Badge>{val}</Badge> },
    { key: 'usuario.nombre', label: 'Usuario' },
    { key: 'acciones', label: '', render: (row) => (
      <div className="flex gap-2">
        <Button size="sm" onClick={() => navigate(`/solicitudes/${row.id}`)}>Ver</Button>
        <Button size="sm" variant="secondary" onClick={() => navigate(`/solicitudes/${row.id}/edit`)}>Editar</Button>
        <Button size="sm" variant="danger" onClick={() => handleDelete(row.id)}>Eliminar</Button>
      </div>
    )}
  ]
  
  return (
    <Layout>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Solicitudes</h1>
          <Button onClick={() => navigate('/solicitudes/new')}>Nueva Solicitud</Button>
        </div>
        
        <Filters value={filters} onChange={setFilters} />
        
        {loading && <Loading />}
        {error && <ErrorAlert error={error} />}
        {data && data.results.length === 0 && <EmptyState />}
        {data && <Table columns={columns} data={data.results} />}
        {data && <Pagination page={page} total={data.total} onChange={setPage} />}
      </div>
    </Layout>
  )
}
```

#### 5.4.2 SolicitudDetail.jsx (70 líneas)
```jsx
function SolicitudDetail() {
  const { id } = useParams()
  const { status, data: solicitud, error } = useAsync(() => 
    solicitudesService.get(id)
  )
  
  if (status === 'pending') return <Loading />
  if (status === 'error') return <ErrorAlert error={error} />
  if (!solicitud) return <EmptyState />
  
  return (
    <Layout>
      <div className="space-y-4">
        <Button variant="secondary" onClick={() => window.history.back()}>Volver</Button>
        
        <Card title={solicitud.asunto}>
          <div className="space-y-4">
            <div><strong>Estado:</strong> <Badge>{solicitud.estado}</Badge></div>
            <div><strong>Descripción:</strong> {solicitud.descripcion}</div>
            <div><strong>Fecha:</strong> {new Date(solicitud.fecha_creacion).toLocaleDateString()}</div>
            <div><strong>Usuario:</strong> {solicitud.usuario.nombre}</div>
          </div>
        </Card>
        
        <div className="flex gap-2">
          <Button onClick={() => navigate(`/solicitudes/${id}/edit`)}>Editar</Button>
          <Button variant="danger" onClick={() => handleDelete(id)}>Eliminar</Button>
        </div>
      </div>
    </Layout>
  )
}
```

#### 5.4.3 SolicitudForm.jsx (100 líneas)
```jsx
function SolicitudForm({ initial, onSubmit, loading }) {
  const [formData, setFormData] = useState(initial || {
    asunto: '',
    descripcion: '',
    prioridad: 'media'
  })
  const [errors, setErrors] = useState({})
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }
  
  const validate = () => {
    const newErrors = {}
    if (!formData.asunto.trim()) newErrors.asunto = 'Requerido'
    if (!formData.descripcion.trim()) newErrors.descripcion = 'Requerido'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) onSubmit(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input 
        label="Asunto" 
        name="asunto" 
        value={formData.asunto} 
        onChange={handleChange}
        error={errors.asunto}
      />
      <TextArea 
        label="Descripción" 
        name="descripcion" 
        value={formData.descripcion} 
        onChange={handleChange}
        error={errors.descripcion}
      />
      <Select 
        label="Prioridad" 
        name="prioridad" 
        value={formData.prioridad} 
        onChange={handleChange}
        options={[
          { value: 'baja', label: 'Baja' },
          { value: 'media', label: 'Media' },
          { value: 'alta', label: 'Alta' }
        ]}
      />
      <Button type="submit" disabled={loading}>
        {loading ? 'Guardando...' : 'Guardar'}
      </Button>
    </form>
  )
}
```

#### 5.4.4 CreateSolicitud.jsx (50 líneas)
```jsx
function CreateSolicitud() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (formData) => {
    setLoading(true)
    try {
      const res = await solicitudesService.create(formData)
      navigate(`/solicitudes/${res.id}`)
    } catch (error) {
      // ErrorAlert handled by store
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Layout>
      <div className="space-y-4">
        <Button variant="secondary" onClick={() => navigate('/solicitudes')}>Volver</Button>
        <Card title="Nueva Solicitud">
          <SolicitudForm onSubmit={handleSubmit} loading={loading} />
        </Card>
      </div>
    </Layout>
  )
}
```

#### 5.4.5 EditSolicitud.jsx (60 líneas)
```jsx
function EditSolicitud() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { status, data: solicitud } = useAsync(() => solicitudesService.get(id))
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (formData) => {
    setLoading(true)
    try {
      await solicitudesService.update(id, formData)
      navigate(`/solicitudes/${id}`)
    } finally {
      setLoading(false)
    }
  }
  
  if (status === 'pending') return <Loading />
  if (!solicitud) return <EmptyState />
  
  return (
    <Layout>
      <Card title="Editar Solicitud">
        <SolicitudForm initial={solicitud} onSubmit={handleSubmit} loading={loading} />
      </Card>
    </Layout>
  )
}
```

---

### Task 5.5: Planner (0.5 horas)

#### 5.5.1 PlannerView.jsx (80 líneas)
```jsx
function PlannerView() {
  const [month, setMonth] = useState(new Date())
  const { status, data: items } = useAsync(() => 
    plannerService.list({ month: month.toISOString().slice(0, 7) })
  )
  
  const nextMonth = () => setMonth(new Date(month.getFullYear(), month.getMonth() + 1))
  const prevMonth = () => setMonth(new Date(month.getFullYear(), month.getMonth() - 1))
  
  return (
    <Layout>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Planificador</h1>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={prevMonth}>◀</Button>
            <span className="px-4 py-2">{month.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}</span>
            <Button variant="secondary" onClick={nextMonth}>▶</Button>
          </div>
        </div>
        
        {status === 'pending' && <Loading />}
        {items && <SimpleTimelineTable items={items} />}
      </div>
    </Layout>
  )
}
```

---

### Task 5.6: Account (1 hora)

#### 5.6.1 AccountProfile.jsx (80 líneas)
```jsx
function AccountProfile() {
  const { user } = useAuthStore()
  const [formData, setFormData] = useState(user || {})
  const [loading, setLoading] = useState(false)
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await accountService.updateProfile(formData)
      // update auth store
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input label="Nombre" name="nombre" value={formData.nombre} onChange={handleChange} />
      <Input label="Email" name="email" value={formData.email} disabled />
      <Input label="Teléfono" name="telefono" value={formData.telefono || ''} onChange={handleChange} />
      <Select label="Departamento" name="departamento" value={formData.departamento || ''} onChange={handleChange} />
      <Button type="submit" disabled={loading}>Guardar Cambios</Button>
    </form>
  )
}
```

#### 5.6.2 AccountSecurity.jsx (100 líneas)
```jsx
function AccountSecurity() {
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setPasswords(prev => ({ ...prev, [name]: value }))
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (passwords.new !== passwords.confirm) {
      setMessage('error: Las contraseñas no coinciden')
      return
    }
    setLoading(true)
    try {
      await accountService.changePassword(passwords)
      setMessage('success: Contraseña actualizada')
      setPasswords({ current: '', new: '', confirm: '' })
    } catch (error) {
      setMessage('error: ' + error.message)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {message && <ErrorAlert message={message} />}
      <Input label="Contraseña Actual" type="password" name="current" value={passwords.current} onChange={handleChange} required />
      <Input label="Nueva Contraseña" type="password" name="new" value={passwords.new} onChange={handleChange} required />
      <Input label="Confirmar Contraseña" type="password" name="confirm" value={passwords.confirm} onChange={handleChange} required />
      <Button type="submit" disabled={loading}>Cambiar Contraseña</Button>
    </form>
  )
}
```

#### 5.6.3 AccountPage.jsx (50 líneas)
```jsx
function AccountPage() {
  const [activeTab, setActiveTab] = useState('profile')
  
  return (
    <Layout>
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Mi Cuenta</h1>
        
        <div className="flex border-b">
          <button 
            onClick={() => setActiveTab('profile')}
            className={`px-4 py-2 ${activeTab === 'profile' ? 'border-b-2 border-blue-600' : ''}`}
          >
            Perfil
          </button>
          <button 
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 ${activeTab === 'security' ? 'border-b-2 border-blue-600' : ''}`}
          >
            Seguridad
          </button>
        </div>
        
        {activeTab === 'profile' && (
          <Card title="Mi Perfil">
            <AccountProfile />
          </Card>
        )}
        
        {activeTab === 'security' && (
          <Card title="Seguridad">
            <AccountSecurity />
          </Card>
        )}
      </div>
    </Layout>
  )
}
```

---

## 🧪 Testing Checklist

Para cada componente:
- [ ] Renderiza sin errores
- [ ] Props funcional
- [ ] Eventos funcionan (click, submit, etc.)
- [ ] Validación funciona
- [ ] Loading states visibles
- [ ] Error handling visible
- [ ] Responsive (desktop + mobile)
- [ ] Accesibilidad básica (labels, aria-*)

---

## 📈 Time Estimates (por Task)

| Task | Componentes | Estimado | Notas |
|------|-----------|----------|-------|
| 5.1 | Button, Input, Card, Badge, Loading, etc. | 1.0h | Crítico - hacerlo primero |
| 5.2 | Services (solicitudes, planner, account) | 0.5h | Simple wrappers |
| 5.3 | useAsync, useForm hooks | 0.5h | Reutilizable |
| 5.4 | SolicitudList, Detail, Create, Edit | 2.5h | CRUD completo |
| 5.5 | PlannerView simple | 0.5h | Timeline básico |
| 5.6 | AccountProfile, Security, Page | 1.0h | Formularios |
| 5.7 | Testing + bug fixes | 0.5h | Validación |
| **Total** | **15+ componentes** | **~7h** | Spread en 2-3 sesiones |

---

## 🚀 Recomendación de Inicio

### Opción 1: Secuencial (Recomendado)
```
1. Task 5.1 (1h) - Shared components
2. Task 5.2 + 5.3 (1h) - Services + hooks
3. Task 5.4 (2.5h) - Solicitudes CRUD
4. Task 5.5 + 5.6 (1.5h) - Planner + Account
5. Testing (0.5h) - Validación y fixes
```

### Opción 2: Paralelo (Si hay múltiples devs)
```
Dev 1: Tasks 5.1, 5.4
Dev 2: Tasks 5.2, 5.3, 5.5, 5.6
```

---

## 📚 Reference Code Patterns

### Pattern 1: useAsync Hook
```javascript
const { status, data, error, execute } = useAsync(asyncFn)
// status: 'idle', 'pending', 'success', 'error'
// data: { ...response }
// error: Error object
// execute: función para re-ejecutar
```

### Pattern 2: useForm Hook (to create)
```javascript
const { values, errors, touched, handleChange, handleSubmit } = useForm({
  initialValues: { name: '', email: '' },
  onSubmit: async (values) => { /* submit */ },
  validate: (values) => { /* return errors */ }
})
```

### Pattern 3: Error Handling
```javascript
try {
  await api.post('/endpoint', data)
  showSuccess('Operación exitosa')
} catch (error) {
  const message = error.response?.data?.error?.message || error.message
  showError(message)
}
```

---

## ✅ Definition of Done

Cada componente se considera "done" cuando:
- [x] Se renderiza sin errores
- [x] Cumple con requirements funcionales
- [x] Tiene error handling
- [x] Responsivo (desktop + mobile)
- [x] Testeado manualmente
- [x] Documentado con JSDoc
- [x] Sin warnings en console
- [x] Integrado en routing

---

**Estado**: Ready for Sprint 2 Development  
**Próximo Step**: Comenzar Task 5.1 - Shared Components  
**Duración Estimada**: 7 horas (completable en 2-3 sesiones)

