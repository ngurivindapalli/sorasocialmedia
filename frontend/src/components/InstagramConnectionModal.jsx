import { useState } from 'react'
import { X, Instagram, Link2, Loader2, AlertCircle, Info } from 'lucide-react'
import { api } from '../utils/api'

function InstagramConnectionModal({ isOpen, onClose, onSuccess }) {
  const [connectionMethod, setConnectionMethod] = useState('oauth') // 'oauth' or 'manual'
  const [manualForm, setManualForm] = useState({
    username: '',
    access_token: '',
    account_id: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleManualSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate form
      if (!manualForm.username.trim() || !manualForm.access_token.trim()) {
        setError('Username and Access Token are required')
        setLoading(false)
        return
      }

      console.log('[Instagram Modal] Submitting manual connection:', {
        username: manualForm.username,
        has_token: !!manualForm.access_token,
        account_id: manualForm.account_id
      })

      // Call API to save connection manually
      const response = await api.post('/api/connections/instagram/manual', {
        username: manualForm.username.trim(),
        access_token: manualForm.access_token.trim(),
        account_id: manualForm.account_id.trim() || null
      })

      console.log('[Instagram Modal] Connection saved:', response.data)

      // Reset form
      setManualForm({ username: '', access_token: '', account_id: '' })
      
      // Notify parent and close
      if (onSuccess) {
        onSuccess(response.data)
      }
      onClose()
    } catch (err) {
      console.error('[Instagram Modal] Error saving connection:', err)
      let errorMessage = 'Failed to save Instagram connection'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.response?.status === 400) {
        errorMessage = 'Invalid connection information. Please check your credentials.'
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.'
      } else if (err.request && !err.response) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running.'
      }

      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleOAuth = async () => {
    setError('')
    setLoading(true)

    try {
      console.log('[Instagram Modal] Starting OAuth flow...')
      console.log('[Instagram Modal] API base URL:', api.defaults.baseURL || '(using proxy)')
      
      // Get OAuth authorization URL
      const response = await api.get('/api/oauth/instagram/authorize')
      
      console.log('[Instagram Modal] OAuth response received:', response.status)
      console.log('[Instagram Modal] Response data:', response.data)
      
      if (response.data?.authorization_url) {
        const authUrl = response.data.authorization_url
        console.log('[Instagram Modal] Got authorization URL:', authUrl)
        console.log('[Instagram Modal] Redirecting NOW to:', authUrl)
        
        // Direct redirect - this should work immediately
        // Use replace to avoid back button issues
        window.location.replace(authUrl)
        
        // Also set href as backup (but replace is executed first)
        window.location.href = authUrl
      } else {
        console.error('[Instagram Modal] No authorization_url in response:', response.data)
        throw new Error('No authorization URL received from server. Response: ' + JSON.stringify(response.data))
      }
    } catch (err) {
      console.error('[Instagram Modal] OAuth error:', err)
      console.error('[Instagram Modal] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText,
        request: err.request ? 'Request made but no response' : 'No request made'
      })
      
      let errorMessage = 'Failed to start OAuth flow'
      
      if (err.response?.status === 401 || err.response?.status === 403) {
        // This shouldn't happen since auth is not required, but handle it
        errorMessage = 'OAuth endpoint requires configuration. Please check backend settings.'
      } else if (err.response?.status === 400) {
        errorMessage = err.response?.data?.detail || 'Instagram OAuth not configured. Please set INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET in your backend .env file'
      } else if (err.response?.status === 500) {
        errorMessage = err.response?.data?.detail || 'Server error. Please check backend logs.'
      } else if (err.request && !err.response) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running on http://localhost:8000'
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }

      console.log('[Instagram Modal] Setting error message:', errorMessage)
      setError(errorMessage)
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center">
              <Instagram className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Connect Instagram</h2>
              <p className="text-sm text-gray-500">Choose your connection method</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Connection Method Tabs */}
          <div className="flex gap-2 mb-6 border-b border-gray-200">
            <button
              type="button"
              onClick={() => {
                setConnectionMethod('oauth')
                setError('')
              }}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                connectionMethod === 'oauth'
                  ? 'text-pink-600 border-b-2 border-pink-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              OAuth (Recommended)
            </button>
            <button
              type="button"
              onClick={() => {
                setConnectionMethod('manual')
                setError('')
              }}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                connectionMethod === 'manual'
                  ? 'text-pink-600 border-b-2 border-pink-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Manual Entry
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium mb-1">Connection Error</p>
                <p>{error}</p>
                {(error.includes('not configured') || error.includes('OAuth not configured') || error.includes('authenticated') || error.includes('Failed to start')) && (
                  <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                    <p className="font-medium mb-1">💡 Solution:</p>
                    <p className="mb-1">OAuth requires Instagram API credentials (CLIENT_ID & CLIENT_SECRET) to be configured in the backend .env file.</p>
                    <p className="font-medium mt-2 mb-1">✅ Easy Alternative:</p>
                    <p>Switch to the <strong>"Manual Entry"</strong> tab above to enter your Instagram access token directly. This works immediately without any backend configuration!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* OAuth Method */}
          {connectionMethod === 'oauth' && (
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 text-sm text-blue-800">
                    <p className="font-medium mb-1">OAuth Flow (Recommended)</p>
                    <p className="text-blue-700">
                      You'll be redirected to Instagram to authorize VideoHook. This is the secure, official method recommended by Instagram.
                    </p>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={handleOAuth}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Link2 className="w-5 h-5" />
                    Connect with Instagram OAuth
                  </>
                )}
              </button>
            </div>
          )}

          {/* Manual Entry Method */}
          {connectionMethod === 'manual' && (
            <form onSubmit={handleManualSubmit} className="space-y-4">
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 text-sm text-yellow-800">
                    <p className="font-medium mb-1">Manual Entry (Advanced)</p>
                    <p className="text-yellow-700">
                      Enter your Instagram access token directly. You can get this from Instagram's Graph API or Meta for Developers portal.
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instagram Username <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={manualForm.username}
                  onChange={(e) => setManualForm({ ...manualForm, username: e.target.value })}
                  placeholder="your_username"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Token <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={manualForm.access_token}
                  onChange={(e) => setManualForm({ ...manualForm, access_token: e.target.value })}
                  placeholder="Enter your Instagram access token"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Your access token is stored securely in the local database.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Account ID <span className="text-gray-400">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={manualForm.account_id}
                  onChange={(e) => setManualForm({ ...manualForm, account_id: e.target.value })}
                  placeholder="Instagram Business Account ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Only needed for Instagram Business accounts. Usually auto-detected.
                </p>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Connection'
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default InstagramConnectionModal

