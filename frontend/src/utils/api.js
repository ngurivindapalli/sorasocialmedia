import axios from 'axios'

// API base URL
// In development, use Vite proxy to avoid CORS issues
// The proxy in vite.config.js will forward /api requests to http://localhost:8000
// In production, use the full URL from environment variable
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://sorasocialmedia-1.onrender.com')

console.log('[API] Mode:', import.meta.env.MODE, 'API_URL:', API_URL || '(using Vite proxy)')
if (!API_URL && !import.meta.env.DEV) {
  console.error('[API] WARNING: VITE_API_URL not set in production! API calls may fail.')
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout (increased for document uploads and context summaries)
})

// Add request logging in development
api.interceptors.request.use(
  (config) => {
    // If data is FormData, remove Content-Type header so axios can set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
      if (import.meta.env.DEV) {
        console.log('[API] FormData detected - Content-Type header removed for multipart/form-data')
      }
    }
    
    // Construct full URL for logging
    const fullUrl = config.baseURL 
      ? (config.baseURL.endsWith('/') ? config.baseURL.slice(0, -1) : config.baseURL) + 
        (config.url.startsWith('/') ? config.url : '/' + config.url)
      : config.url
    if (import.meta.env.DEV) {
      console.log('[API] Request:', config.method?.toUpperCase(), config.url, '-> Full URL:', fullUrl)
      console.log('[API] Base URL:', config.baseURL || '(relative - using Vite proxy)')
      if (config.data instanceof FormData) {
        console.log('[API] FormData fields:', Array.from(config.data.keys()))
      }
    }
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log('[API] Response:', response.status, response.config.url)
    }
    return response
  },
  (error) => {
    // Log more detailed error information
    if (error.response) {
      console.error('[API] Response error:', error.response.status, error.response.statusText, error.config?.url)
      console.error('[API] Response data:', error.response.data)
    } else if (error.request) {
      console.error('[API] No response received:', error.message, error.code, error.config?.url)
      console.error('[API] Request was made but no response received - backend may be down or unreachable')
    } else {
      console.error('[API] Request setup error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Add auth token to requests (only if token exists - authentication is optional)
api.interceptors.request.use(
  (config) => {
    // Check both localStorage and sessionStorage for token
    const rememberMe = localStorage.getItem('videohook_remember_me') === 'true'
    const storage = rememberMe ? localStorage : sessionStorage
    const token = storage.getItem('videohook_token') || localStorage.getItem('videohook_token') || sessionStorage.getItem('videohook_token')
    // Only add Authorization header if token exists - don't require auth
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Don't add empty Authorization header - let requests work without auth
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors - no redirects needed since authentication is optional
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect on 401 errors - authentication is optional now
    // Just clear any invalid tokens silently from both storage locations
    if (error.response?.status === 401) {
      localStorage.removeItem('videohook_token')
      localStorage.removeItem('videohook_current_user')
      localStorage.removeItem('videohook_remember_me')
      sessionStorage.removeItem('videohook_token')
      sessionStorage.removeItem('videohook_current_user')
    }
    return Promise.reject(error)
  }
)

export { api, API_URL }


