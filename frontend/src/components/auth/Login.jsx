import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authUtils } from '../../utils/auth'
import Logo from '../Logo'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!username.trim() || !password) {
      setError('Please enter both username and password')
      setLoading(false)
      return
    }

    try {
    const result = await authUtils.login(username.trim(), password)
    
    if (result.success) {
        // Small delay to ensure token is saved
        setTimeout(() => {
          navigate('/dashboard', { replace: true })
        }, 100)
    } else {
        setError(result.error || 'Invalid username or password')
        setLoading(false)
    }
    } catch (err) {
      console.error('Login error:', err)
      setError('An unexpected error occurred. Please try again.')
    setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-r from-[#cfd7f1] via-[#f0d7d2] to-[#f7f1f4] flex items-center justify-center" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif' }}>
      <div className="max-w-md w-full mx-auto px-6">
        <div className="bg-white rounded-3xl shadow-xl p-10" style={{ borderRadius: '24px' }}>
          <div className="flex flex-col items-center mb-8">
            <div className="text-black mb-4">
              <Logo />
            </div>
            <h1 className="text-2xl font-semibold text-[#111827]" style={{ fontSize: '28px', fontWeight: 600 }}>
              Welcome back
            </h1>
            <p className="text-sm text-[#4b5563] mt-2" style={{ fontSize: '14px', color: '#4b5563' }}>
              Sign in to your VideoHook account
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
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your username"
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
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your password"
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
              className="w-full bg-[#111827] text-white font-medium py-3 px-6 rounded-lg hover:bg-[#000000] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ fontSize: '16px', fontWeight: 500 }}
            >
              {loading ? 'Signing in...' : 'Log in'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>
              Don't have an account?{' '}
              <Link to="/signup" className="text-[#111827] font-medium hover:underline">
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


