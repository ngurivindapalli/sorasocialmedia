// Backend API authentication

import { api } from './api'

export const authUtils = {
  // Sign up a new user
  async signup(username, email, password) {
    try {
      const response = await api.post('/api/auth/signup', {
        username,
        email,
        password
      })
      
      // Store token and user info
      localStorage.setItem('videohook_token', response.data.access_token)
      localStorage.setItem('videohook_current_user', JSON.stringify(response.data.user))
      
      return { success: true, user: response.data.user }
    } catch (error) {
      console.error('Signup error:', error)
      console.error('Error details:', {
        hasResponse: !!error.response,
        hasRequest: !!error.request,
        status: error.response?.status,
        message: error.message,
        code: error.code
      })
      
      let errorMessage = 'Failed to create account'
      
      if (error.response) {
        // Server responded with error
        const detail = error.response.data?.detail || error.response.data?.message
        errorMessage = detail || errorMessage
        
        if (error.response.status === 400) {
          // Bad request - validation error
          if (detail) {
            errorMessage = detail
          }
        } else if (error.response.status === 500) {
          errorMessage = detail || 'Server error occurred. Please check backend logs or try again later.'
        } else if (error.response.status === 409) {
          errorMessage = 'Username or email already exists. Please use different credentials.'
        }
      } else if (error.request && !error.response) {
        // Request was made but no response received - connection issue
        console.error('Connection error - request made but no response')
        console.error('Request URL:', error.config?.url)
        console.error('Base URL:', error.config?.baseURL)
        console.error('Full URL:', error.config?.baseURL + error.config?.url)
        errorMessage = 'Unable to connect to server. Please check if the backend is running on http://localhost:8000'
      } else if (error.message) {
        // Network or other error
        if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
          errorMessage = 'Network error. Please check if the backend is running on http://localhost:8000'
        } else if (error.code === 'ECONNREFUSED') {
          errorMessage = 'Connection refused. Please check if the backend is running on http://localhost:8000'
        } else {
          errorMessage = error.message || errorMessage
        }
      }
      
      return {
        success: false,
        error: errorMessage
      }
    }
  },

  // Login user
  async login(username, password) {
    try {
      const response = await api.post('/api/auth/login', {
        username,
        password
      })
      
      // Store token and user info
      localStorage.setItem('videohook_token', response.data.access_token)
      localStorage.setItem('videohook_current_user', JSON.stringify(response.data.user))
      
      return { success: true, user: response.data.user }
    } catch (error) {
      console.error('Login error:', error)
      let errorMessage = 'Invalid username or password'
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage
        if (error.response.status === 401) {
          errorMessage = 'Invalid username or password'
        } else if (error.response.status === 500) {
          errorMessage = 'Server error. Please try again later.'
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Unable to connect to server. Please check if the backend is running.'
      } else {
        // Something else happened
        errorMessage = error.message || errorMessage
      }
      
      return {
        success: false,
        error: errorMessage
      }
    }
  },

  // Get current user from localStorage or API
  getCurrentUser() {
    try {
      const user = localStorage.getItem('videohook_current_user')
      return user ? JSON.parse(user) : null
    } catch (error) {
      return null
    }
  },

  // Get current user from API (refresh)
  async getCurrentUserFromAPI() {
    try {
      const response = await api.get('/api/auth/me')
      localStorage.setItem('videohook_current_user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      return null
    }
  },

  // Logout user
  logout() {
    localStorage.removeItem('videohook_token')
    localStorage.removeItem('videohook_current_user')
  },

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('videohook_token')
    const user = this.getCurrentUser()
    return !!(token && user)
  },

  // Get auth token
  getToken() {
    return localStorage.getItem('videohook_token')
  }
}


