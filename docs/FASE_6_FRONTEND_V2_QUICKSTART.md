# FASE 6: Frontend v2 - Quick Start Guide

## 📋 Qué es la Fase 6

Creación de una **SPA (Single Page Application)** desacoplada con React/Vue que:
- ✅ Funciona con backend_v2 seguro (JWT, CSRF, Rate Limiting)
- ✅ Maneja autenticación + refresh automático
- ✅ Intercepta 401 para re-login
- ✅ Gestiona CSRF tokens
- ✅ Componentes reutilizables y modulares

---

## 🚀 Setup Inicial

### 1. Crear proyecto frontend_v2

```bash
# Opción A: Vite + React (recomendado)
npm create vite@latest frontend_v2 -- --template react
cd frontend_v2

# Opción B: Vite + Vue
npm create vite@latest frontend_v2 -- --template vue
cd frontend_v2
```

### 2. Dependencias necesarias

```bash
npm install
npm install axios react-router-dom zustand  # React
# O: npm install axios vue-router pinia      # Vue

# Para desarrollo
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Estructura recomendada (React)

```
frontend_v2/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Layout.jsx
│   │   ├── solicitudes/
│   │   │   ├── SolicitudList.jsx
│   │   │   ├── SolicitudDetail.jsx
│   │   │   └── CreateSolicitud.jsx
│   │   └── shared/
│   │       ├── Loading.jsx
│   │       ├── Error.jsx
│   │       └── Button.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useApi.js
│   │   └── useCsrf.js
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   └── csrf.js
│   ├── store/
│   │   ├── authStore.js
│   │   └── csrfStore.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── vite.config.js
├── package.json
└── README.md
```

---

## 🔑 Conceptos Clave de Seguridad a Implementar

### 1. HTTP Client con Interceptores

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // ← IMPORTANTE: Enviar cookies automáticamente
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar 401 y refrescar token
api.interceptors.response.use(
  response => response,
  async error => {
    const { response } = error;
    
    // Si es 401 (token expirado)
    if (response?.status === 401) {
      try {
        // Intentar refrescar token
        await api.post('/auth/refresh');
        
        // Reintentar request original
        return api.request(error.config);
      } catch (refreshError) {
        // Refresh falló → hacer logout
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 2. CSRF Token Management

```javascript
// src/services/csrf.js
import api from './api';

let csrfToken = null;

export async function fetchCsrfToken() {
  if (csrfToken) return csrfToken;
  
  try {
    const response = await api.get('/csrf');
    csrfToken = response.data.csrf_token;
    return csrfToken;
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
    throw error;
  }
}

export function getCsrfToken() {
  return csrfToken;
}

// Usado en requests POST/PUT/PATCH/DELETE
export function withCsrfHeader(config) {
  const token = getCsrfToken();
  if (token) {
    config.headers['X-CSRF-Token'] = token;
  }
  return config;
}
```

### 3. Auth Store (Zustand/Pinia)

```javascript
// src/store/authStore.js (Zustand + React)
import create from 'zustand';
import api from '../services/api';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  
  // Login
  login: async (username, password) => {
    const response = await api.post('/auth/login', {
      username,
      password,
    });
    
    set({
      user: response.data.user,
      isAuthenticated: true,
    });
    
    return response.data;
  },
  
  // Logout
  logout: async () => {
    await api.post('/auth/logout');
    set({
      user: null,
      isAuthenticated: false,
    });
  },
  
  // Obtener usuario actual
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      set({
        user: response.data.user,
        isAuthenticated: true,
      });
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
      });
    }
  },
}));
```

### 4. Protected Route Component

```jsx
// src/components/auth/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, user } = useAuthStore();
  
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}
```

---

## 📱 Flujo de Autenticación en Frontend

```javascript
// src/components/auth/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const login = useAuthStore(state => state.login);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await login(username, password);
      // Login exitoso → cookies automáticamente set por backend
      // axios.withCredentials = true → cookies guardadas
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Login failed');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={e => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

---

## 🛠️ Pasos de Implementación

### Paso 1: Setup Base (Día 1)
- [ ] Crear proyecto Vite + React/Vue
- [ ] Instalar dependencias (axios, router, store)
- [ ] Configurar estructura de carpetas
- [ ] Setup Tailwind CSS

