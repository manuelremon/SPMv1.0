/**
 * Frontend v2 - ProtectedRoute Component
 * Wrapper para proteger rutas que requieren autenticación
 */

import { Navigate } from 'react-router-dom'
import { useAuth } from '../../store/authStore'

/**
 * ProtectedRoute Component
 * Redirige a /login si no está autenticado
 */
export function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
