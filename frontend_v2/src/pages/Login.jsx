import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { fetchCsrfToken } from '../services/csrf'

export default function Login() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError, user } = useAuthStore()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [localError, setLocalError] = useState('')

  useEffect(() => {
    if (user) {
      navigate('/dashboard')
    }
  }, [user, navigate])

  useEffect(() => {
    fetchCsrfToken()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    clearError()

    if (!username.trim() || !password.trim()) {
      setLocalError('Usuario y contraseña son requeridos')
      return
    }

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setLocalError(error || 'Error en el login')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">SPM v2.0</h1>
            <p className="text-gray-600">Sistema de Gestión de Solicitudes</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {(localError || error) && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {localError || error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Usuario
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="admin"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-lg transition"
            >
              {isLoading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center mb-2">Credenciales de Demo:</p>
            <p className="text-xs text-gray-600 text-center">
              <span className="font-semibold">Usuario:</span> admin<br />
              <span className="font-semibold">Contraseña:</span> admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
