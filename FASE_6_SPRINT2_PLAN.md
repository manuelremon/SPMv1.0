# FASE 6: Sprint 2 Plan - Componentes Principales

**Sprint Duration**: 2-3 horas de desarrollo  
**Objetivo**: Implementar 80% de componentes principales (Solicitudes + Account)  
**Estado Actual**: Sprint 1 ✅ (Scaffold terminado)

---

## 📋 Tareas Sprint 2

### Task 5.1: Componentes de Solicitudes

#### 5.1.1 SolicitudList Component
**Archivo**: `src/components/solicitudes/SolicitudList.jsx`

**Responsabilidades**:
- [ ] Obtener listado de solicitudes (`GET /api/solicitudes`)
- [ ] Mostrar tabla con datos
- [ ] Filtros por estado, fecha, usuario
- [ ] Paginación (10 registros/página)
- [ ] Acciones por fila (Ver, Editar, Eliminar)
- [ ] Botón "Nueva Solicitud"
- [ ] Loading state en tabla
- [ ] Error display
- [ ] Empty state

**Columnas Tabla**:
```
ID | Asunto | Estado | Fecha | Usuario | Acciones
```

**Estados Posibles**:
- Borrador
- Enviada
- En Proceso
- Completada
- Rechazada

**Interfaz de Datos** (esperado del backend):
```javascript
{
  id: string,
  asunto: string,
  descripcion: string,
  estado: string,
  fecha_creacion: ISO8601,
  fecha_actualizacion: ISO8601,
  usuario_id: string,
  usuario: { nombre: string, email: string },
  materiales_count: number
}
```

**Pseudocódigo**:
```javascript
const SolicitudList = () => {
  const [solicitudes, setSolicitudes] = useState([])
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ estado: 'todos', search: '' })
  const [loading, setLoading] = useState(false)
  
  // 1. Obtener solicitudes en mount + cuando cambian filters/page
  useEffect(() => {
    fetchSolicitudes()
  }, [page, filters])
  
  // 2. Funciones CRUD
  const fetchSolicitudes = async () => {}
  const deleteSolicitud = async (id) => {}
  const handleEdit = (id) => navigate(`/solicitudes/${id}/edit`)
  const handleView = (id) => navigate(`/solicitudes/${id}`)
  const handleCreate = () => navigate('/solicitudes/new')
  
  // 3. Render
  return (
    <Layout>
      <div className="space-y-4">
        <Header con botón Create />
        <Filters />
        <Table con datos />
        <Pagination />
      </div>
    </Layout>
  )
}
```

#### 5.1.2 SolicitudDetail Component
**Archivo**: `src/components/solicitudes/SolicitudDetail.jsx`

**Responsabilidades**:
- [ ] Obtener detalles de solicitud por ID
- [ ] Mostrar información legible
- [ ] Timeline de cambios
- [ ] Mostrar materiales asociados
- [ ] Botones: Editar, Volver, Eliminar
- [ ] Loading + Error handling
- [ ] Print button (opcional)

**Campos a Mostrar**:
```
Asunto
Descripción (texto largo)
Estado (con badge de color)
Prioridad
Fecha Creación
Última Actualización
Usuario Creador
Materiales (tabla mini)
Timeline de cambios
```

**Pseudocódigo**:
```javascript
const SolicitudDetail = () => {
  const { id } = useParams()
  const [solicitud, setSolicitud] = useState(null)
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    fetchSolicitud(id)
  }, [id])
  
  const fetchSolicitud = async () => {}
  const handleEdit = () => navigate(`/solicitudes/${id}/edit`)
  const handleDelete = () => {
    if (confirm('¿Eliminar?')) deleteSolicitud(id)
  }
  
  return (
    <Layout>
      <div className="space-y-4">
        <Back button />
        <Card con detalles />
        <TimelineCard />
        <MaterialesTable />
        <ActionButtons />
      </div>
    </Layout>
  )
}
```

#### 5.1.3 CreateSolicitud Component
**Archivo**: `src/components/solicitudes/CreateSolicitud.jsx`

**Responsabilidades**:
- [ ] Formulario para crear solicitud
- [ ] Campos: Asunto, Descripción, Prioridad, etc.
- [ ] Validación client-side
- [ ] File upload para materiales (opcional en Sprint 2)
- [ ] Submit `POST /api/solicitudes`
- [ ] Success notification
- [ ] Redirect a detail/list
- [ ] Error handling

**Campos Formulario**:
```
Asunto (texto, requerido)
Descripción (textarea, requerido)
Prioridad (select: Baja, Media, Alta)
Materiales (upload - opcional)
```

**Pseudocódigo**:
```javascript
const CreateSolicitud = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    asunto: '',
    descripcion: '',
    prioridad: 'media'
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  
  const validate = () => {}
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    try {
      const res = await axios.post('/api/solicitudes', formData)
      navigate(`/solicitudes/${res.data.id}`)
    } catch (error) {
      handleError(error)
    }
  }
  
  return (
    <Layout>
      <Form on submit>
        <Input asunto />
        <TextArea descripción />
        <Select prioridad />
        <SubmitButton />
      </Form>
    </Layout>
  )
}
```

