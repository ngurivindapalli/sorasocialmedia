import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authUtils } from '../../utils/auth'
import Logo from '../Logo'

function Signup() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Validation
    if (!username.trim()) {
      setError('Username is required')
      setLoading(false)
      return
    }

    if (!email.trim() || !email.includes('@')) {
      setError('Valid email is required')
      setLoading(false)
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    // Check password byte length (bcrypt limit is 72 bytes)
    const passwordBytes = new TextEncoder().encode(password)
    if (passwordBytes.length > 72) {
      setError('Password is too long. Maximum length is 72 characters. Please use a shorter password.')
      setLoading(false)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    // Sign up using authUtils
    try {
      const result = await authUtils.signup(username.trim(), email.trim(), password)
      
      if (result.success) {
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
          : (result.error?.message || JSON.stringify(result.error) || 'Failed to create account')
        setError(errorMessage)
        setLoading(false)
      }
    } catch (err) {
      console.error('Signup error:', err)
      
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
              Create your account
            </h1>
            <p className="text-sm text-[#4b5563] mt-2" style={{ fontSize: '14px', color: '#4b5563' }}>
              Sign up to get started with Aigis Marketing
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2" style={{ fontSize: '14px', fontWeight: 500 }}>
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your username"
                disabled={loading}
              />
            </div>

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
                placeholder="Enter your password (6-72 characters)"
                disabled={loading}
                maxLength={72}
              />
              <p className="mt-1 text-xs text-[#4b5563]">
                Must be between 6 and 72 characters
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2" style={{ fontSize: '14px', fontWeight: 500 }}>
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Confirm your password"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#1e293b] text-white font-medium py-3 px-6 rounded-lg hover:bg-[#334155] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ fontSize: '16px', fontWeight: 500 }}
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>
              Already have an account?{' '}
              <Link to="/login" className="text-[#1e293b] font-medium hover:underline">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Signup


