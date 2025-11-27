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

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    // Sign up
    try {
      const result = await authUtils.signup(username.trim(), email.trim(), password)
      
      if (result.success) {
        navigate('/dashboard')
      } else {
        setError(result.error || 'Failed to create account. Please try again.')
      }
    } catch (err) {
      console.error('Signup error:', err)
      setError('An unexpected error occurred. Please try again.')
    } finally {
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
              Create your account
            </h1>
            <p className="text-sm text-[#4b5563] mt-2" style={{ fontSize: '14px', color: '#4b5563' }}>
              Sign up to get started with VideoHook
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
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent"
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
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent"
                style={{ fontSize: '16px' }}
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2" style={{ fontSize: '14px', fontWeight: 500 }}>
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent"
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
              className="w-full bg-[#111827] text-white font-medium py-3 px-6 rounded-lg hover:bg-[#000000] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ fontSize: '16px', fontWeight: 500 }}
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>
              Already have an account?{' '}
              <Link to="/login" className="text-[#111827] font-medium hover:underline">
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