#### 5.1.4 EditSolicitud Component
**Archivo**: `src/components/solicitudes/EditSolicitud.jsx`

**Responsabilidades**:
- [ ] Cargar solicitud actual
- [ ] Mismo formulario que Create pero con datos precargados
- [ ] PUT `PUT /api/solicitudes/:id`
- [ ] Success/Error notifications
- [ ] Validación

**Nota**: Puede compartir lógica con CreateSolicitud (Form component reutilizable)

---

### Task 5.2: Componentes de Planner

#### 5.2.1 PlannerView Component
**Archivo**: `src/components/planner/PlannerView.jsx`

**Responsabilidades**:
- [ ] Vista de gantt chart o calendario
- [ ] Mostrar solicitudes con timeline
- [ ] Arrastrar para reasignar
- [ ] Filtrar por usuario/fase
- [ ] Hoy resaltado

**Opciones de Implementación**:
1. **Gantt Simple**: HTML table con grid (semanas)
2. **Calendario**: FullCalendar (npm)
3. **Timeline Personalizado**: Tailwind + React

**MVP para Sprint 2**: Tabla simple con fechas

**Pseudocódigo**:
```javascript
const PlannerView = () => {
  const [solicitudes, setSolicitudes] = useState([])
  const [month, setMonth] = useState(new Date())
  
  useEffect(() => {
    fetchSolicitudes()
  }, [month])
  
  const fetchSolicitudes = async () => {
    // GET /api/solicitudes?start_date=...&end_date=...
  }
  
  return (
    <Layout>
      <div>
        <MonthSelector />
        <SimpleTimelineView solicitudes={solicitudes} />
      </div>
    </Layout>
  )
}
```

---

### Task 5.3: Componentes de Cuenta

#### 5.3.1 AccountProfile Component
**Archivo**: `src/components/account/AccountProfile.jsx`

**Responsabilidades**:
- [ ] Mostrar perfil actual
- [ ] Editar información personal
- [ ] Cambiar foto de perfil (opcional)
- [ ] PUT `PUT /api/auth/profile`
- [ ] Success message

**Campos**:
```
Nombre
Email
Teléfono
Departamento
Rol (read-only)
Avatar (opcional)
```

**Pseudocódigo**:
```javascript
const AccountProfile = () => {
  const { user } = useAuthStore()
  const [formData, setFormData] = useState(user)
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.put('/api/auth/profile', formData)
      showSuccess('Perfil actualizado')
    } catch (error) {
      showError(error.message)
    }
  }
  
  return (
    <Layout>
      <Card>
        <Form on submit>
          <Input name="nombre" value={formData.nombre} />
          <Input name="email" disabled />
          <Input name="telefono" />
          <Select name="departamento" />
          <SubmitButton />
        </Form>
      </Card>
    </Layout>
  )
}
```

#### 5.3.2 AccountSecurity Component
**Archivo**: `src/components/account/AccountSecurity.jsx`

**Responsabilidades**:
- [ ] Cambiar contraseña
- [ ] Ver sesiones activas
- [ ] Cerrar otras sesiones (opcional)
- [ ] POST `POST /api/auth/change-password`

**Pseudocódigo**:
```javascript
const AccountSecurity = () => {
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  })
  
  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (passwords.new !== passwords.confirm) {
      showError('Las contraseñas no coinciden')
      return
    }
    try {
      await axios.post('/api/auth/change-password', passwords)
      showSuccess('Contraseña actualizada')
      setPasswords({ current: '', new: '', confirm: '' })
    } catch (error) {
      showError(error.message)
    }
  }
  
  return (
    <Layout>
      <Tabs defaultValue="password">
        <PasswordForm on submit={handleChangePassword} />
        <SessionsList />
      </Tabs>
    </Layout>
  )
}
```

#### 5.3.3 AccountPage Component
**Archivo**: `src/components/account/AccountPage.jsx`

**Responsabilidades**:
- [ ] Wrapper que muestra Profile + Security
- [ ] Tabs o sidebar navigation
- [ ] Redirige a /account
- [ ] Estructura general de página

**Pseudocódigo**:
```javascript
const AccountPage = () => {
  const [activeTab, setActiveTab] = useState('profile')
  
  return (
    <Layout>
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab value="profile">
          <AccountProfile />
        </Tab>
        <Tab value="security">
          <AccountSecurity />
        </Tab>
        <Tab value="notifications" disabled>
          (Future)
        </Tab>
      </Tabs>
    </Layout>
  )
}
```

---

## 📦 Shared Components (Task 5.4)

### 5.4.1 Componentes Reutilizables

**Archivo**: `src/components/shared/Button.jsx`
```javascript
<Button variant="primary|secondary|danger" size="sm|md|lg" disabled={false}>
  Click me
</Button>
```

**Archivo**: `src/components/shared/Input.jsx`
```javascript
<Input label="Nombre" type="text" value={value} onChange={handleChange} error={error} />
```

**Archivo**: `src/components/shared/Card.jsx`
```javascript
<Card title="Título" footer={actions}>
  Contenido
</Card>
```