### Paso 2: Servicios de Seguridad (Día 2)
- [ ] Crear `api.js` con axios + interceptores
- [ ] Implementar `csrf.js` para CSRF token management
- [ ] Crear `auth.js` para endpoints de autenticación
- [ ] Tests de interceptores

### Paso 3: Autenticación (Día 3)
- [ ] Crear auth store (Zustand/Pinia)
- [ ] Componente Login
- [ ] Componente Register
- [ ] ProtectedRoute wrapper

### Paso 4: Componentes Principales (Día 4-5)
- [ ] Layout base (Header, Sidebar, Footer)
- [ ] Dashboard
- [ ] Solicitudes (list, detail, create)
- [ ] Mi Cuenta (perfil, settings)

### Paso 5: Testing (Día 6)
- [ ] Tests de auth flow
- [ ] Tests de CSRF
- [ ] Tests de refresh token
- [ ] E2E tests

### Paso 6: Polish (Día 7)
- [ ] Error handling mejorado
- [ ] Loading states
- [ ] Toast notifications
- [ ] Responsive design

---

## ✅ Checklist de Integración con Backend

- [ ] **CORS**: Backend permite requests desde `http://localhost:5173` (Vite default)
- [ ] **Cookies**: `withCredentials: true` en axios
- [ ] **CSRF**: Obtener token en `GET /api/csrf` antes de POST/PUT/PATCH
- [ ] **JWT**: Almacenado en httpOnly cookies (no localStorage)
- [ ] **Refresh**: Interceptor maneja 401 automáticamente
- [ ] **Rate Limit**: Mostrar error amigable en 429
- [ ] **Session**: Recuperar usuario en app init con `GET /api/auth/me`

---

## 🔗 Endpoints a Usar

```javascript
// Autenticación
POST   /api/auth/login       → {username, password} → {user, cookies}
POST   /api/auth/register    → {username, password, ...} → {user}
GET    /api/auth/me          → {} → {user}
POST   /api/auth/refresh     → {} → {user, new_access_token}
POST   /api/auth/logout      → {} → {message}

// Seguridad
GET    /api/csrf             → {} → {csrf_token}

// Data
GET    /api/solicitudes      → {filters} → {items}
POST   /api/solicitudes      → {data, csrf_token} → {created}
GET    /api/solicitudes/:id  → {} → {item}
PUT    /api/solicitudes/:id  → {data, csrf_token} → {updated}
DELETE /api/solicitudes/:id  → {csrf_token} → {deleted}

// Planner
GET    /api/planner/...      → {...}
POST   /api/planner/...      → {...}

// Health
GET    /api/health           → {status}
```

---

## 🧪 Testing Local

```bash
# Terminal 1: Backend
cd backend_v2
python -m pip install -r ../requirements.txt
python app.py

# Terminal 2: Frontend
cd frontend_v2
npm run dev

# Acceder a: http://localhost:5173
# Backend en: http://localhost:5000
```

---

## 🐛 Debugging Tips

### 1. Verificar cookies
```javascript
// En console del navegador
console.log(document.cookie);

// Debe mostrar:
// spm_token=...
// spm_token_refresh=...
```

### 2. Ver headers en Network tab
- Headers enviados:
  - `Authorization: Bearer ...` (si lo usas)
  - `X-CSRF-Token: ...` (en POST/PUT/PATCH)
  - `Cookie: spm_token=...` (automático)

### 3. Test CSRF manualmente
```javascript
// Obtener token
const csrfResp = await fetch('http://localhost:5000/api/csrf');
const { csrf_token } = await csrfResp.json();

// Usar en request
fetch('http://localhost:5000/api/solicitudes', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token
  },
  body: JSON.stringify({...})
});
```

---

## 📚 Referencias y Recursos

- [Vite Guide](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [Zustand Store](https://github.com/pmndrs/zustand)
- [Axios Docs](https://axios-http.com/)
- [OWASP - CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)

---

## 🎯 Siguiente Paso

Una vez completada FASE 6, proceder con:

**FASE 7: PostgreSQL**
- Migración SQLite → PostgreSQL
- Mantener backward compatibility

---

**Estado**: Ready para iniciar  
**Estimated Duration**: 1 semana  
**Complexity**: Media

¿Listo para comenzar Fase 6? 🚀

