import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { fetchCsrfToken } from './services/csrf'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'
import Loading from './components/Loading'

function App() {
  const { user, isLoading, getCurrentUser } = useAuthStore()
  const [appLoading, setAppLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      try {
        // Obtener usuario actual
        await getCurrentUser()
        // Obtener CSRF token
        await fetchCsrfToken()
      } catch (err) {
        console.error('App init error:', err)
      } finally {
        setAppLoading(false)
      }
    }

    init()
  }, [])

  if (appLoading || isLoading) {
    return <Loading />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
