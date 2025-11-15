/**
 * Frontend v2 - Layout Component
 * Layout principal para páginas autenticadas
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/authStore'
import { Menu, LogOut, User } from 'lucide-react'

export function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login', { replace: true })
    } catch (error) {
      console.error('Logout error:', error)
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-900 text-white transition-all duration-300 ease-in-out`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 bg-gray-800">
          {sidebarOpen && <h1 className="text-xl font-bold">SPM</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <Menu size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-8 space-y-4 px-4">
          <a
            href="/dashboard"
            className="flex items-center space-x-3 p-2 rounded hover:bg-gray-800 transition"
          >
            <span className="text-xl">📊</span>
            {sidebarOpen && <span>Dashboard</span>}
          </a>

          <a
            href="/solicitudes"
            className="flex items-center space-x-3 p-2 rounded hover:bg-gray-800 transition"
          >
            <span className="text-xl">📋</span>
            {sidebarOpen && <span>Solicitudes</span>}
          </a>

          <a
            href="/planner"
            className="flex items-center space-x-3 p-2 rounded hover:bg-gray-800 transition"
          >
            <span className="text-xl">📅</span>
            {sidebarOpen && <span>Planner</span>}
          </a>

          <a
            href="/account"
            className="flex items-center space-x-3 p-2 rounded hover:bg-gray-800 transition"
          >
            <User size={20} />
            {sidebarOpen && <span>Mi Cuenta</span>}
          </a>
        </nav>

        {/* User Info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
          {user && sidebarOpen && (
            <div className="text-sm mb-3">
              <p className="font-medium">{user.username}</p>
              <p className="text-gray-400">{user.role}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-700 rounded py-2 transition"
          >
            <LogOut size={18} />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-800">
            {user?.nombre} {user?.apellido}
          </h2>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
