/**
 * Frontend v2 - Auth Store (Zustand)
 * Gestiona estado global de autenticación
 */

import { create } from 'zustand'
import * as authService from '../services/auth'
import { fetchCsrfToken, clearCsrfToken } from '../services/csrf'

/**
 * Auth Store con Zustand
 */
export const useAuthStore = create((set, get) => ({
    // Estado
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    /**
     * Login
     */
    login: async (username, password) => {
      set({ isLoading: true, error: null })

      try {
        const data = await authService.login(username, password)

        set({
          user: data.user,
          isAuthenticated: true,
          isLoading: false
        })

        return data
      } catch (error) {
        const errorMsg = error.response?.data?.error?.message || 'Login failed'
        set({ error: errorMsg, isLoading: false })
        throw error
      }
    },

    /**
     * Register
     */
    register: async (userData) => {
      set({ isLoading: true, error: null })

      try {
        const data = await authService.register(userData)

        set({
          user: data.user,
          isAuthenticated: true,
          isLoading: false
        })

        return data
      } catch (error) {
        const errorMsg = error.response?.data?.error?.message || 'Register failed'
        set({ error: errorMsg, isLoading: false })
        throw error
      }
    },

    /**
     * Obtener usuario actual (en app init)
     */
    getCurrentUser: async () => {
      set({ isLoading: true })

      try {
        const data = await authService.getCurrentUser()

        set({
          user: data.user,
          isAuthenticated: true,
          isLoading: false
        })

        return data
      } catch (error) {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false
        })

        throw error
      }
    },

    /**
     * Logout
     */
    logout: async () => {
      set({ isLoading: true })

      try {
        await authService.logout()

        // Limpiar estado
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        })

        // Limpiar CSRF token
        clearCsrfToken()
      } catch (error) {
        // Logout de todas formas
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false
        })

        clearCsrfToken()
        throw error
      }
    },

    /**
     * Limpiar error
     */
    clearError: () => set({ error: null }),

    /**
     * Setear error manual
     */
    setError: (error) => set({ error })
  })
)

/**
 * Hook para usar el auth store
 */
export const useAuth = () => useAuthStore()
