import { create } from 'zustand'
import * as authService from '../services/auth'

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authService.login(username, password)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
      return response
    } catch (error) {
      const errorMsg = error.response?.data?.error?.message || error.message
      set({
        error: errorMsg,
        isLoading: false
      })
      throw error
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authService.register(userData)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
      return response
    } catch (error) {
      const errorMsg = error.response?.data?.error?.message || error.message
      set({
        error: errorMsg,
        isLoading: false
      })
      throw error
    }
  },

  getCurrentUser: async () => {
    set({ isLoading: true })
    try {
      const response = await authService.getCurrentUser()
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      })
      return response
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      })
    }
  },

  logout: async () => {
    set({ isLoading: true })
    try {
      await authService.logout()
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      })
    } catch (error) {
      console.error('Logout error:', error)
      // Logout locally even if API fails
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      })
    }
  },

  clearError: () => set({ error: null })
}))
