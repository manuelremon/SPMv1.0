/**
 * Frontend v2 - Login Component
 * Página de autenticación
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/authStore'
import { fetchCsrfToken } from '../../services/csrf'

export function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const navigate = useNavigate()
  const { login, error, clearError, isAuthenticated } = useAuth()

  // Si ya está autenticado, ir a dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  // Obtener CSRF token en mount
  useEffect(() => {
    const initCsrf = async () => {
      try {
        await fetchCsrfToken()
      } catch (err) {
        console.warn('Failed to fetch CSRF token:', err)
        // Continuar de todas formas
      }
    }

    initCsrf()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')

    if (!username.trim()) {
      setLocalError('Username is required')
      return
    }

    if (!password) {
      setLocalError('Password is required')
      return
    }

    setIsSubmitting(true)

    try {
      await login(username, password)
      // El redirect se hace automáticamente por el useEffect
    } catch (err) {
      // El error ya está en el store, no hacer nada
      setPassword('')
    } finally {
      setIsSubmitting(false)
    }
  }

  const displayError = localError || error

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-8 text-center text-white">
          <h1 className="text-3xl font-bold">SPM</h1>
          <p className="text-blue-100 mt-2">Sistema de Planificación de Materiales</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Error Message */}
          {displayError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-red-700 text-sm">
              {displayError}
            </div>
          )}

          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onFocus={() => clearError()}
              placeholder="Enter your username"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isSubmitting}
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => clearError()}
              placeholder="Enter your password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isSubmitting}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-md transition duration-200 mt-6"
          >
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 text-center text-sm text-gray-600">
          <p>Demo Credentials:</p>
          <p className="text-xs text-gray-500 mt-1">
            Username: <span className="font-mono">admin</span>
          </p>
          <p className="text-xs text-gray-500">
            Password: <span className="font-mono">admin123</span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
