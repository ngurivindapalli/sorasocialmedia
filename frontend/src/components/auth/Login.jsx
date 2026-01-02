import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authUtils } from '../../utils/auth'
import Logo from '../Logo'
import { Loader2, AlertCircle } from 'lucide-react'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [backendStatus, setBackendStatus] = useState('checking') // 'checking' | 'online' | 'offline'
  const navigate = useNavigate()

  // Load saved email if remember me was previously enabled
  useEffect(() => {
    const savedEmail = localStorage.getItem('videohook_saved_email')
    const wasRemembered = localStorage.getItem('videohook_remember_me') === 'true'
    if (savedEmail && wasRemembered) {
      setEmail(savedEmail)
      setRememberMe(true)
    }
  }, [])

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const { api } = await import('../../utils/api')
        const response = await api.get('/api/health', { timeout: 10000 })
        if (response.data?.status === 'healthy') {
          setBackendStatus('online')
        } else {
          setBackendStatus('offline')
        }
      } catch (err) {
        console.warn('[Login] Backend health check failed:', err)
        setBackendStatus('offline')
      }
    }
    checkBackendHealth()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!email.trim() || !password) {
      setError('Please enter both email and password')
      setLoading(false)
      return
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address')
      setLoading(false)
      return
    }

    try {
    const result = await authUtils.login(email.trim(), password, rememberMe)
    
    if (result.success) {
        // Save email if remember me is checked
        if (rememberMe) {
          localStorage.setItem('videohook_saved_email', email.trim())
          localStorage.setItem('videohook_remember_me', 'true')
        } else {
          localStorage.removeItem('videohook_saved_email')
          localStorage.removeItem('videohook_remember_me')
        }
        
        // Small delay to ensure token is saved
        setTimeout(() => {
          // Navigate back to marketing post if that's where they came from
          const from = new URLSearchParams(window.location.search).get('from') || '/dashboard'
          navigate(from, { replace: true })
        }, 100)
    } else {
        // Ensure error is a string
        const errorMessage = typeof result.error === 'string' 
          ? result.error 
          : (result.error?.message || JSON.stringify(result.error) || 'Invalid email or password')
        setError(errorMessage)
        setLoading(false)
    }
    } catch (err) {
      console.error('Login error:', err)
      
      // Extract error message properly
      let errorMessage = 'An unexpected error occurred. Please try again.'
      
      if (err.response?.data) {
        const errorData = err.response.data
        
        // Handle Pydantic validation errors (array of errors)
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
        }
        // Handle string error messages
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        }
        // Handle object error messages
        else if (errorData.detail && typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.msg || errorData.detail.message || 'Validation error occurred'
        }
        // Fallback to message field
        else if (errorData.message) {
          errorMessage = errorData.message
        }
      } else if (err.request && !err.response) {
        // Network/connection error - likely Render cold start
        if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          errorMessage = 'Backend is starting up (this may take 30-60 seconds on free tier). Please wait a moment and try again.'
        } else {
          errorMessage = 'Unable to connect to server. The backend may be starting up. Please wait a moment and try again.'
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center" style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif" }}>
      <div className="max-w-md w-full mx-auto px-6">
        <div className="bg-white rounded-3xl shadow-xl p-10 border border-[#e5e7eb]" style={{ borderRadius: '24px' }}>
          <div className="flex flex-col items-center mb-8">
            <div className="text-black mb-4">
              <Logo />
            </div>
            <h1 className="text-2xl font-semibold text-[#111827]" style={{ fontSize: '28px', fontWeight: 600 }}>
              Welcome back
            </h1>
            <p className="text-sm text-[#4b5563] mt-2" style={{ fontSize: '14px', color: '#4b5563' }}>
              Sign in to your Aigis Marketing account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2" style={{ fontSize: '14px', fontWeight: 500 }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your email"
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2" style={{ fontSize: '14px', fontWeight: 500 }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your password"
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 text-[#1e293b] border-[#e5e7eb] rounded focus:ring-2 focus:ring-[#1e293b]"
                disabled={loading}
              />
              <label htmlFor="rememberMe" className="ml-2 text-sm text-[#4b5563]" style={{ fontSize: '14px', cursor: 'pointer' }}>
                Remember me
              </label>
            </div>

            {backendStatus === 'checking' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <p className="text-blue-800 text-sm">Checking backend connection...</p>
              </div>
            )}
            {backendStatus === 'offline' && !error && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-center gap-3">
                <AlertCircle className="w-4 h-4 text-yellow-600" />
                <p className="text-yellow-800 text-sm">Backend may be starting up. This can take 30-60 seconds on free tier. Please try again in a moment.</p>
              </div>
            )}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#1e293b] text-white font-medium py-3 px-6 rounded-lg hover:bg-[#334155] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ fontSize: '16px', fontWeight: 500 }}
            >
              {loading ? 'Signing in...' : 'Log in'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>
              Don't have an account?{' '}
              <Link to="/signup" className="text-[#1e293b] font-medium hover:underline">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login


