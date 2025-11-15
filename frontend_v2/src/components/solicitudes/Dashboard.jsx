/**
 * Frontend v2 - Dashboard Page
 * Página principal después del login
 */

import { useAuth } from '../../store/authStore'
import { Layout } from '../layout/Layout'

export function Dashboard() {
  const { user } = useAuth()

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md p-6 text-white">
          <h1 className="text-3xl font-bold mb-2">
            ¡Bienvenido, {user?.nombre}!
          </h1>
          <p className="text-blue-100">
            Sistema de Planificación de Materiales v2.0
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Stat Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-blue-600 mb-2">12</div>
            <p className="text-gray-600 text-sm">Solicitudes Pendientes</p>
          </div>

          {/* Stat Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-green-600 mb-2">45</div>
            <p className="text-gray-600 text-sm">Solicitudes Completadas</p>
          </div>

          {/* Stat Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-yellow-600 mb-2">8</div>
            <p className="text-gray-600 text-sm">En Proceso</p>
          </div>

          {/* Stat Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-purple-600 mb-2">156</div>
            <p className="text-gray-600 text-sm">Total de Materiales</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Nueva Solicitud
            </h3>
            <a
              href="/solicitudes/new"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition"
            >
              Crear Solicitud
            </a>
          </div>

          <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Ver Solicitudes
            </h3>
            <a
              href="/solicitudes"
              className="inline-block bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded transition"
            >
              Mi Lista
            </a>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            ℹ️ Información
          </h3>
          <p className="text-blue-800">
            Este es el dashboard de SPM v2.0. Aquí puedes gestionar tus solicitudes,
            ver el estado del planificador y acceder a todas las funciones del sistema.
          </p>
        </div>
      </div>
    </Layout>
  )
}

export default Dashboard
