/**
 * Frontend v2 - Main App Component
 * Router y componentes principales
 */

import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/authStore'
import { fetchCsrfToken } from './services/csrf'

// Pages
import { Login } from './components/auth/Login'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Dashboard } from './components/solicitudes/Dashboard'
import { Layout } from './components/layout/Layout'

function AppContent() {
  const { getCurrentUser, isLoading } = useAuth()

  // Inicializar: obtener usuario actual y CSRF token
  useEffect(() => {
    const initApp = async () => {
      try {
        // Intentar obtener usuario actual (si tiene cookies válidas)
        await getCurrentUser()
      } catch (error) {
        console.warn('No authenticated user')
      }

      // Obtener CSRF token para requests
      try {
        await fetchCsrfToken()
      } catch (error) {
        console.warn('Failed to fetch CSRF token')
      }
    }

    initApp()
  }, [getCurrentUser])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Inicializando aplicación...</p>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Login Page */}
      <Route path="/login" element={<Login />} />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Placeholder for future routes */}
      <Route
        path="/solicitudes"
        element={
          <ProtectedRoute>
            <Layout>
              <div className="text-center py-12">
                <h1 className="text-2xl font-bold text-gray-800">
                  Solicitudes (En desarrollo)
                </h1>
              </div>
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/planner"
        element={
          <ProtectedRoute>
            <Layout>
              <div className="text-center py-12">
                <h1 className="text-2xl font-bold text-gray-800">
                  Planner (En desarrollo)
                </h1>
              </div>
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/account"
        element={
          <ProtectedRoute>
            <Layout>
              <div className="text-center py-12">
                <h1 className="text-2xl font-bold text-gray-800">
                  Mi Cuenta (En desarrollo)
                </h1>
              </div>
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Root redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* 404 fallback */}
      <Route
        path="*"
        element={
          <div className="flex items-center justify-center h-screen bg-gray-100">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
              <p className="text-gray-600 mb-6">Página no encontrada</p>
              <a
                href="/dashboard"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded transition"
              >
                Ir al Dashboard
              </a>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
