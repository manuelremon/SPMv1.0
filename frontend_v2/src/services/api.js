/**
 * Frontend v2 - API Client
 * Axios instance con interceptores para:
 * - Incluir cookies automáticamente
 * - Manejar 401 y refrescar token
 * - Agregar CSRF token en requests POST/PUT/PATCH/DELETE
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

/**
 * Crear instancia de Axios
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // ← CRÍTICO: Enviar cookies automáticamente
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Variables globales para controlar refresh
 */
let isRefreshing = false
let refreshSubscribers = []

/**
 * Suscribirse a fin de refresh
 */
const onRefreshed = (cb) => {
  refreshSubscribers.push(cb)
}

/**
 * Notificar a todos los suscriptores
 */
const notifyRefreshSubscribers = () => {
  refreshSubscribers.forEach(cb => cb())
  refreshSubscribers = []
}

/**
 * Interceptor de RESPUESTA:
 * Maneja 401 (token expirado) y reintenta automáticamente
 */
api.interceptors.response.use(
  response => response,
  async error => {
    const { response, config } = error

    // Si no es 401, retornar el error
    if (response?.status !== 401) {
      return Promise.reject(error)
    }

    // Si ya estamos refrescando, esperar
    if (isRefreshing) {
      return new Promise((resolve) => {
        onRefreshed(() => {
          resolve(api(config))
        })
      })
    }

    // Marcar que estamos refrescando
    isRefreshing = true

    try {
      // Intentar refrescar el token
      const refreshResponse = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        {},
        {
          withCredentials: true // ← Incluir cookies para refresh token
        }
      )

      // Refrescado exitosamente
      isRefreshing = false
      notifyRefreshSubscribers()

      // Reintentar request original
      return api(config)
    } catch (refreshError) {
      // Refresh falló → logout
      isRefreshing = false
      refreshSubscribers = []

      // Redirigir a login (será manejado por el store)
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }

      return Promise.reject(refreshError)
    }
  }
)

/**
 * Interceptor de REQUEST:
 * Agrega CSRF token en métodos que modifican datos
 */
api.interceptors.request.use(
  config => {
    // Agregar CSRF token si existe en localStorage
    const csrfToken = localStorage.getItem('csrf_token')
    if (csrfToken && ['post', 'put', 'patch', 'delete'].includes(config.method)) {
      config.headers['X-CSRF-Token'] = csrfToken
    }

    return config
  },
  error => Promise.reject(error)
)

export default api