**Archivo**: `src/components/shared/Badge.jsx`
```javascript
<Badge variant="success|warning|danger">Estado</Badge>
```

**Archivo**: `src/components/shared/Table.jsx`
```javascript
<Table columns={[...]} data={rows} />
```

**Archivo**: `src/components/shared/Modal.jsx`
```javascript
<Modal isOpen={true} onClose={handleClose}>
  Contenido
</Modal>
```

**Archivo**: `src/components/shared/Loading.jsx`
```javascript
<Loading message="Cargando..." />
```

**Archivo**: `src/components/shared/EmptyState.jsx`
```javascript
<EmptyState icon={icon} title="Sin resultados" action={button} />
```

---

## 🔌 API Endpoints Esperados

```bash
# Solicitudes
GET    /api/solicitudes                    → Listar (con paginación, filtros)
GET    /api/solicitudes/:id                → Detalles
POST   /api/solicitudes                    → Crear
PUT    /api/solicitudes/:id                → Editar
DELETE /api/solicitudes/:id                → Eliminar

# Planner
GET    /api/planner                        → Obtener timeline
GET    /api/planner?start=...&end=...      → Por rango de fechas

# Account
GET    /api/auth/profile                   → Obtener perfil
PUT    /api/auth/profile                   → Actualizar perfil
POST   /api/auth/change-password           → Cambiar contraseña
GET    /api/auth/sessions                  → Sesiones activas (opcional)
DELETE /api/auth/sessions/:session_id      → Cerrar sesión (opcional)
```

---

## 🎨 UI/UX Considerations

### Color Scheme (usando Tailwind)
```
Primary:    bg-blue-600
Success:    bg-green-600
Warning:    bg-yellow-600
Danger:     bg-red-600
Neutral:    bg-gray-600

Estados Solicitud:
- Borrador:   gray
- Enviada:    blue
- Proceso:    yellow
- Completada: green
- Rechazada:  red
```

### Spacing Pattern
```
Page:        container mx-auto px-4 py-8
Card:        bg-white rounded-lg shadow p-6
Section:     mb-6 space-y-4
Form:        space-y-4
```

### Icons (Lucide React)
```
Plus:           + (crear)
Edit2:          ✏️ (editar)
Trash2:         🗑️ (eliminar)
Eye:            👁️ (ver)
ChevronLeft:    ◀ (volver)
Filter:         ⊙ (filtrar)
Calendar:       📅 (planner)
User:           👤 (cuenta)
LogOut:         🚪 (logout)
```

---

## 📊 Estimation

| Task | Complexity | Time | Notes |
|------|-----------|------|-------|
| SolicitudList | High | 1h | Tabla + filtros + paginación |
| SolicitudDetail | Medium | 30m | Vista read-only |
| CreateSolicitud | High | 1h | Formulario + validación |
| EditSolicitud | Low | 30m | Reutiliza CreateSolicitud |
| PlannerView | Medium | 45m | Timeline simple |
| AccountProfile | Medium | 45m | Formulario básico |
| AccountSecurity | Medium | 45m | Change password |
| AccountPage | Low | 15m | Wrapper + tabs |
| Shared Components | Medium | 1.5h | 8 componentes básicos |
| **Total** | **-** | **~7h** | Spread en 2-3 sesiones |

---

## ✅ Checklist por Componente

### Cada componente debe tener:
- [ ] Estado (useState)
- [ ] Efectos (useEffect para data fetching)
- [ ] Manejo de errores
- [ ] Loading state
- [ ] Validación
- [ ] Responsividad (Tailwind)
- [ ] Accesibilidad (labels, aria-*)
- [ ] Comments en código complejo

### Antes de marcar como "done":
- [ ] Se ve bien en desktop (1920px)
- [ ] Se ve bien en mobile (375px)
- [ ] No hay errores en console
- [ ] Los datos vienen del backend (no hardcoded)
- [ ] Acciones CRUD funcionan
- [ ] Errores se muestran al usuario
- [ ] Loading states visibles

---

## 🚀 Next Steps After Sprint 2

1. **Sprint 3 - Testing & Polish**:
   - [ ] Integration testing con backend
   - [ ] Error handling mejorado
   - [ ] Toast notifications (React Toastify)
   - [ ] Loading skeletons
   - [ ] Infinite scroll vs pagination

2. **Sprint 4 - Advanced Features**:
   - [ ] File upload para materiales
   - [ ] Search full-text en solicitudes
   - [ ] Filtros avanzados
   - [ ] Export a PDF
   - [ ] Notificaciones push

3. **Sprint 5 - Testing & Deployment**:
   - [ ] Unit tests (Vitest)
   - [ ] E2E tests (Cypress)
   - [ ] Performance optimization
   - [ ] Build production
   - [ ] Deploy a Render/Vercel

---

## 📝 Notas

- **Backend Ready**: Fase 5 completada, seguridad implementada ✅
- **API Contracts**: Asegurar que backend expone exactamente los endpoints listados
- **Error Messages**: Mostrar mensajes de error amigables (no raw API errors)
- **Loading States**: Usar skeleton loaders o spinners
- **Validation**: Client-side (UX rápido) + server-side (seguridad)

