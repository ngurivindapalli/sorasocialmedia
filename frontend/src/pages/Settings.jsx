import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Settings as SettingsIcon, Mail, Linkedin, CheckCircle2, ExternalLink, Loader2 } from 'lucide-react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

function Settings() {
  const [searchParams] = useSearchParams()
  const [user, setUser] = useState(null)
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [linkedinStatus, setLinkedinStatus] = useState({ connected: false, companyId: null })
  const [linkedinConnecting, setLinkedinConnecting] = useState(false)
  const [linkedinSuccess, setLinkedinSuccess] = useState(false)

  useEffect(() => {
    loadUserSettings()
    loadLinkedInStatus()
    
    // Check for LinkedIn callback success
    if (searchParams.get('linkedin') === 'connected') {
      setLinkedinSuccess(true)
      setTimeout(() => setLinkedinSuccess(false), 5000)
    }
  }, [searchParams])

  const loadUserSettings = async () => {
    try {
      const userData = await authUtils.getCurrentUserFromAPI()
      if (userData) {
        setUser(userData)
        setEmailNotifications(userData.email_notifications_enabled)
      }
    } catch (err) {
      console.error('Failed to load user settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadLinkedInStatus = async () => {
    try {
      // Check company page configuration
      const companyResponse = await api.get('/api/linkedin/company-info')
      if (companyResponse.data.configured) {
        setLinkedinStatus(prev => ({
          ...prev,
          companyId: companyResponse.data.company_id,
          companyName: companyResponse.data.company_name,
          companyUrl: companyResponse.data.company_url
        }))
      }
      
      // Check for active LinkedIn connections
      const connectionsResponse = await api.get('/api/connections')
      const linkedinConn = connectionsResponse.data?.find(c => c.platform === 'linkedin' && c.is_active)
      if (linkedinConn) {
        setLinkedinStatus(prev => ({
          ...prev,
          connected: true,
          username: linkedinConn.account_username
        }))
      }
    } catch (err) {
      console.error('Failed to load LinkedIn status:', err)
    }
  }

  const handleConnectLinkedIn = async () => {
    try {
      setLinkedinConnecting(true)
      const response = await api.get('/api/linkedin/auth-url')
      if (response.data.auth_url) {
        // Store state for verification
        localStorage.setItem('linkedin_oauth_state', response.data.state)
        // Redirect to LinkedIn OAuth
        window.location.href = response.data.auth_url
      }
    } catch (err) {
      console.error('Failed to get LinkedIn auth URL:', err)
      alert('Failed to initiate LinkedIn connection. Please try again.')
    } finally {
      setLinkedinConnecting(false)
    }
  }

  const handleToggleEmailNotifications = async () => {
    try {
      setSaving(true)
      const newValue = !emailNotifications
      await api.put('/api/user/email-notifications', null, {
        params: { enabled: newValue }
      })
      setEmailNotifications(newValue)
      if (user) {
        setUser({ ...user, email_notifications_enabled: newValue })
      }
    } catch (err) {
      console.error('Failed to update email notifications:', err)
      alert('Failed to update email notification settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading settings...</div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-[#111827] mb-2 flex items-center gap-3">
          <SettingsIcon className="w-8 h-8 text-[#1e293b]" />
          Settings
        </h1>
        <p className="text-[#4b5563]">Manage your account and preferences</p>
      </div>

      <div className="space-y-8">
        {/* Account Information */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-4">Account Information</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-[#4b5563] mb-1">Username</label>
              <p className="text-[#111827]">{user?.username}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-[#4b5563] mb-1">Email</label>
              <p className="text-[#111827]">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* LinkedIn Connection */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <div className="flex items-start gap-3">
            <Linkedin className="w-5 h-5 text-[#0077b5] mt-1" />
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-[#111827]">LinkedIn Integration</h2>
              <p className="text-sm text-[#4b5563] mt-1 mb-4">
                Connect your LinkedIn account to post content directly to the AIGIS company page
              </p>
              
              {/* Success Message */}
              {linkedinSuccess && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  LinkedIn connected successfully!
                </div>
              )}
              
              {/* Company Page Info */}
              {linkedinStatus.companyId && (
                <div className="mb-4 p-4 bg-[#f5f5f5] rounded-lg">
                  <p className="text-sm text-[#4b5563]">Company Page:</p>
                  <div className="flex items-center justify-between mt-1">
                    <p className="font-medium text-[#111827]">
                      {linkedinStatus.companyName || 'AIGIS'}
                    </p>
                    <a 
                      href={linkedinStatus.companyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-[#0077b5] hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View Page
                    </a>
                  </div>
                </div>
              )}
              
              {/* Connection Status */}
              <div className="flex items-center justify-between">
                <div>
                  {linkedinStatus.connected ? (
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle2 className="w-5 h-5" />
                      <span className="font-medium">Connected</span>
                      {linkedinStatus.username && (
                        <span className="text-sm text-[#4b5563]">
                          ({linkedinStatus.username})
                        </span>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-[#6b7280]">Not connected</p>
                  )}
                </div>
                <button
                  onClick={handleConnectLinkedIn}
                  disabled={linkedinConnecting}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                    linkedinStatus.connected 
                      ? 'bg-[#f5f5f5] text-[#4b5563] hover:bg-[#e5e7eb]'
                      : 'bg-[#0077b5] text-white hover:bg-[#005885]'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {linkedinConnecting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Linkedin className="w-4 h-4" />
                      {linkedinStatus.connected ? 'Reconnect' : 'Connect LinkedIn'}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Email Notifications */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-[#1e293b]" />
              <div>
                <h2 className="text-xl font-semibold text-[#111827]">Email Notifications</h2>
                <p className="text-sm text-[#4b5563] mt-1">
                  Receive email notifications when your posts are published to social media
                </p>
              </div>
            </div>
            <button
              onClick={handleToggleEmailNotifications}
              disabled={saving}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                emailNotifications ? 'bg-[#1e293b]' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  emailNotifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
