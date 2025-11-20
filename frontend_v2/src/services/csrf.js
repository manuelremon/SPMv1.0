import api from './api'

export const fetchCsrfToken = async () => {
  try {
    const response = await api.get('/auth/csrf')
    const token = response.headers['x-csrf-token'] || response.data.csrf_token
    if (token) {
      localStorage.setItem('csrf_token', token)
    }
    return token
  } catch (error) {
    console.error('CSRF token fetch error:', error)
    throw error
  }
}

export const getCsrfToken = () => {
  return localStorage.getItem('csrf_token')
}

export const clearCsrfToken = () => {
  localStorage.removeItem('csrf_token')
}
