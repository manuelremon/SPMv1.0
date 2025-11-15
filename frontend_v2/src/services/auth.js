/**
 * Frontend v2 - Auth Service
 * Endpoints de autenticación
 */

import api from './api'

/**
 * Login
 * @param {string} username - Usuario
 * @param {string} password - Contraseña
 * @returns {Promise<{ok, user}>}
 */
export async function login(username, password) {
  const response = await api.post('/auth/login', {
    username,
    password
  })

  return response.data
}

/**
 * Register
 * @param {object} userData - Datos del usuario
 * @returns {Promise<{ok, user}>}
 */
export async function register(userData) {
  const response = await api.post('/auth/register', userData)
  return response.data
}

/**
 * Obtener usuario actual
 * @returns {Promise<{ok, user}>}
 */
export async function getCurrentUser() {
  const response = await api.get('/auth/me')
  return response.data
}

/**
 * Refrescar token (manejado automáticamente por interceptor)
 * Pero exponemos por si se necesita manualmente
 * @returns {Promise<{ok, user}>}
 */
export async function refreshToken() {
  const response = await api.post('/auth/refresh')
  return response.data
}

/**
 * Logout
 * @returns {Promise<{ok, message}>}
 */
export async function logout() {
  const response = await api.post('/auth/logout')
  return response.data
}
