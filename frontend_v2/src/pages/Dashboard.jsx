import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (err) {
      console.error('Logout error:', err)
      navigate('/login')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">
              Bienvenido, <span className="font-semibold">{user?.nombre || user?.username}</span>
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Stats Cards */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Solicitudes</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="text-blue-600 text-3xl">📋</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">En Proceso</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="text-yellow-600 text-3xl">⏳</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Completadas</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="text-green-600 text-3xl">✅</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Pendientes</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="text-red-600 text-3xl">⚠️</div>
            </div>
          </div>
        </div>

        {/* Welcome Card */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            ¡Bienvenido a SPM v2.0!
          </h2>
          <p className="text-gray-600 mb-4">
            Sistema de Gestión de Solicitudes - Versión 2.0
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-900 text-sm">
              Esta es una aplicación de demostración con autenticación JWT, CSRF protection y seguridad OWASP implementada.
            </p>
          </div>
        </div>

        {/* User Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Información del Usuario</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600 text-sm">ID</p>
              <p className="text-gray-900 font-semibold">{user?.id}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Usuario</p>
              <p className="text-gray-900 font-semibold">{user?.username}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Nombre</p>
              <p className="text-gray-900 font-semibold">{user?.nombre}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Email</p>
              <p className="text-gray-900 font-semibold">{user?.email}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Rol</p>
              <p className="text-gray-900 font-semibold">{user?.rol}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
