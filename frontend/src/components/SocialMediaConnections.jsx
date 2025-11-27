import { useState, useEffect } from 'react'
import { Instagram, Linkedin, X as XIcon, Music, Link2, Trash2, CheckCircle2, Loader2, AlertCircle } from 'lucide-react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'
import { useNavigate } from 'react-router-dom'
import InstagramConnectionModal from './InstagramConnectionModal'

const PLATFORMS = [
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: '#E4405F' },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: '#0077B5' },
  { id: 'x', name: 'X (Twitter)', icon: XIcon, color: '#000000' },
  { id: 'tiktok', name: 'TikTok', icon: Music, color: '#000000' },
]

function SocialMediaConnections() {
  const [connections, setConnections] = useState([])
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState(null)
  const [error, setError] = useState('')
  const [showInstagramModal, setShowInstagramModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    console.log('[SocialMediaConnections] Component mounted, loading connections...')
    loadConnections()
  }, [])

  const loadConnections = async () => {
    // No authentication required - load connections directly
    try {
      setLoading(true)
      setError('')
      const response = await api.get('/api/connections')
      console.log('[Connections] Loaded:', response.data)
      setConnections(response.data)
    } catch (err) {
      console.error('[Connections] Load error:', err)
      console.error('[Connections] Error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message
      })
      
      let errorMessage = 'Failed to load connections'
      if (err.response?.status === 403 || err.response?.status === 401) {
        // Backend might still have auth requirement - but we can continue without connections
        console.log('[Connections] Auth error - continuing without connections (auth optional)')
        errorMessage = '' // Don't show error - just show empty connections list
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error loading connections. Please check backend logs.'
      } else if (err.request && !err.response) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running.'
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      
      // Only set error if it's not an auth error (auth is optional now)
      if (errorMessage && !errorMessage.includes('authenticated')) {
        setError(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async (platform) => {
    // No authentication required - OAuth works without login now
    console.log('[OAuth] ===== handleConnect START =====')
    console.log('[OAuth] Platform:', platform)
    console.log('[OAuth] Current state - connecting:', connecting, 'loading:', loading)
    
    // Don't block if already connecting to same platform - allow it
    if (connecting && connecting !== platform) {
      console.log('[OAuth] Already connecting to different platform, ignoring request')
      return
    }
    
    if (loading) {
      console.log('[OAuth] Still loading connections, waiting...')
      // Don't block - just log
    }
    
    try {
      console.log('[OAuth] Setting connecting state to:', platform)
      setConnecting(platform)
      setError('')
      
      const apiUrl = `/api/oauth/${platform}/authorize`
      console.log('[OAuth] Making API request to:', apiUrl)
      console.log('[OAuth] API base URL:', api.defaults.baseURL || '(using proxy)')
      
      // Get authorization URL
      const response = await api.get(apiUrl)
      
      console.log('[OAuth] Response received!')
      console.log('[OAuth] Status:', response.status)
      console.log('[OAuth] Data:', response.data)
      
      if (!response.data?.authorization_url) {
        throw new Error('No authorization_url in response. Response: ' + JSON.stringify(response.data))
      }
      
      const authUrl = response.data.authorization_url
      console.log('[OAuth] Got authorization URL:', authUrl)
      console.log('[OAuth] About to redirect...')
      
      // Small delay to ensure state updates are visible
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Redirect to OAuth URL
      console.log('[OAuth] Redirecting now!')
      window.location.href = authUrl
    } catch (err) {
      console.error('[OAuth] ===== ERROR OCCURRED =====')
      console.error('[OAuth] Error object:', err)
      console.error('[OAuth] Error message:', err.message)
      console.error('[OAuth] Error stack:', err.stack)
      
      const errorDetails = {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText,
        request: err.request ? 'Request made but no response' : 'No request made',
        config: {
          url: err.config?.url,
          method: err.config?.method,
          baseURL: err.config?.baseURL
        }
      }
      console.error('[OAuth] Error details:', errorDetails)
      
      let errorMessage = `Failed to connect ${platform}`
      
      if (err.response?.status === 401 || err.response?.status === 403) {
        errorMessage = 'Authentication error. OAuth should work without login - please check backend configuration.'
      } else if (err.response?.status === 400) {
        errorMessage = err.response?.data?.detail || errorMessage
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please check if OAuth credentials are configured in backend .env file.'
      } else if (err.request && !err.response) {
        errorMessage = 'Unable to connect to server. Please check if the backend is running on http://localhost:8000'
      } else if (err.message) {
        errorMessage = err.message
      } else {
        errorMessage = err.response?.data?.detail || errorMessage
      }
      
      console.log('[OAuth] Setting error message:', errorMessage)
      setError(errorMessage)
      setConnecting(null)
      console.log('[OAuth] ===== handleConnect END (ERROR) =====')
    }
  }

  const handleDisconnect = async (connectionId) => {
    if (!confirm('Are you sure you want to disconnect this account?')) {
      return
    }

    try {
      await api.delete(`/api/connections/${connectionId}`)
      setConnections(connections.filter(c => c.id !== connectionId))
    } catch (err) {
      setError('Failed to disconnect account')
      console.error(err)
    }
  }

  const getConnectionForPlatform = (platform) => {
    return connections.find(c => c.platform === platform)
  }

  const handleInstagramConnect = (e) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('[SocialMedia] Opening Instagram connection modal')
    setShowInstagramModal(true)
  }

  const handleConnectionSuccess = (newConnection) => {
    console.log('[SocialMedia] Connection successful:', newConnection)
    // Reload connections to show the new one
    loadConnections()
    setShowInstagramModal(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Social Media Connections</h2>
        <p className="text-gray-600">Connect your social media accounts to post videos directly from VideoHook</p>
      </div>

      {error && !error.includes('authenticated') && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p>{error}</p>
            {error.includes('OAuth credentials') && (
              <p className="mt-2 text-xs text-gray-600">
                To connect Instagram, you need to set up OAuth credentials in your backend .env file:
                <br />INSTAGRAM_CLIENT_ID=your_client_id
                <br />INSTAGRAM_CLIENT_SECRET=your_client_secret
              </p>
            )}
            {error.includes('unable to connect') && (
              <p className="mt-2 text-xs text-gray-600">
                Make sure the backend server is running on http://localhost:8000
              </p>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {PLATFORMS.map((platform) => {
          const Icon = platform.icon
          const connection = getConnectionForPlatform(platform.id)
          const isConnecting = connecting === platform.id

          return (
            <div
              key={platform.id}
              className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {platform.id === 'x' ? (
                    <span className="w-8 h-8 flex items-center justify-center font-bold text-xl" style={{ fontFamily: 'system-ui' }}>𝕏</span>
                  ) : (
                    <Icon className="w-8 h-8" style={{ color: platform.color }} />
                  )}
                  <div>
                    <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                    {connection && (
                      <p className="text-sm text-gray-500">@{connection.account_username}</p>
                    )}
                  </div>
                </div>
                {connection && (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                )}
              </div>

              {connection ? (
                <div className="space-y-2">
                  <div className="text-sm text-gray-600">
                    <p>Connected: {new Date(connection.connected_at).toLocaleDateString()}</p>
                    {connection.last_used_at && (
                      <p>Last used: {new Date(connection.last_used_at).toLocaleDateString()}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDisconnect(connection.id)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Disconnect
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    if (platform.id === 'instagram') {
                      // Show modal for Instagram
                      handleInstagramConnect(e)
                    } else {
                      // Use OAuth for other platforms
                      console.log('[SocialMedia] ===== BUTTON CLICKED =====')
                      console.log('[SocialMedia] Platform:', platform.id)
                      console.log('[SocialMedia] isConnecting:', isConnecting, 'loading:', loading)
                      console.log('[SocialMedia] Button disabled?:', isConnecting || loading)
                      console.log('[SocialMedia] Calling handleConnect...')
                      try {
                        handleConnect(platform.id)
                      } catch (err) {
                        console.error('[SocialMedia] Error in onClick handler:', err)
                        setError('An error occurred: ' + err.message)
                      }
                    }
                  }}
                  disabled={isConnecting || loading}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 active:opacity-75"
                  style={{ 
                    backgroundColor: platform.color,
                    cursor: (isConnecting || loading) ? 'not-allowed' : 'pointer',
                    pointerEvents: (isConnecting || loading) ? 'none' : 'auto'
                  }}
                  aria-label={`Connect ${platform.name}`}
                  title={isConnecting ? 'Connecting...' : loading ? 'Loading...' : `Connect ${platform.name}`}
                >
                  {isConnecting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Link2 className="w-4 h-4" />
                      Connect {platform.name}
                    </>
                  )}
                </button>
              )}
            </div>
          )
        })}
      </div>

      {/* Instagram Connection Modal */}
      <InstagramConnectionModal
        isOpen={showInstagramModal}
        onClose={() => setShowInstagramModal(false)}
        onSuccess={handleConnectionSuccess}
      />
    </div>
  )
}

export default SocialMediaConnections


