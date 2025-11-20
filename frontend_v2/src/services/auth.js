import api from './api'

export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password })
  return response.data
}

export const register = async (userData) => {
  const response = await api.post('/auth/register', userData)
  return response.data
}

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/auth/me')
    return response.data
  } catch (error) {
    throw error
  }
}

export const refreshToken = async () => {
  const response = await api.post('/auth/refresh')
  return response.data
}

export const logout = async () => {
  const response = await api.post('/auth/logout')
  return response.data
}
