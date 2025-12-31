// Backend API authentication

import { api } from './api'

export const authUtils = {
  // Sign up a new user
  async signup(username, email, password) {
    try {
      const response = await api.post('/api/auth/signup', {
        username,
        email: email.toLowerCase().trim(),
        password
      })
      
      // Store token and user info in localStorage (new signups default to remember me)
      localStorage.setItem('videohook_token', response.data.access_token)
      localStorage.setItem('videohook_current_user', JSON.stringify(response.data.user))
      localStorage.setItem('videohook_remember_me', 'true')
      
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
        const fullUrl = error.config?.baseURL 
          ? (error.config.baseURL.endsWith('/') ? error.config.baseURL.slice(0, -1) : error.config.baseURL) + 
            (error.config.url.startsWith('/') ? error.config.url : '/' + error.config.url)
          : error.config?.url
        console.error('Full URL:', fullUrl)
        errorMessage = `Unable to connect to server at ${fullUrl || 'backend URL'}. Please check if the backend is running and VITE_API_URL is set correctly.`
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
  async login(email, password, rememberMe = false) {
    try {
      const response = await api.post('/api/auth/login', {
        email: email.toLowerCase().trim(),
        password
      })
      
      // Choose storage based on remember me preference
      const storage = rememberMe ? localStorage : sessionStorage
      
      // Store token and user info in appropriate storage
      storage.setItem('videohook_token', response.data.access_token)
      storage.setItem('videohook_current_user', JSON.stringify(response.data.user))
      
      // Also store remember me preference in localStorage (for checking on page load)
      if (rememberMe) {
        localStorage.setItem('videohook_remember_me', 'true')
      } else {
        localStorage.removeItem('videohook_remember_me')
      }
      
      return { success: true, user: response.data.user }
    } catch (error) {
      console.error('Login error:', error)
      let errorMessage = 'Invalid email or password'
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage
        if (error.response.status === 401) {
          errorMessage = 'Invalid email or password'
        } else if (error.response.status === 500) {
          errorMessage = 'Server error. Please try again later.'
        }
      } else if (error.request) {
        // Request was made but no response received
        const fullUrl = error.config?.baseURL 
          ? (error.config.baseURL.endsWith('/') ? error.config.baseURL.slice(0, -1) : error.config.baseURL) + 
            (error.config.url.startsWith('/') ? error.config.url : '/' + error.config.url)
          : error.config?.url || 'backend'
        console.error('Connection error - Full URL attempted:', fullUrl)
        errorMessage = `Unable to connect to server at ${fullUrl}. Please check if the backend is running and VITE_API_URL is set correctly in your environment.`
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

  // Get current user from localStorage or sessionStorage
  getCurrentUser() {
    try {
      // Check if remember me is enabled
      const rememberMe = localStorage.getItem('videohook_remember_me') === 'true'
      const storage = rememberMe ? localStorage : sessionStorage
      
      const user = storage.getItem('videohook_current_user')
      return user ? JSON.parse(user) : null
    } catch (error) {
      return null
    }
  },

  // Get current user from API (refresh)
  async getCurrentUserFromAPI() {
    try {
      const response = await api.get('/api/auth/me')
      const rememberMe = localStorage.getItem('videohook_remember_me') === 'true'
      const storage = rememberMe ? localStorage : sessionStorage
      storage.setItem('videohook_current_user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      return null
    }
  },

  // Logout user
  logout() {
    // Clear both localStorage and sessionStorage to be safe
    localStorage.removeItem('videohook_token')
    localStorage.removeItem('videohook_current_user')
    localStorage.removeItem('videohook_remember_me')
    sessionStorage.removeItem('videohook_token')
    sessionStorage.removeItem('videohook_current_user')
  },

  // Check if user is authenticated
  isAuthenticated() {
    const rememberMe = localStorage.getItem('videohook_remember_me') === 'true'
    const storage = rememberMe ? localStorage : sessionStorage
    const token = storage.getItem('videohook_token')
    const user = this.getCurrentUser()
    return !!(token && user)
  },

  // Get auth token
  getToken() {
    const rememberMe = localStorage.getItem('videohook_remember_me') === 'true'
    const storage = rememberMe ? localStorage : sessionStorage
    return storage.getItem('videohook_token')
  }
}


