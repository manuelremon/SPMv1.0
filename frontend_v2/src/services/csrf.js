/**
 * Frontend v2 - CSRF Service
 * Gestiona obtención y almacenamiento de tokens CSRF
 */

import api from './api'

/**
 * Obtener token CSRF del backend
 * Llamar una vez en app init
 */
export async function fetchCsrfToken() {
  try {
    const response = await api.get('/csrf')
    const { csrf_token } = response.data

    // Guardar en localStorage para usarlo en requests
    localStorage.setItem('csrf_token', csrf_token)

    return csrf_token
  } catch (error) {
    console.error('Error fetching CSRF token:', error)
    throw error
  }
}

/**
 * Obtener CSRF token desde localStorage
 */
export function getCsrfToken() {
  return localStorage.getItem('csrf_token')
}

/**
 * Limpiar CSRF token (en logout)
 */
export function clearCsrfToken() {
  localStorage.removeItem('csrf_token')
}
