import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

let isRefreshing = false
let failedQueue = []

const onRefreshed = (resolve, reject) => {
  failedQueue.push({ resolve, reject })
}

const processQueue = (error) => {
  failedQueue.forEach(promise => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve()
    }
  })
  failedQueue = []
}

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add CSRF token
api.interceptors.request.use((config) => {
  const csrfToken = localStorage.getItem('csrf_token')
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})

// Response interceptor - handle 401
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          onRefreshed(resolve, reject)
        })
        .then(() => api(originalRequest))
        .catch(err => {
          window.location.href = '/login'
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await axios.post(`${API_BASE_URL.replace('/api', '')}/api/auth/refresh`, {}, {
          withCredentials: true
        })
        processQueue(null)
        return api(originalRequest)
      } catch (err) {
        processQueue(err)
        window.location.href = '/login'
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
