import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import Loading from './Loading'

export default function ProtectedRoute({ children }) {
  const { user, isLoading, isAuthenticated } = useAuthStore()

  if (isLoading) {
    return <Loading />
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  return children
}
